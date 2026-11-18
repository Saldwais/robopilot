"""ROS 2 Twist-to-wheel target node. Does not connect to physical motors."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
from drive_model import DriveConfig, wheel_targets

class DriveNode(Node):
    def __init__(self):
        super().__init__('robopilot_drive')
        self.declare_parameter('drive_type', 'differential_2wd')
        self.declare_parameter('wheel_radius_m', 0.05)
        self.declare_parameter('track_width_m', 0.25)
        self.declare_parameter('max_wheel_rad_s', 4.0)
        self.declare_parameter('motor_ids', [9, 10])
        self.declare_parameter('motor_signs', [-1, 1])
        self.declare_parameter('command_timeout_s', 0.35)
        self.declare_parameter('hardware_enabled', False)
        self.config = DriveConfig(
            self.get_parameter('drive_type').value,
            self.get_parameter('wheel_radius_m').value,
            self.get_parameter('track_width_m').value,
            self.get_parameter('max_wheel_rad_s').value,
            tuple(self.get_parameter('motor_ids').value),
            tuple(self.get_parameter('motor_signs').value))
        self.config.validate()
        self.timeout = float(self.get_parameter('command_timeout_s').value)
        self.hardware_enabled = bool(self.get_parameter('hardware_enabled').value)
        self.last_cmd = None
        self.sub = self.create_subscription(Twist, '/cmd_vel', self.on_cmd, 10)
        self.pub = self.create_publisher(Float64MultiArray, '/wheel_targets', 10)
        self.timer = self.create_timer(0.05, self.tick)
        self.get_logger().warning('Hardware output disabled. This node only publishes wheel targets.')

    def on_cmd(self, msg):
        self.last_cmd = (self.get_clock().now(), float(msg.linear.x), float(msg.angular.z))

    def tick(self):
        output = Float64MultiArray()
        if self.last_cmd is not None:
            stamp, linear, angular = self.last_cmd
            age = (self.get_clock().now() - stamp).nanoseconds / 1e9
            if age <= self.timeout:
                output.data = list(wheel_targets(linear, angular, self.config))
        self.pub.publish(output)

def main(args=None):
    rclpy.init(args=args)
    node = DriveNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
