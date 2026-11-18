"""Detect requested scene labels in compressed camera frames and publish overlays."""
import json
from base64 import b64decode
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from .camera_vision import CameraVision

class CameraPerceptionNode(Node):
 def __init__(self):
  super().__init__('robopilot_camera_perception')
  self.declare_parameter('targets','road,tree,person,dog,stairs')
  self.declare_parameter('image_topic','/camera/image')
  self.vision=CameraVision(); self.pub=self.create_publisher(String,'/perception/detections',10); self.overlay=self.create_publisher(Image,'/perception/annotated',2)
  self.sub=self.create_subscription(Image,self.get_parameter('image_topic').value,self.on_image,5)
  self.get_logger().warning('Object detection is a fallible visual aid; it is not a person/pet safety system. LiDAR and physical e-stop remain independent.')
 def on_image(self,msg):
  try:
   import cv2, numpy as np
   channels=1 if msg.encoding in ('mono8','8UC1') else 3
   frame=np.frombuffer(msg.data,dtype=np.uint8).reshape(msg.height,msg.width,channels)
   if msg.encoding=='rgb8': frame=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
   ok,encoded=cv2.imencode('.jpg',frame)
   if not ok: return
   result=self.vision.analyze(encoded.tobytes(),self.get_parameter('targets').value)
   if result is None:return
   out=String(); out.data=json.dumps({'stamp_sec':msg.header.stamp.sec,'stamp_nanosec':msg.header.stamp.nanosec,'frame_id':msg.header.frame_id,'boxes':result['boxes'],'counts':result['counts']}); self.pub.publish(out)
   if result['annotated_jpeg']:
    annotated=cv2.imdecode(np.frombuffer(b64decode(result['annotated_jpeg']),np.uint8),cv2.IMREAD_COLOR)
    if annotated is not None:
     rgb=cv2.cvtColor(annotated,cv2.COLOR_BGR2RGB); img=Image(); img.header=msg.header; img.height=rgb.shape[0]; img.width=rgb.shape[1]; img.encoding='rgb8'; img.step=rgb.shape[1]*3; img.data=rgb.tobytes(); self.overlay.publish(img)
  except Exception as e:self.get_logger().error(f'Camera perception error: {e}')
def main(args=None):
 rclpy.init(args=args); n=CameraPerceptionNode()
 try:rclpy.spin(n)
 finally:n.destroy_node();rclpy.shutdown()
if __name__=='__main__':main()
