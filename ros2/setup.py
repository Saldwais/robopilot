from setuptools import setup
setup(name='robopilot_drive', version='0.1.0', packages=['robopilot_drive'],
      data_files=[('share/ament_index/resource_index/packages',['resource/robopilot_drive']),
                  ('share/robopilot_drive',['package.xml']),
                  ('share/robopilot_drive/config',['config/drive.yaml'])],
      install_requires=['setuptools'], zip_safe=True,
      entry_points={'console_scripts':['drive_node=robopilot_drive.drive_node:main']})
