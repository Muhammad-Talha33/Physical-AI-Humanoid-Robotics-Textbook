# Chapter 5: Sensor Integration in ROS 2

Sensor integration is fundamental for any robot, especially humanoids, to perceive their environment and interact intelligently. This chapter explores how various sensors are integrated into ROS 2, focusing on the concepts of ROS 2 interfaces, message types, and the Transform (TF) tree.

## 5.1 ROS 2 Sensor Interfaces

ROS 2 provides standard message types and conventions for common robot sensors, ensuring interoperability between different hardware and software components. These interfaces simplify the process of publishing sensor data to the ROS 2 graph.

**Common Sensor Types and Their ROS 2 Messages:**

*   **Cameras**: Used for computer vision tasks. ROS 2 provides `sensor_msgs/msg/Image` for raw image data and `sensor_msgs/msg/CameraInfo` for camera calibration parameters.
*   **LiDAR/Depth Sensors**: Provide point cloud data for environmental mapping and obstacle avoidance. `sensor_msgs/msg/PointCloud2` and `sensor_msgs/msg/LaserScan` are typically used.
*   **IMUs (Inertial Measurement Units)**: Measure orientation, angular velocity, and linear acceleration. `sensor_msgs/msg/Imu` is the standard message type.
*   **Joint State Sensors**: Report the position, velocity, and effort of robot joints. `sensor_msgs/msg/JointState` is used for this purpose.
*   **Force/Torque Sensors**: Measure forces and torques applied to robot end-effectors or joints. `geometry_msgs/msg/WrenchStamped` can be used.

### Conceptual Sensor Node (Publisher)

A typical sensor integration involves a ROS 2 node (often a device driver) that reads data from the physical sensor and publishes it to a corresponding ROS 2 topic.

```python
# pseudo-code for a conceptual camera sensor node

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge # Assumed for converting OpenCV images to ROS 2 messages
import cv2

class CameraSensorNode(Node):

    def __init__(self):
        super().__init__('camera_sensor_node')
        self.image_publisher_ = self.create_publisher(Image, 'camera/image_raw', 10)
        self.info_publisher_ = self.create_publisher(CameraInfo, 'camera/camer-info', 10)
        self.timer = self.create_timer(0.1, self.publish_camera_data) # 10 Hz
        self.bridge = CvBridge()
        self.get_logger().info('Camera Sensor Node initialized.')

    def publish_camera_data(self):
        # --- Conceptual: Read image from hardware ---
        # For a real robot, this would involve reading from a camera sensor.
        # Here, we simulate a dummy image.
        dummy_image = cv2.imread('path/to/dummy_image.jpg') # Replace with actual sensor read
        if dummy_image is None:
            self.get_logger().warn('Could not load dummy image.')
            return

        # Convert OpenCV image to ROS 2 Image message
        ros_image_msg = self.bridge.cv2_to_imgmsg(dummy_image, "bgr8")
        ros_image_msg.header.stamp = self.get_clock().now().to_msg()
        ros_image_msg.header.frame_id = 'camera_frame'
        self.image_publisher_.publish(ros_image_msg)

        # --- Conceptual: Publish CameraInfo (from calibration) ---
        camer-info_msg = CameraInfo()
        camer-info_msg.header.stamp = ros_image_msg.header.stamp
        camer-info_msg.header.frame_id = 'camera_frame'
        # Fill in actual camera calibration parameters here (K, D, R, P, etc.)
        # camer-info_msg.k = [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        self.info_publisher_.publish(camer-info_msg)

def main(args=None):
    rclpy.init(args=args)
    camer-node = CameraSensorNode()
    rclpy.spin(camer-node)
    camer-node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 5.2 The Transform (TF) Tree

The **Transform (TF) tree** is a crucial concept in ROS 2 for keeping track of multiple coordinate frames and transforming data between them. Robots typically have many sensors and actuators, each with its own local coordinate frame. TF allows you to manage these frames and understand the spatial relationships between different parts of the robot and its environment.

**Key Aspects of TF:**

*   **Coordinate Frames**: Each link in the URDF, and each sensor, has an associated coordinate frame.
*   **Transforms**: Represent the rigid body transformation (position and orientation) from one coordinate frame to another.
*   **Broadcaster**: A node that publishes transforms (e.g., `robot_state_publisher` broadcasting transforms from URDF, or a sensor driver broadcasting its own frame).
*   **Listener**: A node that queries transforms to get the relationship between any two frames at a specific point in time.

### Why TF is Critical for Humanoids:

*   **Perception**: Transform sensor data (e.g., camera images, LiDAR points) from the sensor's frame to a common robot base frame or world frame.
*   **Manipulation**: Calculate the required end-effector pose relative to a target object, considering the robot's current joint states and its base frame.
*   **Navigation**: Relate the robot's base frame to a map frame for localization and path planning.
*   **Kinematics**: Used by inverse and forward kinematics solvers to determine joint angles for desired poses.

### Conceptual TF Broadcaster (Static or Dynamic)

Nodes can publish transforms to the TF tree, either static (unchanging) or dynamic (changing over time, like a robot joint).

```python
# pseudo-code for a conceptual static TF broadcaster node

