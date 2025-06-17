#!/bin/bash

# Default to original system if no argument is provided
USE_YOLO=${1:-0}

# Display which object detector will be used
DETECTOR_TYPE=$([ "$USE_YOLO" -eq 1 ] && echo 'YOLO' || echo 'Original')
DETECTOR_CMD=$([ "$USE_YOLO" -eq 1 ] && echo "source /home/student/git/SP4/SweetPicker4/SP4Objekterkenner/venv_SP4Objekterkenner/bin/activate && python3 /home/student/git/SP4/SweetPicker4/SP4Objekterkenner/SP4Objekterkenner.py" || echo "python3.9 /home/student/git/SP4/SweetPicker4/SP4Objekterkenner/SP3Objekterkenner.py /home/student/git/SP4/SweetPicker4/SP4Bildanalysator/SP3Bilderkennung/aktuelleSzene.jpg")

# Set up permissions for USB port
sudo chmod a+rw /dev/ttyACM0

# Launch all components in tabs
gnome-terminal \
    --tab --title="ROS Core" \
        --command="bash -c 'echo -e \"\e[1;34m===== ROS Core =====\e[0m\"; source ~/catkin_ws/devel/setup.bash; roscore; exec bash'" \
    --tab --title="OMX Controller" \
        --command="bash -c 'echo -e \"\e[1;34m===== OMX Controller =====\e[0m\"; sleep 2; source ~/catkin_ws/devel/setup.bash; roslaunch open_manipulator_controller open_manipulator_controller.launch usb_port:=/dev/ttyACM0 baud_rate:=1000000; exec bash'" \
    --tab --title="Coordinate Translator" \
        --command="bash -c 'echo -e \"\e[1;34m===== Coordinate Translator =====\e[0m\"; sleep 3; source ~/catkin_ws/devel/setup.bash; rosrun my_om_controller coordinate_translator.py; exec bash'" \
    --tab --title="OpenManipulator Service" \
        --command="bash -c 'echo -e \"\e[1;34m===== OpenManipulator Service =====\e[0m\"; sleep 4; source ~/catkin_ws/devel/setup.bash; rosrun my_om_controller my_om_service_client_pick_and_place_2.py; exec bash'" \
    --tab --title="SP4 Koordinator" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Koordinator =====\e[0m\"; sleep 5; source ~/catkin_ws/devel/setup.bash; rosrun SP4Koordinator SP4Koordinator; exec bash'" \
    --tab --title="SP4 Bildanalysator" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Bildanalysator =====\e[0m\"; sleep 6; /home/student/git/SP4/SweetPicker4/build-SP4Bildanalysator-Desktop_Qt_6_2_3_GCC_64bit-Debug/SP4Bildanalysator; exec bash'" \
    --tab --title="SP4 Admin" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Admin =====\e[0m\"; sleep 6; echo \"Passwort steht in konfig.ini (Wahrscheinlich SP4)\"; /home/student/git/SP4/SweetPicker4/build-SP4Admin-Desktop_Qt_6_2_3_GCC_64bit-Debug/SP4Admin; exec bash'" \
    --tab --title="SP4 Objekterkenner ($DETECTOR_TYPE)" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Objekterkenner ($DETECTOR_TYPE) =====\e[0m\"; sleep 7; $DETECTOR_CMD; exec bash'"

echo -e "\e[1;32mSP4 System with OpenManipulator X launched using $DETECTOR_TYPE object detector.\e[0m"
