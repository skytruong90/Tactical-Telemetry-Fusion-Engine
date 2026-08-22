import unittest
from telemetry_fusion import source_samples,nearest,fuse
class Tests(unittest.TestCase):
    def test_source_count(self): self.assertEqual(len(source_samples(1,2,'nav')),3)
    def test_nearest(self): self.assertEqual(nearest([(0,1),(1,2)],.9,.2),(1,2))
    def test_health_range(self): self.assertTrue(all(0<=r['health_score']<=100 for r in fuse(2)))
if __name__=='__main__': unittest.main()
