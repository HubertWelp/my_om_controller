#!/usr/bin/env python3.8
import rospy
from geometry_msgs.msg import Pose
from open_manipulator_msgs.srv import SetKinematicsPose, SetKinematicsPoseRequest
from open_manipulator_msgs.srv import SetJointPosition, SetJointPositionRequest
from movement_listener import open_manipulator_velocity_listener
from std_msgs.msg import String
import time

# Defines

# Gripper
OPEN_GRIPPER = 0.010
CLOSE_GRIPPER = -0.01

# Fallback global sleep
MOVEMENT_SLEEP_TIME = 3.0
GRIPPER_SLEEP_TIME = 0.65
POLLING_TIME = 0.5

# Sweetpicker relevant stuff
# Topic from which the Openmanipulator receives coordinates
SWEETPICKER_COORDINATE_TOPIC = "sweet_pose_translated"
# Topic which the SweetPicker expects the reply on
SWEETPICKER_REPLY_TOPIC = "robot/status"
SWEETPICKER_REPLY_TOPIC = "rueckmeldung"
# Specified in SW-Architektur 2.2.3.3 rueckmeldung
SUCCESS_REPLY = "Süßigkeit dargereicht"
# NOT SPECIFIED
FAILURE_REPLY = "0"


class publisher:
    def __init__(self, topicName: str, type):
        self._publishedTopicName = topicName

        try:
            self._publishedTopic = rospy.Publisher(
                self._publishedTopicName, type, queue_size=10
            )
            self._rate = rospy.Rate(1)  # hz
            rospy.loginfo(rospy.get_caller_id() + ": Publisher has been started")
        except Exception as e:
            rospy.logerr(
                rospy.get_caller_id()
                + "An exception occurred! Node could not be started (generic publisher)."
                + str(e)
            )

    def publish(self, msg) -> None:
        rospy.loginfo(
            rospy.get_caller_id() + ": publishing: '%s' on topic: '%s'",
            msg,
            self._publishedTopicName,
        )
        self._publishedTopic.publish(msg)
        self._rate.sleep()


