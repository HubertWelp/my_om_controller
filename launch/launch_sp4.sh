#!/bin/bash

# Default to original system if no argument is provided
USE_YOLO=${1:-0}

# Display which object detector will be used
DETECTOR_TYPE=$([ "$USE_YOLO" -eq 1 ] && echo 'YOLO' || echo 'Original')
DETECTOR_CMD=$([ "$USE_YOLO" -eq 1 ] && echo "source /home/student/git/SP4/SweetPicker4/SP4Objekterkenner/venv_SP4Objekterkenner/bin/activate && python3 /home/student/git/SP4/SweetPicker4/SP4Objekterkenner/SP4Objekterkenner.py" || echo "python3.9 /home/student/git/SP4/SweetPicker4/SP4Objekterkenner/SP3Objekterkenner.py /home/student/git/SP4/SweetPicker4/SP4Bildanalysator/SP3Bilderkennung/aktuelleSzene.jpg")

# Launch all components in tabs
gnome-terminal \
    --tab --title="ROS Core" \
        --command="bash -c 'echo -e \"\e[1;34m===== ROS Core =====\e[0m\"; source ~/catkin_ws/devel/setup.bash; roscore; exec bash'" \
    --tab --title="SP4 Koordinator" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Koordinator =====\e[0m\"; sleep 2; source ~/catkin_ws/devel/setup.bash; rosrun SP4Koordinator SP4Koordinator; exec bash'" \
    --tab --title="SP4 Bildanalysator" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Bildanalysator =====\e[0m\"; sleep 3; /home/student/git/SP4/SweetPicker4/build-SP4Bildanalysator-Desktop_Qt_6_2_3_GCC_64bit-Debug/SP4Bildanalysator; exec bash'" \
    --tab --title="SP4 Admin" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Admin =====\e[0m\"; sleep 3; echo \"Passwort steht in konfig.ini (Wahrscheinlich SP4)\"; /home/student/git/SP4/SweetPicker4/build-SP4Admin-Desktop_Qt_6_2_3_GCC_64bit-Debug/SP4Admin; exec bash'" \
    --tab --title="SP4 Objekterkenner ($DETECTOR_TYPE)" \
        --command="bash -c 'echo -e \"\e[1;34m===== SP4 Objekterkenner ($DETECTOR_TYPE) =====\e[0m\"; sleep 4; $DETECTOR_CMD; exec bash'"

echo -e "\e[1;32mSP4 System launched with $DETECTOR_TYPE object detector.\e[0m"
