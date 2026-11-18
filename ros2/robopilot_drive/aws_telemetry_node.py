"""Opt-in AWS IoT Core telemetry from ROS 2; never accepts control commands."""
import json,os,ssl,time
from datetime import datetime,timezone
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
class AwsTelemetryNode(Node):
 def __init__(self):
  super().__init__('robopilot_aws_telemetry')
  self.declare_parameter('publish_period_s',2.0);self.declare_parameter('drive_type','differential_2wd');self.declare_parameter('mode','sim')
  self.odom=None;self.scan=None;self.nav_state='unknown';self.last_rx=time.monotonic()
  import paho.mqtt.client as mqtt
  endpoint=os.environ['AWS_IOT_ENDPOINT'];self.device=os.environ['ROBOT_DEVICE_ID'];ca=os.environ['AWS_CA_FILE'];cert=os.environ['AWS_CERT_FILE'];key=os.environ['AWS_PRIVATE_KEY_FILE']
  self.topic=f'robopilot/{self.device}/telemetry';self.client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id=self.device,protocol=mqtt.MQTTv311)
  self.client.tls_set(ca_certs=ca,certfile=cert,keyfile=key,tls_version=ssl.PROTOCOL_TLS_CLIENT);self.client.connect(endpoint,8883,30);self.client.loop_start()
  self.create_subscription(Odometry,'/odom',self.on_odom,10);self.create_subscription(LaserScan,'/scan',self.on_scan,10);self.create_subscription(String,'/navigation/state',self.on_nav,10)
  self.timer=self.create_timer(float(self.get_parameter('publish_period_s').value),self.publish)
 def on_odom(self,m):self.odom=m
 def on_scan(self,m):self.scan=m;self.last_rx=time.monotonic()
 def on_nav(self,m):self.nav_state=m.data
 def publish(self):
  if self.odom is None:return
  p=self.odom.pose.pose.position;q=self.odom.pose.pose.orientation
  valid=[float(r) for r in (self.scan.ranges if self.scan else []) if r>0 and r<float('inf')]
  payload={'schema_version':'1.0','device_id':self.device,'timestamp':datetime.now(timezone.utc).isoformat(),'drive_type':self.get_parameter('drive_type').value,'mode':self.get_parameter('mode').value,'odom':{'x_m':p.x,'y_m':p.y,'yaw_qz':q.z,'yaw_qw':q.w},'lidar_min_range_m':min(valid) if valid else None,'navigation_state':self.nav_state,'scan_age_ms':round((time.monotonic()-self.last_rx)*1000)}
  self.client.publish(self.topic,json.dumps(payload),qos=1,retain=False)
 def destroy_node(self):
  if hasattr(self,'client'):self.client.loop_stop();self.client.disconnect()
  super().destroy_node()
def main(args=None):
 rclpy.init(args=args);n=AwsTelemetryNode()
 try:rclpy.spin(n)
 finally:n.destroy_node();rclpy.shutdown()
if __name__=='__main__':main()
