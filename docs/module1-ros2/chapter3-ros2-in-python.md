# Chapter 3: ROS 2 in Python (rclpy)

This chapter focuses on `rclpy`, the Python client library for ROS 2. Python is widely used in robotics for its readability, extensive libraries, and rapid prototyping capabilities, making it an excellent choice for interacting with ROS 2.

## 3.1 Introduction to `rclpy`

`rclpy` is the official Python API for ROS 2. It provides the necessary interfaces to create ROS 2 nodes and interact with the ROS 2 graph using Python. It builds upon `rcl`, the C library that forms the foundation for all ROS 2 client libraries.

**Key Features of `rclpy`:**

*   **Ease of Use**: Python's syntax makes it straightforward to write ROS 2 applications.
*   **Rapid Prototyping**: Ideal for quick development and testing of robotic behaviors.
*   **Integration**: Seamlessly integrates with Python's rich ecosystem of data science, machine learning, and computer vision libraries.
*   **Asynchronous Support**: Leverages Python's `asyncio` for efficient handling of concurrent operations.

## 3.2 Setting up a ROS 2 Python Package

Before writing `rclpy` code, you need to set up a proper ROS 2 package. A typical Python package structure within a ROS 2 workspace looks like this:

```
my_robot_ws/
├── src/
│   └── my_python_pkg/
│       ├── my_python_pkg/
│       │   ├── __init__.py
│       │   └── my_node.py
│       ├── resource/
│       │   └── my_python_pkg
│       ├── setup.py
│       ├── package.xml
│       └── CMAKELists.txt  # (Optional, but often included for consistency)
├── install/
├── build/
└── log/
```

**Key files in a Python package:**

*   `setup.py`: Standard Python setup file, used by `colcon` (the ROS 2 build tool) to install Python scripts and dependencies.
*   `package.xml`: Defines package metadata, dependencies, and build tool requirements.
*   `my_python_pkg/__init__.py`: Makes the `my_python_pkg` directory a Python package.
*   `my_python_pkg/my_node.py`: Contains the Python code for your ROS 2 node(s).
*   `resource/my_python_pkg`: A marker file for `colcon`.

## 3.3 Minimal `rclpy` Node Examples

Here are conceptual pseudo-code examples demonstrating minimal `rclpy` nodes for publishers and subscribers.

### Minimal Publisher Node (pseudo-code)

