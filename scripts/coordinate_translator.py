#! /usr/bin/env python3
import rospy
from geometry_msgs.msg import Pose, PoseStamped
import tf2_ros
import tf2_geometry_msgs


# # Offsets for camera-omx coordinate system
OFFSET_OMX_Z = 0.030  # so we dont scrape the baseplate
MM_TO_M = 1 / 1000
M_TO_MM = 1000


class sweetpicker_openmanipulator_mediator_subscriber:
    def __init__(self):
        self._nodeName = "SweetPicker_CoordinateTranslator"
        self._subscribedTopicName = "robot/pose"

        try:
            rospy.init_node(self._nodeName, anonymous=False)

            # Subscribe sweet_pose
            self._subscribedTopic = rospy.Subscriber(
                self._subscribedTopicName, PoseStamped, self.transform_pose_callback
            )

            self._rate = rospy.Rate(1)  # hz
            rospy.loginfo(
                rospy.get_caller_id()
                + ": Subscriber has been started. Waiting on coordinates"
            )
            self._myPublisher = sweetpicker_openmanipulator_mediator_publisher()
        except Exception as e:
            rospy.logerr(
                rospy.get_caller_id()
                + "An exception occurred! Node could not be started."
                + str(e)
            )

    def transform_pose_callback(self, msg: PoseStamped) -> None:
        msg.pose.position.x = msg.pose.position.x * MM_TO_M
        msg.pose.position.y = msg.pose.position.y * MM_TO_M
        msg.pose.position.z = msg.pose.position.z * MM_TO_M
        print(f"{msg.pose.position}")
        transformed_pose = self.transform_pose(msg.pose, "camera", "world")
        transformed_pose.position.z = transformed_pose.position.z + OFFSET_OMX_Z
        self._myPublisher.publish_coordinates(transformed_pose)

        # print(f"{transformed_pose.position} \n ************** \n")

    def transform_pose(self, input_pose: Pose, from_frame: str, to_frame: str) -> Pose:
        # **Assuming /tf2 topic is being broadcasted
        tf_buffer = tf2_ros.Buffer()
        listener = tf2_ros.TransformListener(tf_buffer)

        pose_stamped = tf2_geometry_msgs.PoseStamped()
        pose_stamped.pose = input_pose
        pose_stamped.header.frame_id = from_frame
        pose_stamped.header.stamp = rospy.Time.now()

        try:
            # ** It is important to wait for the listener to start listening. Hence the rospy.Duration(1)
            output_pose_stamped = tf_buffer.transform(
                pose_stamped, to_frame, rospy.Duration(1)
            )
            return output_pose_stamped.pose

        except (
            tf2_ros.LookupException,
            tf2_ros.ConnectivityException,
            tf2_ros.ExtrapolationException,
        ):
            raise


class sweetpicker_openmanipulator_mediator_publisher:
    def __init__(self):
        self._publishedTopicName = "sweet_pose_translated"

        try:
            # rospy.init_node(self._nodeName, anonymous=False)

            # Publish sweet_pose_translated
            self._publishedTopic = rospy.Publisher(
                self._publishedTopicName, Pose, queue_size=10
            )
            self._rate = rospy.Rate(1)  # hz
            rospy.loginfo(
                rospy.get_caller_id()
                + ": Publisher has been started. Waiting on coordinates"
            )
        except Exception as e:
            rospy.logerr(
                rospy.get_caller_id()
                + "An exception occurred! Node could not be started."
                + str(e)
            )

    def publish_coordinates(self, msg: Pose) -> None:
        rospy.loginfo(
            rospy.get_caller_id() + ": publishing: x = %3.2f, y = %3.2f, z = %3.2f",
            msg.position.x,
            msg.position.y,
            msg.position.x,
        )
        self._publishedTopic.publish(msg)
        self._rate.sleep()


def main():
    sweetpicker_openmanipulator_mediator_subscriber()
    rospy.spin()


if __name__ == "__main__":
    main()
