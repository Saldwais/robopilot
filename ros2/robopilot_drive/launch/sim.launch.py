from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,ExecuteProcess
from launch.substitutions import LaunchConfiguration,Command,PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
 drive=LaunchConfiguration('drive_type')
 pkg=FindPackageShare('robopilot_drive')
 xacro=PathJoinSubstitution([pkg,'urdf','robot.urdf.xacro'])
 world=PathJoinSubstitution([pkg,'worlds','robopilot_test.sdf'])
 robot_description={'robot_description':Command(['xacro ',xacro,' drive_type:=',drive])}
 bridge_args=['/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist','/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry','/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan','/camera/image@sensor_msgs/msg/Image[gz.msgs.Image']
 return LaunchDescription([
  DeclareLaunchArgument('drive_type',default_value='differential_2wd',description='differential_2wd or skid_4wd'),
  ExecuteProcess(cmd=['gz','sim','-r',world],output='screen'),
  Node(package='robot_state_publisher',executable='robot_state_publisher',parameters=[robot_description]),
  Node(package='ros_gz_sim',executable='create',arguments=['-name','robopilot','-topic','robot_description','-x','0','-y','0','-z','0.25'],output='screen'),
  Node(package='ros_gz_bridge',executable='parameter_bridge',arguments=bridge_args,output='screen'),
  Node(package='robopilot_drive',executable='drive_node',parameters=[robot_description,{'hardware_enabled':False,'drive_type':drive}]),
  Node(package='robopilot_drive',executable='camera_perception_node',parameters=[{'targets':'road,tree,person,dog,stairs'}]),
  Node(package='robopilot_drive',executable='mapless_nav_node'),
  Node(package='rviz2',executable='rviz2',arguments=['-d',PathJoinSubstitution([pkg,'rviz','robot_and_lidar.rviz'])],output='screen')
 ])