```python
# my_robot_ws/src/my_python_pkg/my_python_pkg/simple_publisher.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SimplePublisher(Node):

    def __init__(self):
        super().__init__('simple_publisher')
        self.publisher_ = self.create_publisher(String, 'my_topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS 2 from Python: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)

    simple_publisher = SimplePublisher()

    rclpy.spin(simple_publisher)

    simple_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Minimal Subscriber Node (pseudo-code)

```python
# my_robot_ws/src/my_python_pkg/my_python_pkg/simple_subscriber.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SimpleSubscriber(Node):

    def __init__(self):
        super().__init__('simple_subscriber')
        self.subscription = self.create_subscription(
            String,
            'my_topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)

    simple_subscriber = SimpleSubscriber()

    rclpy.spin(simple_subscriber)

    simple_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 3.4 Package `setup.py` and `package.xml` for `rclpy`

**`setup.py` (pseudo-code)**

```python
from setuptools import setup

package_name = 'my_python_pkg'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='A minimal ROS 2 Python package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_publisher = my_python_pkg.simple_publisher:main',
            'simple_subscriber = my_python_pkg.simple_subscriber:main',
        ],
    },
)
```

**`package.xml` (pseudo-code)**

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_python_pkg</name>
  <version>0.0.1</version>
  <description>A minimal ROS 2 Python package</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake_python</buildtool_depend>
  <buildtool_depend>colcon_common_extensions</buildtool_depend>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>

## 3.5 Conceptualizing LLM-Robot Command Examples

Large Language Models (LLMs) can play a crucial role in enabling more natural and intuitive human-robot interaction. By translating natural language commands into robot-executable actions, LLMs bridge the gap between high-level human intent and low-level robot control.

Here, we conceptualize how an LLM might generate ROS 2 commands, focusing on the interface between an LLM and an `rclpy` node.

### LLM-to-ROS 2 Command Flow (Conceptual)

1.  **User Input**: A human user provides a natural language command (e.g., "Robot, go to the kitchen and pick up the red cup.").
2.  **LLM Processing**: An LLM (running perhaps on an edge device or cloud) receives this command.
3.  **Command Translation**: The LLM, trained on robot capabilities and ROS 2 interfaces, translates the natural language into a structured, executable ROS 2 command. This might involve:
    *   **Task Decomposition**: Breaking "go to the kitchen and pick up the red cup" into "navigate to kitchen" and "manipulate red cup".
    *   **Parameter Extraction**: Identifying objects ("red cup"), locations ("kitchen"), and actions ("pick up").
    *   **ROS 2 Message/Service/Action Generation**: Formulating the appropriate ROS 2 message (e.g., a `MoveToGoal` action with a `target_location` parameter, or a `PickObject` service call with `object_id` and `color` parameters).
4.  **ROS 2 Interface Node**: An `rclpy` node acts as an interface, receiving the structured command from the LLM.
5.  **Execution**: This interface node then publishes to relevant ROS 2 topics, calls services, or sends action goals to other robot control nodes to execute the command.
6.  **Feedback**: Robot sends feedback (e.g., "Navigating to kitchen," "Red cup acquired") which can be relayed back to the LLM or directly to the user.

### Pseudo-code: LLM Interface Node (conceptual)

This `rclpy` node would be responsible for receiving structured commands from an LLM and dispatching them to other ROS 2 components.

```python
# my_robot_ws/src/my_python_pkg/my_python_pkg/llm_interface_node.py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String # Assuming simple string commands from LLM for now
from geometry_msgs.msg import PoseStamped # For navigation goals
from custom_interfaces.srv import PickObject # Custom service for manipulation
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose # Example navigation action

class LLMInterfaceNode(Node):

    def __init__(self):
        super().__init__('llm_interface_node')
        self.llm_command_subscription = self.create_subscription(
            String,
            'llm_commands',
            self.llm_command_callback,
            10)
        self.llm_command_subscription # prevent unused variable warning

        # Example publishers/clients for robot control
        self.nav_action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.pick_object_client = self.create_client(PickObject, 'pick_object_service')

        self.get_logger().info('LLM Interface Node initialized.')

    def llm_command_callback(self, msg):
        raw_command = msg.data
        self.get_logger().info(f'Received LLM command: "{raw_command}"')

        # --- Conceptual LLM parsing and command generation ---
        # In a real system, an LLM would parse raw_command and output structured data.
        # For this example, we'll simulate a simple parsing.
        if "go to kitchen" in raw_command.lower():
            self.send_navigation_goal("kitchen")
        elif "pick up red cup" in raw_command.lower():
            self.call_pick_object_service("red cup", "red")
        else:
            self.get_logger().warn(f'Unknown command: {raw_command}')

    def send_navigation_goal(self, location):
        self.get_logger().info(f'Sending navigation goal to: {location}')
        # This is highly conceptual; actual navigation would involve complex poses
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        # Dummy pose for conceptual example
        goal_msg.pose.pose.position.x = 1.0 if location == "kitchen" else 0.0
        goal_msg.pose.pose.position.y = 2.0 if location == "kitchen" else 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.nav_action_client.wait_for_server()
        future = self.nav_action_client.send_goal_async(goal_msg)
        future.add_done_callback(self.nav_goal_response_callback)

    def nav_goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Navigation goal rejected :(')
            return
        self.get_logger().info('Navigation goal accepted :)')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.nav_result_callback)

    def nav_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Navigation complete!')

    def call_pick_object_service(self, object_name, color):
        self.get_logger().info(f'Calling pick object service for: {color} {object_name}')
        while not self.pick_object_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Pick object service not available, waiting again...')
        request = PickObject.Request()
        request.object_name = object_name
        request.color = color
        future = self.pick_object_client.call_async(request)
        future.add_done_callback(self.pick_object_response_callback)

    def pick_object_response_callback(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Successfully picked up {response.object_name}')
            else:
                self.get_logger().error(f'Failed to pick up {response.object_name}: {response.message}')
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')

def main(args=None):
    rclpy.init(args=args)

    llm_interface_node = LLMInterfaceNode()

    rclpy.spin(llm_interface_node)

    llm_interface_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
``````