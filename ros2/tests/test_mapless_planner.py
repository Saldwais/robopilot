import math, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from robopilot_drive.mapless_planner import MaplessPlanner

class PlannerTests(unittest.TestCase):
 def setUp(self): self.p=MaplessPlanner()
 def test_drives_toward_clear_goal(self):
  cmd=self.p.plan(2,0,[5.0]*181,-math.pi,math.pi/90)
  self.assertEqual(cmd.state,'driving'); self.assertGreater(cmd.linear_x,0); self.assertAlmostEqual(cmd.angular_z,0,places=2)
 def test_stops_when_all_beams_blocked(self):
  cmd=self.p.plan(2,0,[0.2]*181,-math.pi,math.pi/90)
  self.assertEqual(cmd.state,'blocked'); self.assertEqual(cmd.linear_x,0)
 def test_routes_around_blocked_goal_heading(self):
  ranges=[5.0]*181; ranges[90]=0.2
  cmd=self.p.plan(2,0,ranges,-math.pi,math.pi/90)
  self.assertEqual(cmd.state,'avoiding_obstacle'); self.assertGreater(cmd.linear_x,0); self.assertNotEqual(cmd.angular_z,0)
 def test_goal_reached(self):
  cmd=self.p.plan(.1,.1,[5.0]*10,-1,.2)
  self.assertEqual(cmd.state,'goal_reached'); self.assertEqual(cmd.linear_x,0)
 def test_invalid_goal_stops(self):
  cmd=self.p.plan(float('nan'),0,[3.0],0,.1)
  self.assertEqual(cmd.state,'invalid_input'); self.assertEqual(cmd.linear_x,0)
if __name__=='__main__': unittest.main()