import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import tf_transformations # for quaternion calculations

class StaticTFBroadcaster(Node):

    def __init__(self):
        super().__init__('static_tf_broadcaster')
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        self.make_static_transform()
        self.get_logger().info('Static TF Broadcaster initialized.')

    def make_static_transform(self):
        static_transform_stamped = TransformStamped()
        static_transform_stamped.header.stamp = self.get_clock().now().to_msg()
        static_transform_stamped.header.frame_id = 'base_link' # Parent frame
        static_transform_stamped.child_frame_id = 'camera_frame' # Child frame

        static_transform_stamped.transform.translation.x = 0.1
        static_transform_stamped.transform.translation.y = 0.0
        static_transform_stamped.transform.translation.z = 0.5

        quat = tf_transformations.quaternion_from_euler(0.0, 0.0, 0.0)
        static_transform_stamped.transform.rotation.x = quat[0]
        static_transform_stamped.transform.rotation.y = quat[1]
        static_transform_stamped.transform.rotation.z = quat[2]
        static_transform_stamped.transform.rotation.w = quat[3]

        self.static_tf_broadcaster.sendTransform(static_transform_stamped)

def main(args=None):
    rclpy.init(args=args)
    static_broadcaster = StaticTFBroadcaster()
    try:
        rclpy.spin(static_broadcaster)
    except KeyboardInterrupt:
        pass
    static_broadcaster.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Conceptual TF Listener (Lookup Transforms)

A TF listener node can query the TF tree to find the transform between any two existing frames.

```python
# pseudo-code for a conceptual TF listener node

import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
import time

class TFListenerNode(Node):

    def __init__(self):
        super().__init__('tf_listener_node')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(1.0, self.lookup_transform) # Lookup every 1 second
        self.get_logger().info('TF Listener Node initialized.')

    def lookup_transform(self):
        try:
            # Get the transform from 'base_link' to 'camera_frame'
            t = self.tf_buffer.lookup_transform(
                'base_link', 'camera_frame', rclpy.time.Time())
            self.get_logger().info(f'Transform from base_link to camera_frame: '
                                  f'Translation: x={t.transform.translation.x}, '
                                  f'y={t.transform.translation.y}, '
                                  f'z={t.transform.translation.z} | '
                                  f'Rotation: x={t.transform.rotation.x}, '
                                  f'y={t.transform.rotation.y}, '
                                  f'z={t.transform.rotation.z}, '
                                  f'w={t.transform.rotation.w}')
        except Exception as e:
            self.get_logger().error(f'Could not transform: {e}')

def main(args=None):
    rclpy.init(args=args)
    tf_listener = TFListenerNode()
    rclpy.spin(tf_listener)
    tf_listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```