# *** ROS-Packages zur Inbetriebnahme des OpenManipulators ***

## 1) ** Beschreibung **

XXX

## 2) ** Allgemeine Hinweise **

Remote-PC:
- ROS-Version: ROS Noetic
- Ubuntu-Version: Ubuntu 20.04

## 3) ** Installation Remote-PC **

**3.1) Update the public key used for ROS apt repositories: <br/>**
```
$ scurl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
```

**3.2) Install libignition-rendering3: <br/>**
```
$ sudo apt install libignition-rendering3
```

**3.3) Install dependent pacakges: <br/>**
```
$ source ~/.bashrc
$ sudo apt-get install ros-noetic-ros-controllers ros-noetic-gazebo* ros-noetic-moveit* ros-noetic-industrial-core
$ sudo apt install ros-noetic-dynamixel-sdk ros-noetic-dynamixel-workbench*
$ sudo apt install ros-noetic-robotis-manipulator
```

**3.4) Download and build OpenMANIPULATOR-X packages: <br/>**
```
$ cd ~/catkin_ws/src/
$ git clone -b noetic-devel https://github.com/ROBOTIS-GIT/open_manipulator.git
$ git clone -b noetic-devel https://github.com/ROBOTIS-GIT/open_manipulator_msgs.git
$ git clone -b noetic-devel https://github.com/ROBOTIS-GIT/open_manipulator_simulations.git
$ git clone https://github.com/ROBOTIS-GIT/open_manipulator_dependencies.git
$ cd ~/catkin_ws && catkin_make
```

**3.5) Download and build ROS-Service Clients to operate OpenMANIPULATOR-X : <br/>**
```
$ cd ~/catkin_ws/src/
$ git clone https://github.com/ChrisDillmann/my_om_controller.git
$ cd ~/catkin_ws && catkin_make
```
Note: Set executable permissions:
```
$ roscd my_om_controller
$ cd scripts
$ sudo chmod a+x scirptname.py
```

## 4) ** Quick-Start **

***5.1) Load a OpenManipulator-X model on Gazebo and RViz:<br/>***

**5.1.1) Load OpenManipulator-X on Gazebo simulator and click on Play ▶ button at the bottom of the Gazebo window:<br/>**
```
$ roslaunch my_om_controller my_om_gazebo_rviz.launch
```
Note: The OpenManipulator-X model is also loaded in RViz.

To load the OpenManipulator-X exclusively in RViz run the following terminal command instead:
```
$ roslaunch my_om_controller my_om_rviz.launch
```
To load the OpenManipulator-X exclusively in Gazebo run the following terminal command instead:
```
$ roslaunch my_om_controller my_om_gazebo.launch
```

**5.1.2) Start ROS-Service Client Node to operate OpenMANIPULATOR-X <br/>**
```
$ rosrun my_om_controller my_om_service_client_pick_and_place.py
```
**5.1.3) Publish pose message:<br/>**
```
$ rostopic pub -1 /sweet_pose geometry_msgs/Pose  '{position:  {x: 0.21, y: -0.06, z: 0.04}, orientation: {x: 0.10,y: 0.64,z: -0.11,w: 0.76}}'
$ rostopic pub -1 /sweet_pose geometry_msgs/Pose  '{position:  {x: 0.126, y: 0.042, z: 0.03}, orientation: {x: -0.12,y: 0.65,z: 0.13,w: 0.74}}'
$ rostopic pub -1 /sweet_pose geometry_msgs/Pose  '{position:  {x: 0.17, y: -0.07, z: 0.04}, orientation: {x: 0.13,y: 0.62,z: -0.15,w: 0.75}}'
```

***5.2) Operate with "real" OpenMANIPULATOR-X:<br/>***

**5.2.1) Launch controller:<br/>**
```
roslaunch open_manipulator_controller open_manipulator_controller.launch usb_port:=/dev/ttyACM0 baud_rate:=1000000
```
**5.2.2) Start ROS-Service Client Node to operate OpenMANIPULATOR-X: <br/>**
```
$ rosrun my_om_controller my_om_service_client_pick_and_place.py
```
**5.2.3) Optional: Load the OpenManipulator-X in RViz: <br/>**
```
$ roslaunch my_om_controller my_om_rviz.launch
```
**5.2.4) Publish pose message: <br/>**
```
$ rostopic pub -1 /sweet_pose geometry_msgs/Pose  '{position:  {x: 0.21, y: -0.06, z: 0.04}, orientation: {x: 0.10,y: 0.64,z: -0.11,w: 0.76}}'
$ rostopic pub -1 /sweet_pose geometry_msgs/Pose  '{position:  {x: 0.126, y: 0.042, z: 0.03}, orientation: {x: -0.12,y: 0.65,z: 0.13,w: 0.74}}'
$ rostopic pub -1 /sweet_pose geometry_msgs/Pose  '{position:  {x: 0.17, y: -0.07, z: 0.04}, orientation: {x: 0.13,y: 0.62,z: -0.15,w: 0.75}}'
```
