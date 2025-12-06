# Introduction to ROS 2

## What is ROS 2?

ROS 2 (Robot Operating System 2) is the next generation of the Robot Operating System, a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robotic platforms.

ROS 2 builds upon the lessons learned from ROS 1 and addresses many of its limitations, particularly in the areas of real-time systems, security, and multi-robot systems. The primary goal of ROS 2 is to provide a production-ready framework that can be used in commercial products and safety-critical applications.

## Core Concepts

### Nodes

In ROS 2, a node is a process that performs computation. Nodes communicate with each other by publishing messages to topics, providing and calling services, and getting and setting parameters. A ROS 2 system typically consists of many nodes working together.

Each node should be designed to perform a single, well-defined task. For example, one node might control a laser range-finder, while another node might use that data to build a map of the environment.

### Topics

Topics are named buses over which nodes exchange messages. Nodes can publish messages to a topic or subscribe to a topic to receive messages. Topics are used for continuous data streams like sensor readings, robot state, etc.

The publish-subscribe model allows for loose coupling between nodes. Publishers don't need to know who is listening, and subscribers don't need to know who is publishing.

### Services

Services are another way that nodes can communicate. Unlike topics which provide continuous data streams, services provide a request-reply interaction. A node can offer a service, and other nodes can call that service by sending a request and waiting for a response.

Services are useful for discrete operations that have a defined start and end, like triggering a camera to take a picture or requesting the current configuration of a node.

## Key Features of ROS 2

### Real-Time Support

One of the major improvements in ROS 2 is support for real-time systems. ROS 2 uses DDS (Data Distribution Service) as its middleware, which provides quality-of-service (QoS) settings that can be configured for different use cases, including real-time requirements.

### Security

ROS 2 includes built-in security features based on the DDS Security specification. This includes authentication, encryption, and access control, making it suitable for commercial and industrial applications where security is critical.

### Multi-Robot Systems

ROS 2 was designed with multi-robot systems in mind. It uses DDS discovery mechanisms to allow robots to discover each other on the network automatically, making it easier to coordinate multiple robots working together.

## Installing ROS 2

To install ROS 2, you need a supported platform. ROS 2 is officially supported on Ubuntu Linux, macOS, and Windows. The installation process varies depending on your platform.

For Ubuntu users, you can install ROS 2 using the apt package manager. First, set up your sources and keys, then install the desired ROS 2 distribution.

```bash
sudo apt update && sudo apt install ros-humble-desktop
```

After installation, you need to source the ROS 2 setup file to configure your environment:

```bash
source /opt/ros/humble/setup.bash
```

## Your First ROS 2 Node

Creating a simple ROS 2 node in Python involves importing the ROS 2 Python client library (rclpy), creating a node class, and implementing the necessary callbacks.

```python
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.i += 1
```

This simple example creates a node that publishes a string message to a topic every 0.5 seconds.

## Summary

ROS 2 represents a significant evolution of the ROS framework, addressing the needs of modern robotics applications. Its improved architecture, real-time support, security features, and better support for multi-robot systems make it an excellent choice for both research and commercial robotics projects.

In the next chapters, we will dive deeper into the core concepts of ROS 2 and explore how to build more complex robotic systems using this powerful framework.
