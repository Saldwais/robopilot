import sys, unittest, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
class ModelTests(unittest.TestCase):
 def test_world_and_xacro_parse(self):
  ET.parse(ROOT/'worlds/robopilot_test.sdf'); ET.parse(ROOT/'robopilot_drive/robot.urdf.xacro')
 def test_model_has_lidar_and_camera_topics(self):
  x=(ROOT/'robopilot_drive/robot.urdf.xacro').read_text()
  for token in ('gpu_lidar','/scan','front_camera','/camera/image','left_rear_joint','right_rear_joint'):
   self.assertIn(token,x)
 def test_rviz_displays_lidar_and_annotated_camera(self):
  c=(ROOT/'robopilot_drive/rviz_robot_and_lidar.rviz').read_text()
  self.assertIn('/scan',c);self.assertIn('/perception/annotated',c);self.assertIn('Robot Exterior Model',c)
 def test_perception_labels_are_available_by_default(self):
  n=(ROOT/'robopilot_drive/camera_perception_node.py').read_text()
  for label in ('road,tree,person,dog,stairs','/perception/detections','/perception/annotated'):
   self.assertIn(label,n)
if __name__=='__main__':unittest.main()
