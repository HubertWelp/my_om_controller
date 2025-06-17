#! /usr/bin/env python3

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Pose


def callback_pose(data: Pose) -> None:
    rospy.loginfo(
        rospy.get_caller_id()
        + ": Received order for: x: "
        + str(data.position.x)
        + " y: "
        + str(data.position.y)
        + " z: "
        + str(data.position.z)
    )


def callback_string(data: String) -> None:
    rospy.loginfo(f"Received message: {data.data}")


def listener() -> None:
    rospy.init_node("simpleSubcriber", anonymous=True)
    rospy.Subscriber("simpleChatter", String, callback_string)
    rospy.loginfo(
        "SimpleSubscriber node started, waiting for messages on /simpleChatter ..."
    )
    rospy.spin()


if __name__ == "__main__":
    try:
        listener()
    except rospy.ROSInterruptException:
        pass
