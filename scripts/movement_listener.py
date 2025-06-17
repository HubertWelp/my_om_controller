#! /usr/bin/env python3.9

import rospy
from sensor_msgs.msg import JointState

# For float comparison
ZERO_THRESHOLD = 0.00001


class open_manipulator_velocity_listener:
    def __init__(self):
        try:
            # self._nodeName = "SweetPicker_VelocityListener"
            self._subscribedTopicName = "joint_states"
            self._is_moving = None

            # rospy.init_node(self._nodeName, anonymous=False)
            self._subscribedTopic = rospy.Subscriber(
                self._subscribedTopicName, JointState, self.callback
            )

            self._rate = rospy.Rate(1)  # hz
            rospy.loginfo(rospy.get_caller_id() + ": Starting Node")
        except Exception as e:
            rospy.logerr(
                rospy.get_caller_id() + ": could not be started: " + str(e)
            )

    def callback(self, data):
        total_velocity = sum(abs(velocity) for velocity in data.velocity)
        if total_velocity >= ZERO_THRESHOLD:
            self._is_moving = bool(True)
        else:
            self._is_moving = bool(False)


def main():
    open_manipulator_velocity_listener()
    rospy.spin()


if __name__ == "__main__":
    main()
