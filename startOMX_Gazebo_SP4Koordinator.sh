#!/bin/bash

# Analyse whether an IP-adress is provided as an argument for SP4Koordinator and ros_bridge
if [ -z "$1" ]; then
	IP_ADRESS_BILDANALYSATOR='127.0.0.1'
else
	IP_ADRESS_BILDANALYSATOR=$1
fi
IP_ADRESS_CHATBOT_ORCHESTRATOR=$IP_ADRESS_BILDANALYSATOR
echo $IP_ADRESS_CHATBOT_ORCHESTRATOR

# Launch all components in tabs
gnome-terminal \
    --tab --title="ROS Core" \
        --command="bash -c 'echo -e \"\e[1;34m===== ROS Core =====\e[0m\"; source ~/catkin_ws/devel/setup.bash; roscore; exec bash'" \
    --tab --title="OMX Controller" \
        --command="bash -c 'echo -e \"\e[1;34m===== OMX Controller =====\e[0m\"; sleep 2; source ~/catkin_ws/devel/setup.bash; roslaunch my_om_controller my_om_gazebo.launch; exec bash'" \
    --tab --title="Staic Transform Publisher" \
        --command="bash -c 'echo -e \"\e[1;34m===== Static Transform Publisher =====\e[0m\"; sleep 3; source ~/catkin_ws/devel/setup.bash; rosrun tf2_ros static_transform_publisher 0.055 -0.140 0.0 1.57 0.0 3.14  world camera; exec bash'" \
    --tab --title="Coordinate Translator" \
        --command="bash -c 'echo -e \"\e[1;34m===== Coordinate Translator =====\e[0m\"; sleep 3; source ~/catkin_ws/devel/setup.bash; rosrun my_om_controller coordinate_translator.py; exec bash'" \
    --tab --title="OpenManipulator Service" \
        --command="bash -c 'echo -e \"\e[1;34m===== OpenManipulator Service	 =====\e[0m\"; sleep 4; source ~/catkin_ws/devel/setup.bash; rosrun my_om_controller my_om_service_openmanipulator_pick_and_place_client_2.py; exec bash'" \
    --tab --title="ROS Bridge" \
        --command="bash -c 'echo -e \"\e[1;34m===== ROS Bridge --IP $IP_ADRESS_CHATBOT_ORCHESTRATOR =====\e[0m\"; sleep 3; source ~/catkin_ws/devel/setup.bash; rosrun chatbot_lm ros_bridge.py --IP $IP_ADRESS_CHATBOT_ORCHESTRATOR; exec bash'" \
    --tab --title="SP4 Koordinator" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Koordinator --IP $IP_ADRESS_BILDANALYSATOR =====\e[0m\"; sleep 5; source ~/catkin_ws/devel/setup.bash; rosrun SP4Koordinator SP4Koordinator --IP $IP_ADRESS_BILDANALYSATOR; exec bash'" \


echo -e "\e[1;32mSP4 System with OpenManipulator X launched using object detector.\e[0m"