class sweetpicker_openmanipulator_coordinator:
    def __init__(self) -> None:
        # Initialize in home position
        rospy.init_node("openmanipulator_pick_and_place_client")

        # Launch movement listener
        try:
            self.__movement_listener = open_manipulator_velocity_listener()
        except Exception as e:
            rospy.logerr(
                rospy.get_caller_id()
                + "An exception occurred! movement_listener Node could not be started."
                + str(e)
            )
        print("move to init pose")
        self.move_to_init_pose()
        print("open gripper")
        self.control_gripper(OPEN_GRIPPER)

        # Subscribe to sweet_pose and wait for activity
        rospy.loginfo(
            rospy.get_caller_id() + ": Node has been started. Waiting for order..."
        )
        print('starting '+SWEETPICKER_COORDINATE_TOPIC+' listener')
        self._subscribedTopic = rospy.Subscriber(
            SWEETPICKER_COORDINATE_TOPIC, Pose, callback=self.pose_callback
        )
        self._publishedTopic = publisher(topicName=SWEETPICKER_REPLY_TOPIC, type=String)
        rospy.on_shutdown(self.shutdown)
        rospy.spin()

    def shutdown(self) -> bool:
        rospy.loginfo(
            rospy.get_caller_id()
            + ": Shutting down node and moving the robot to a safe position"
        )
        self.control_gripper(CLOSE_GRIPPER)
        target_position = [0.0, 0.3, 0.0, 1.25]
        response = self.move_to_position_joint_space(target_position)

        if response:
            rospy.loginfo(
                rospy.get_caller_id()
                + ": Robot in safe position. Ready to switch off the power supply..."
            )
        else:
            rospy.logerr(
                rospy.get_caller_id()
                + ": Robot unable to reach a safe position! manual support required when switching off the power supply!"
            )
        return response

    def control_gripper(self, val: float) -> bool:
        service_name = "/goal_tool_control"
        rospy.wait_for_service(service_name)

        try:
            gripper_control = rospy.ServiceProxy(service_name, SetJointPosition)

            arg = SetJointPositionRequest()
            arg.planning_group = "gripper"
            arg.joint_position.joint_name = ["gripper"]
            arg.joint_position.position = [val]
            arg.joint_position.max_accelerations_scaling_factor = 1.0
            arg.joint_position.max_velocity_scaling_factor = 1.0
            arg.path_time = 0.5

            resp = gripper_control(arg)
            # Hardcoded sleep duration as the gripper does not output velocity information
            rospy.sleep(GRIPPER_SLEEP_TIME)
            return resp.is_planned

        except rospy.ServiceException as exc:
            print(f"Service '/goal_tool_control' did not process request: {exc}")
            return False

    def pose_callback(self, msg: Pose) -> None:
        rospy.loginfo(
            rospy.get_caller_id()
            + ": Received order for: x: "
            + str(msg.position.x)
            + " y: "
            + str(msg.position.y)
            + " z: "
            + str(msg.position.z)
        )
        print('Message received on topic sweet_pose_translated')
        try:
            # Convert coordinates to correct format
            target_object = SetKinematicsPoseRequest()

            target_object.kinematics_pose.pose.position.x = float(
                format(float(msg.position.x), ".3f")
            )
            target_object.kinematics_pose.pose.position.y = float(
                format(float(msg.position.y), ".3f")
            )
            target_object.kinematics_pose.pose.position.z = float(
                format(float(msg.position.z), ".3f")
            )

            # Target coordinates right above the object
            target_object_birds_eye_view = SetKinematicsPoseRequest()

            target_object_birds_eye_view.kinematics_pose.pose.position.x = float(
                format(float(msg.position.x), ".3f")
            )
            target_object_birds_eye_view.kinematics_pose.pose.position.y = float(
                format(float(msg.position.y), ".3f")
            )
            target_object_birds_eye_view.kinematics_pose.pose.position.z = float(
                format(float(msg.position.z + 0.04), ".3f")
            )

            # Stage A - Grasping
            try:
                result = self.move_to_home_pose()
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage A Step 1/3 Result: %s", result
                )
                result = self.control_gripper(OPEN_GRIPPER)
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage A Gripping Result: %s", result
                )

                result = self.move_to_position_task_space(
                    target_object_birds_eye_view.kinematics_pose.pose.position
                )
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage A Step 2/3 Result: %s", result
                )

                result = self.move_to_position_task_space(
                    target_object.kinematics_pose.pose.position
                )
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage A Step 3/3 Result: %s", result
                )
                result = self.control_gripper(CLOSE_GRIPPER)
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage A Gripping Result: %s", result
                )
            except Exception as e:
                rospy.logerr("Ran into Problem in movement routine: " + str(e))
                self.move_to_init_pose()
                self._publishedTopic.publish(FAILURE_REPLY)

            # Stage B - Delivery
            try:
                result = self.move_to_position_task_space(
                    target_object_birds_eye_view.kinematics_pose.pose.position
                )
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage B Step 1/3 Result: %s", result
                )
                result = self.move_to_init_delivery_pose()
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage B Step 2/3 Result: %s", result
                )
                result = self.move_to_delivery_pose()
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage B Step 3/3 Result: %s", result
                )
                result = self.control_gripper(OPEN_GRIPPER)
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage B Gripping Result: %s", result
                )
            except Exception as e:
                rospy.logerr("Ran into Problem in movement routine: " + str(e))
                self.move_to_init_pose()
                self._publishedTopic.publish(FAILURE_REPLY)

            # Stage C - Cleanup
            try:
                result = self.move_to_init_pose()
                rospy.loginfo(
                    rospy.get_caller_id() + ": Stage C Step 1/2 Result: %s", result
                )
                rospy.loginfo(rospy.get_caller_id() + ": Stage C Step 2/2 Publishing..")
                self._publishedTopic.publish(SUCCESS_REPLY)

            except Exception as e:
                rospy.logerr(
                    rospy.get_caller_id()
                    + ": Ran into Problem in movement routine: "
                    + str(e)
                )
                self.move_to_init_pose()
                self._publishedTopic.publish(FAILURE_REPLY)

        except rospy.ServiceException as exc:
            rospy.logerr(
                rospy.get_caller_id()
                + f": Service '/goal_task_space_path' did not process request: {exc}"
            )
            self.move_to_init_pose()
            self._publishedTopic.publish(FAILURE_REPLY)

    def move_to_center_pose(self) -> bool:
        target_position = [0.0, 0.0, 0.0, 0.0]
        return self.move_to_position_joint_space(target_position)

    def move_to_init_pose(self) -> bool:
        target_position = [1.6, 0.0, 0.0, 1.2]
        result = self.move_to_position_joint_space(target_position)
        self.control_gripper(OPEN_GRIPPER)
        return result

    def move_to_init_delivery_pose(self) -> bool:
        target_position = [1.6, 0.0, 0.0, 0.0]
        return self.move_to_position_joint_space(target_position)

    def move_to_delivery_pose(self) -> bool:
        target_position = [1.6, 0.3, 0.0, 1.2]
        return self.move_to_position_joint_space(target_position)

    def move_to_home_pose(self) -> bool:
        target_position = [0.0, 0.0, 0.0, 1.2]
        return self.move_to_position_joint_space(target_position)

    def move_to_position_task_space(self, lst) -> bool:
        # Check format
        if isinstance(lst, Pose):
            raise ValueError(
                "Type 'Pose' with length 3 was expected! received type '"
                + str(type(lst))
                + "'"
            )

        # Wait for service
        service_name = "goal_task_space_path_position_only"
        # rospy.loginfo("Waiting for service: '%s'", service_name)
        rospy.wait_for_service(service_name)

        # Set target Position
        arg = SetKinematicsPoseRequest()
        arg.end_effector_name = "gripper"
        arg.kinematics_pose.pose.position = lst
        arg.kinematics_pose.tolerance = 0.5
        arg.kinematics_pose.max_accelerations_scaling_factor = 1.0
        arg.kinematics_pose.max_velocity_scaling_factor = 1.0
        arg.path_time = 3

        # Execute move request
        try:
            target_position = rospy.ServiceProxy(
                name=service_name, service_class=SetKinematicsPose, persistent=True
            )
            print("Target-Position: /n"+ str(arg.kinematics_pose.pose.position))
            response = target_position(arg)

            # Blocking call
            print("check movement task space")
            # rospy.sleep(POLLING_TIME*10)
            self.check_movement()
            print("movement checked")
            
            if response is False:
                raise Exception("OM-Controller was unable to solve the IK!")
        except rospy.ServiceException as e:
            print(
                "An exception occurred! Service "
                + str(service_name)
                + " did not process request: "
                + str(e)
            )
            return False

        return response.is_planned

    def move_to_position_joint_space(self, lst) -> bool:
        # Check list format (not checking if they're numbers or letters)
        if isinstance(lst, list) and len(lst) != 4:
            raise ValueError(
                "Type list with length 4 was expected! received type '"
                + str(type(lst))
                + "' of size '"
                + str(len(lst))
                + "'"
            )

        # Wait for service
        service_name = "goal_joint_space_path"
        rospy.loginfo("Waiting for service: '%s'", service_name)
        rospy.wait_for_service(service_name)

        # Set joint properties
        print("Set joint properties")
        arg = SetJointPositionRequest()
        arg.joint_position.joint_name = ["joint1", "joint2", "joint3", "joint4"]
        arg.joint_position.position = lst
        arg.joint_position.max_accelerations_scaling_factor = 1.0
        arg.joint_position.max_velocity_scaling_factor = 1.0
        arg.path_time = 3

        # Execute move request
        try:
            target_position = rospy.ServiceProxy(
                name=service_name, service_class=SetJointPosition, persistent=True
            )
            response = target_position(arg)

            # Blocking call
            print("check movement joint space")
            self.check_movement()
            #rospy.sleep(POLLING_TIME*10)
            print("movement checked")

            if response is False:
                raise Exception("OM-Controller was unable to solve the IK!")
        except rospy.ServiceException as e:
            print(
                "An exception occurred! Service "
                + str(service_name)
                + " did not process request: "
                + str(e)
            )
            return False
        except Exception as exc:
            print("An exception occurred! " + str(exc))
            return False

        return response.is_planned

    # Blocking call
    def check_movement(self) -> None:
        time_now = time.time()
        print('check_movement: wait while moving')
        while self.__movement_listener._is_moving is False:
            rospy.sleep(POLLING_TIME)
            if time_now + 2 < time.time():
                print("timeout")
                break
            else:
     #           print(time.time() - time_now)
                pass

        while self.__movement_listener._is_moving is True:
     #   	print(time.time())
        	rospy.sleep(POLLING_TIME)


if __name__ == "__main__":
    try:
        coordinator = sweetpicker_openmanipulator_coordinator()
    except Exception as e:
        rospy.logerr(
            rospy.get_caller_id() + ": (OMX) Node could not be started: " + str(e)
        )
