# Chapter 2: ROS 2 Core Concepts

This chapter delves into the fundamental building blocks of ROS 2, expanding on the overview from Chapter 1. A solid understanding of these concepts is crucial for developing robust and scalable robot applications.

## 2.1 Nodes: The Executable Units

In ROS 2, a **node** is an executable process that performs computation. Think of nodes as individual programs or modules within your robot's software system. Each node should ideally be responsible for a single, well-defined task.

**Key properties of Nodes:**

*   **Independence**: Nodes run independently and communicate over the ROS 2 graph.
*   **Modularity**: Encapsulate specific functionalities (e.g., a camera driver node, a motor controller node, a path planning node).
*   **Lifecycle Management**: Nodes can have defined states (e.g., unconfigured, inactive, active) and transitions, allowing for more reliable system startup and shutdown.

## 2.2 Topics: Asynchronous Data Streaming

**Topics** are the most common way for nodes to exchange data in ROS 2. They implement a publish/subscribe communication model, enabling asynchronous, many-to-many data streaming.

**How Topics Work:**

1.  **Publisher**: A node that sends messages on a specific topic.
2.  **Subscriber**: A node that receives messages from a specific topic.
3.  **Messages**: Data structures (defined using `.msg` files) that specify the type of information being sent.

When a publisher sends a message to a topic, all nodes subscribed to that topic receive a copy of the message. This decouples senders from receivers, making the system flexible.

## 2.3 Services: Synchronous Request/Response

**Services** provide a synchronous request/response communication mechanism. Unlike topics, which are for continuous data streams, services are used when a node needs to request a specific action or piece of information from another node and wait for an immediate response.

**How Services Work:**

1.  **Service Server**: A node that offers a service and implements the logic to handle requests.
2.  **Service Client**: A node that sends a request to a service server and blocks until a response is received.
3.  **Service Definition**: Defined using `.srv` files, specifying the structure of both the request and the response.

Services are ideal for discrete, single-shot operations like triggering a robot arm movement or querying a sensor's current status.

## 2.4 Actions: Goal-Oriented Feedback-Rich Tasks

**Actions** are designed for long-running, goal-oriented tasks that provide continuous feedback and allow for preemption. They combine aspects of both topics (feedback) and services (request/response for goal/result).

**How Actions Work:**

1.  **Action Server**: A node that accepts goals, executes the task, and sends periodic feedback.
2.  **Action Client**: A node that sends a goal to an action server, monitors its progress via feedback, and can cancel the goal.
3.  **Action Definition**: Defined using `.action` files, specifying the structure for the goal, result, and feedback.

Actions are perfect for complex tasks like navigating to a faraway location, picking up an object, or performing a lengthy inspection, where the client needs to know the progress and potentially intervene.

## 2.5 Parameters: Dynamic Configuration

**Parameters** are configuration values that can be set, retrieved, and updated by nodes at runtime. They allow for flexible adjustment of node behavior without recompiling code.

**Key aspects of Parameters:**

*   **Dynamic**: Can be changed during runtime.
*   **Typed**: Parameters have specific data types (e.g., integer, float, string, boolean).
*   **Hierarchical**: Parameters can be organized in namespaces.

Parameters are used for settings like sensor gains, motor speeds, or algorithm thresholds, which might need to be fine-tuned during operation.

## Conceptual Examples of ROS 2 Communication Patterns

### Node Example: Simple Publisher and Subscriber

**Publisher Node (conceptual)**

```python
# pseudo-code for a simple ROS 2 publisher node

import rclpy
from std_msgs.msg import String

def main():
    node = rclpy.create_node('minimal_publisher')
    publisher = node.create_publisher(String, 'topic', 10)
    msg = String()
    i = 0
    while rclpy.ok():
        msg.data = f'Hello World: {i}'
        node.get_logger().info(f'Publishing: "{msg.data}"')
        publisher.publish(msg)
        i += 1
        rclpy.spin_once(node, timeout_sec=1.0) # publish every 1 second
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Subscriber Node (conceptual)**

```python
# pseudo-code for a simple ROS 2 subscriber node

