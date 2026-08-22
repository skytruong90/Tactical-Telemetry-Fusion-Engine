from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path

def source_samples(duration,rate,name):
    rows=[]
    for i in range(int(duration*rate)+1):
        t=i/rate
        if name=='air': value=120+8*math.sin(t/4)
        elif name=='nav': value=0.98-.03*(1+math.sin(t/5))/2
        else: value=65+5*math.sin(t/7)
        rows.append((t,value))
    return rows

def nearest(rows,t,max_age=.25):
    sample=min(rows,key=lambda r:abs(r[0]-t)); return sample if abs(sample[0]-t)<=max_age else None

def fuse(duration=20,rate=10):
    streams={n:source_samples(duration,r,n) for n,r in [('air',5),('nav',2),('thermal',1)]}; out=[]
    for i in range(int(duration*rate)+1):
        t=i/rate; values={}; stale=[]
        for name,rows in streams.items():
            s=nearest(rows,t,.55 if name=='thermal' else .3)
            if s is None: stale.append(name); values[name]=None
            else: values[name]=s[1]
        health=100-20*len(stale)
        if values['nav'] is not None: health-=max(0,(.97-values['nav'])*200)
        if values['thermal'] is not None: health-=max(0,values['thermal']-68)*1.5
        out.append({'t_s':t,**values,'stale_count':len(stale),'health_score':round(max(0,min(100,health)),2)})
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('--duration',type=float,default=20); p.add_argument('--output',type=Path,default=Path('artifacts')); a=p.parse_args(); rows=fuse(a.duration); a.output.mkdir(parents=True,exist_ok=True)
    with (a.output/'fused_telemetry.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    report={'samples':len(rows),'min_health_score':min(r['health_score'] for r in rows),'stale_records':sum(r['stale_count']>0 for r in rows)}; (a.output/'summary.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
if __name__=='__main__': main()
