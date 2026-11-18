# RoboPilot ROS 2 + AWS Simulation Extension

Adds configurable 2-wheel differential and 4-wheel skid-steer kinematics to RoboPilot. This package is a simulation-ready integration scaffold; physical motor wiring and XLeRobot/RO-101 hardware support must be validated on the actual robot before driving.

## Safety and scope

- Default is simulation mode; hardware publishing is disabled unless explicitly enabled.
- 2WD order: left, right. 4WD order: front-left, rear-left, front-right, rear-right.
- Set motor IDs and direction signs from your actual chassis. Do not copy IDs between chassis.
- All wheel rates are bounded and `/cmd_vel` expires after 0.35 s without a fresh command.
- AWS bridge is telemetry-only by default. Remote motion commands are intentionally not enabled in this first integration.
- No AWS credentials, certificates, private keys, or robot identifiers belong in Git.
- No real-robot test has been run by this package. Start with wheels raised, low limits, emergency stop reachable, and a spotter.

## Drive profiles

Edit `config/drive.yaml` and choose `differential_2wd` or `skid_4wd`. Four-wheel profile drives each left wheel as one side and each right wheel as the other. For 4WD, set four unique motor IDs and signs. Measure wheel radius and track width.

## ROS 2

Target: ROS 2 Jazzy on Ubuntu 24.04 with Gazebo Harmonic. A ROS-independent kinematics module and tests are included so basic drive math can be checked without ROS installed.

```bash
python3 -m unittest discover -s tests -v
```

The ROS node translates `geometry_msgs/Twist` on `/cmd_vel` to bounded `/wheel_targets` (`std_msgs/Float64MultiArray`). It does not yet command your serial motors. A robot-specific `ros2_control` hardware plugin or tested serial bridge must be added after the exact wheel controller, motor IDs, and firmware are confirmed.

## 3D environment

`worlds/robopilot_test.sdf` provides a simple indoor floor, lane markings, obstacles, and lighting for visualization and navigation experiments. The current model is an environment, not a validated digital twin; adjust its dimensions to match the real robot and carpet.

## AWS

`aws/telemetry_contract.json` documents a non-sensitive telemetry schema for AWS IoT Core ingestion. This scaffold does not connect to AWS until a certificate-backed bridge is configured. Store certificates outside the repository and use an AWS IoT policy restricted to the robot's specific telemetry topic. Remote motion is not supported.

## Validation boundary

Unit tests validate wheel kinematics only. ROS 2 launch, Gazebo, AWS connectivity, camera perception, and real hardware need to be tested in their respective environments. This repository makes no claim that the robot has successfully driven in simulation or outdoors.
