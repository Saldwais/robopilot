from setuptools import setup
from glob import glob
import os

setup(name='robopilot_drive',version='0.2.0',packages=['robopilot_drive'],
 data_files=[('share/ament_index/resource_index/packages',['resource/robopilot_drive']),
 ('share/robopilot_drive',['package.xml']),
 (os.path.join('share','robopilot_drive','config'),glob('config/*.yaml')),
 (os.path.join('share','robopilot_drive','worlds'),glob('worlds/*.sdf')),
 (os.path.join('share','robopilot_drive','launch'),glob('robopilot_drive/launch/*.py')),
 (os.path.join('share','robopilot_drive','urdf'),glob('robopilot_drive/*.xacro')),
 (os.path.join('share','robopilot_drive','rviz'),glob('robopilot_drive/*.rviz'))],
 install_requires=['setuptools'],zip_safe=True,
 entry_points={'console_scripts':['drive_node=robopilot_drive.drive_node:main','camera_perception_node=robopilot_drive.camera_perception_node:main','mapless_nav_node=robopilot_drive.mapless_nav_node:main','aws_telemetry_node=robopilot_drive.aws_telemetry_node:main']})
