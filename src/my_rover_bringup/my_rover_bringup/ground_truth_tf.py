import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, TransformStamped
from tf2_ros import TransformBroadcaster


class GroundTruthTF(Node):
    def __init__(self):
        super().__init__('ground_truth_tf')

        self.declare_parameter('model_link_name', 'my_rover::base_link')
        self.link_name = self.get_parameter('model_link_name').value

        self.br = TransformBroadcaster(self)
        self.sub = self.create_subscription(
            PoseArray,
            '/model/my_rover/pose',
            self.pose_callback,
            10,
        )

    def pose_callback(self, msg: PoseArray):
        if not msg.poses:
            return

        # PoseArray from Pose_V has no per-pose names by default, so if
        # publish_link_pose picks up multiple links, index 0 is usually
        # the model/base_link pose. Verify with:
        #   ros2 topic echo /model/my_rover/pose
        # and adjust the index below if base_link isn't first.
        pose = msg.poses[0]

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'my_rover/odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = pose.position.x
        t.transform.translation.y = pose.position.y
        t.transform.translation.z = pose.position.z
        t.transform.rotation = pose.orientation

        self.br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = GroundTruthTF()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()