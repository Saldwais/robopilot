"""Reactive LiDAR point-to-point navigation. No global map; e-stop and scan timeout stop motion."""
import math,time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist,PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool,String
from .mapless_planner import MaplessPlanner

def yaw_from_q(q): return math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
class MaplessNavNode(Node):
 def __init__(self):
  super().__init__('robopilot_mapless_nav')
  self.declare_parameter('scan_timeout_s',.5);self.declare_parameter('stop_distance_m',.55);self.declare_parameter('max_linear_mps',.18);self.declare_parameter('max_angular_rps',.65)
  self.planner=MaplessPlanner(stop_distance=self.get_parameter('stop_distance_m').value,max_linear=self.get_parameter('max_linear_mps').value,max_angular=self.get_parameter('max_angular_rps').value)
  self.scan=None;self.scan_t=0;self.odom=None;self.goal=None;self.estop=True
  self.cmd=self.create_publisher(Twist,'/cmd_vel',10);self.state=self.create_publisher(String,'/navigation/state',10)
  self.create_subscription(LaserScan,'/scan',self.on_scan,10);self.create_subscription(Odometry,'/odom',self.on_odom,10);self.create_subscription(PoseStamped,'/goal',self.on_goal,10);self.create_subscription(Bool,'/estop',self.on_estop,10);self.timer=self.create_timer(.1,self.tick)
  self.get_logger().warning('Reactive mapless demo only. Enable with /estop false after hardware e-stop and supervised checks.')
 def on_scan(self,m):self.scan=m;self.scan_t=time.monotonic()
 def on_odom(self,m):self.odom=m
 def on_goal(self,m):self.goal=(m.pose.position.x,m.pose.position.y)
 def on_estop(self,m):self.estop=bool(m.data)
 def halt(self,status):
  self.cmd.publish(Twist()); s=String();s.data=status;self.state.publish(s)
 def tick(self):
  if self.estop:self.halt('estop');return
  if self.scan is None or time.monotonic()-self.scan_t>float(self.get_parameter('scan_timeout_s').value):self.halt('scan_stale');return
  if self.odom is None or self.goal is None:self.halt('waiting_for_odom_or_goal');return
  p=self.odom.pose.pose.position;yaw=yaw_from_q(self.odom.pose.pose.orientation);dx=self.goal[0]-p.x;dy=self.goal[1]-p.y
  c,s=math.cos(yaw),math.sin(yaw);gx=c*dx+s*dy;gy=-s*dx+c*dy
  plan=self.planner.plan(gx,gy,self.scan.ranges,self.scan.angle_min,self.scan.angle_increment,self.scan.range_max)
  msg=Twist();msg.linear.x=plan.linear_x;msg.angular.z=plan.angular_z;self.cmd.publish(msg)
  st=String();st.data=plan.state;self.state.publish(st)
def main(args=None):
 rclpy.init(args=args);n=MaplessNavNode()
 try:rclpy.spin(n)
 finally:n.halt('shutdown');n.destroy_node();rclpy.shutdown()
if __name__=='__main__':main()