import rclpy
from std_msgs.msg import String

def listener_callback(msg):
    node.get_logger().info(f'I heard: "{msg.data}"')

def main():
    node = rclpy.create_node('minimal_subscriber')
    subscription = node.create_subscription(String, 'topic', listener_callback, 10)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Service Example: Adder Service

**Service Definition (conceptual - `AddTwoInts.srv`)**

```
int64 a
int64 b
---
int64 sum
```

**Service Server Node (conceptual)**

```python
# pseudo-code for a simple ROS 2 service server node

import rclpy
from example_interfaces.srv import AddTwoInts

def add_two_ints_callback(request, response):
    response.sum = request.a + request.b
    node.get_logger().info(f'Incoming request: a={request.a} b={request.b}')
    node.get_logger().info(f'Sending response: {response.sum}')
    return response

def main():
    node = rclpy.create_node('add_two_ints_server')
    service = node.create_service(AddTwoInts, 'add_two_ints', add_two_ints_callback)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Service Client Node (conceptual)**

```python
# pseudo-code for a simple ROS 2 service client node

import rclpy
from example_interfaces.srv import AddTwoInts

def main():
    node = rclpy.create_node('add_two_ints_client')
    client = node.create_client(AddTwoInts, 'add_two_ints')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('service not available, waiting again...')
    request = AddTwoInts.Request()
    request.a = 2
    request.b = 3
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    if future.result() is not None:
        node.get_logger().info(f'Result of add_two_ints: {future.result().sum}')
    else:
        node.get_logger().error('Service call failed %r' % (future.exception(),))
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Action Example: Fibonacci Action

**Action Definition (conceptual - `Fibonacci.action`)**

```
int64 order
---
int64[] sequence
---
int64[] partial_sequence
```

**Action Server Node (conceptual)**

```python
# pseudo-code for a simple ROS 2 action server node

import rclpy
from rclpy.action import ActionServer
from example_interfaces.action import Fibonacci

def execute_callback(goal_handle):
    node.get_logger().info('Executing goal...')

    sequence = [0, 1]
    for i in range(1, goal_handle.request.order):
        if goal_handle.is_cancel_requested:
            goal_handle.canceled()
            node.get_logger().info('Goal canceled')
            return Fibonacci.Result()
        sequence.append(sequence[i] + sequence[i-1])
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = sequence
        goal_handle.publish_feedback(feedback_msg)
        node.get_logger().info(f'Feedback: {feedback_msg.partial_sequence}')

    goal_handle.succeed()
    result = Fibonacci.Result()
    result.sequence = sequence
    node.get_logger().info(f'Result: {result.sequence}')
    return result

def main():
    node = rclpy.create_node('fibonacci_action_server')
    action_server = ActionServer(
        node, Fibonacci, 'fibonacci', execute_callback
    )
    rclpy.spin(node)
    action_server.destroy()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Action Client Node (conceptual)**

```python
# pseudo-code for a simple ROS 2 action client node

import rclpy
from rclpy.action import ActionClient
from example_interfaces.action import Fibonacci

def feedback_callback(feedback_msg):
    node.get_logger().info(f'Received feedback: {feedback_msg.feedback.partial_sequence}')

def main():
    node = rclpy.create_node('fibonacci_action_client')
    action_client = ActionClient(node, Fibonacci, 'fibonacci')
    while not action_client.wait_for_server(timeout_sec=1.0):
        node.get_logger().info('action server not available, waiting again...')

    goal_msg = Fibonacci.Goal()
    goal_msg.order = 10

    node.get_logger().info('Sending goal...')
    future = action_client.send_goal_async(goal_msg, feedback_callback=feedback_callback)

    rclpy.spin_until_future_complete(node, future)

    goal_handle = future.result()
    if not goal_handle.accepted:
        node.get_logger().error('Goal rejected :(')
        return

    node.get_logger().info('Goal accepted :)')

    result_future = goal_handle.get_result_async()

    rclpy.spin_until_future_complete(node, result_future)

    result = result_future.result().result
    node.get_logger().info(f'Result: {result.sequence}')

    action_client.destroy()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```