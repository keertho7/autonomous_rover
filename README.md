# my_rover

A ROS 2 simulation stack for a two-wheeled differential-drive rover. The rover runs in Gazebo with a 2D lidar, builds a map of its environment with `slam_toolbox`, and then navigates that map autonomously using Nav2.

Everything runs in simulation — no hardware required.

## What's in here

| Package | Build type | Contents |
|---|---|---|
| `my_rover_description` | `ament_cmake` | Robot URDF, Gazebo SDF model, and the test world |
| `my_rover_bringup` | `ament_python` | Launch files, bridge/SLAM/Nav2 configs, saved maps |

## The rover

| Property | Value |
|---|---|
| Drive | Differential (`gz-sim-diff-drive-system`) |
| Wheel radius | 0.06 m |
| Wheel separation | 0.31 m |
| Lidar | GPU lidar, 360 samples, 10 Hz, 0.2–10.0 m range |
| Lidar mount | 0.08 m above `base_link` |
| Frames | `map` → `odom` → `base_link` → `lidar_link` |

The world (`rover_world.sdf`) is a small walled arena with four box obstacles and a ground plane.

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy Jalisco
- Gazebo Harmonic (`gz sim`)
- `ros_gz_sim` and `ros_gz_bridge`
- `slam_toolbox`
- `nav2_bringup`
- `robot_state_publisher`, `rviz2`

```bash
sudo apt install ros-jazzy-ros-gz \
                 ros-jazzy-slam-toolbox \
                 ros-jazzy-navigation2 \
                 ros-jazzy-nav2-bringup
```

> Ubuntu 24.04 + Gazebo Harmonic is the combination ROS 2 Jazzy is built and tested against, so `ros-jazzy-ros-gz` will pull in Harmonic automatically — no separate Gazebo install needed.

## Build

```bash
mkdir -p ~/rover_ws/src
cd ~/rover_ws/src
git clone https://github.com/<your-username>/<your-repo>.git .

cd ~/rover_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

## Usage

### 1. Build a map (SLAM)

```bash
ros2 launch my_rover_bringup simulation.launch.py
```

This brings up Gazebo, spawns the rover, starts the ROS–Gazebo bridge and `robot_state_publisher`, launches `slam_toolbox` in mapping mode, and opens RViz.

Drive the rover around to fill in the map:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Once the map looks complete, save it:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/rover_ws/src/my_rover_bringup/maps/rover_world_map
```

### 2. Navigate autonomously (Nav2)

In one terminal, start the simulation world:

```bash
ros2 launch my_rover_bringup world.launch.py
```

In another, start Nav2 against the saved map:

```bash
ros2 launch my_rover_bringup navigation.launch.py
```

Then use **2D Pose Estimate** in RViz to seed AMCL, and **Nav2 Goal** to send the rover somewhere.

Optional arguments:

```bash
ros2 launch my_rover_bringup navigation.launch.py \
  map:=/path/to/your_map.yaml \
  params_file:=/path/to/nav2_params.yaml \
  use_sim_time:=true
```

## Launch files

| File | What it does |
|---|---|
| `world.launch.py` | Starts Gazebo with `rover_world.sdf` and spawns the rover after a 3 s delay |
| `bringup.launch.py` | `robot_state_publisher` + the `ros_gz_bridge` parameter bridge |
| `simulation.launch.py` | Full mapping session: world + bringup + `slam_toolbox` + RViz |
| `navigation.launch.py` | Bringup + Nav2 stack (AMCL, costmaps, planner, controller) + Nav2 RViz view |

## Topics

Bridged between Gazebo and ROS 2 via `config/bridge.yaml`:

| Topic | Type | Direction |
|---|---|---|
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo → ROS |
| `/scan` | `sensor_msgs/msg/LaserScan` | Gazebo → ROS |
| `/odom` | `nav_msgs/msg/Odometry` | Gazebo → ROS |
| `/tf` | `tf2_msgs/msg/TFMessage` | Gazebo → ROS |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | ROS → Gazebo |

All nodes run with `use_sim_time: true`.

## Configuration

**`config/slam.yaml`** — `slam_toolbox` in async mapping mode. Map resolution 0.025 m, laser range clamped to 0.2–4.5 m for rastering, loop closure enabled, Ceres solver.

**`config/nav2_params.yaml`** — AMCL with an initial pose at the origin and laser range limited to 0.1–3.5 m to suppress self-reflections and max-range ghost arcs. DWB local planner capped at 0.5 m/s linear and 1.0 rad/s angular. Costmap inflation radius 0.55 m.

**`maps/rover_world_map.yaml`** — 231 × 233 px at 0.025 m/px, origin `[-2.853, -2.900, 0]`.

## Repository layout

```
src/
├── my_rover_bringup/
│   ├── config/          # bridge.yaml, slam.yaml, nav2_params.yaml
│   ├── launch/          # world, bringup, simulation, navigation
│   ├── maps/            # rover_world_map.pgm + .yaml
│   └── my_rover_bringup/
│       └── ground_truth_tf.py
└── my_rover_description/
    ├── urdf/            # my_rover.urdf (kinematic tree for TF)
    ├── models/          # model.sdf (physics, lidar, diff-drive plugin)
    └── worlds/          # rover_world.sdf
```

## Notes and known issues

- `ground_truth_tf.py` publishes a ground-truth `odom` → `base_link` transform from Gazebo's pose publisher. It is **not** registered in `setup.py`'s `console_scripts`, so it can't be run with `ros2 run` yet — add an entry point if you want to use it. It also depends on the `gz-sim-pose-publisher-system` plugin, which is currently commented out in `model.sdf`.
- The SLAM block in `bringup.launch.py` is commented out; SLAM is launched from `simulation.launch.py` instead.
- `package.xml` and `setup.py` still carry `TODO` placeholders for description and license in both packages.
- The repo contains backup/editor artifacts (`src/my_rover/model_backup.sdf`, `model_jul6_bck.sdf`, `launch/simulation.launch.py~`). Consider removing them and adding a `.gitignore`.
