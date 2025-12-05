# Chapter 4: Robot Modeling with URDF for Humanoids

This chapter introduces the Unified Robot Description Format (URDF) as a crucial tool for modeling the physical structure and kinematic properties of humanoid robots within the ROS 2 ecosystem. Accurate robot models are essential for simulation, visualization, motion planning, and control.

## 4.1 Introduction to URDF

**URDF (Unified Robot Description Format)** is an XML-based file format used in ROS to describe the kinematic and dynamic properties of a robot. It defines the robot's physical structure, including its links (rigid bodies) and joints (connections between links).

**Why URDF is Important for Humanoids:**

*   **Visualization**: Allows tools like RViz to display the robot's 3D model, its sensor data, and planned motions.
*   **Simulation**: Provides the kinematic and inertial properties needed by physics engines (like Gazebo) to accurately simulate robot behavior.
*   **Motion Planning**: Serves as input for motion planning libraries (e.g., MoveIt) to calculate valid robot trajectories.
*   **Control**: Defines the joint limits and motor properties necessary for controlling the robot's actuators.
*   **Modularity**: Facilitates the description of complex multi-link, multi-joint structures common in humanoids.

## 4.2 Basic URDF Structure

A URDF file primarily consists of `<link>` and `<joint>` elements, nested within a root `<robot>` tag.

```xml
<robot name="my_humanoid_robot">

  <!-- Links: Represent the rigid bodies of the robot (e.g., torso, upper arm, forearm, hand) -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.2 0.4 0.6" />
      </geometry>
      <material name="blue">
        <color rgba="0 0 .8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.2 0.4 0.6" />
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
    </inertial>
  </link>

  <!-- Joints: Define the connections and motion constraints between links -->
  <joint name="head_joint" type="revolute">
    <parent link="base_link"/>
    <child link="head_link"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1.0"/>
  </joint>

  <link name="head_link">
    <visual>
      <geometry>
        <sphere radius="0.1" />
      </geometry>
      <material name="red">
        <color rgba="0.8 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1" />
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Materials can be defined globally or inline -->
  <material name="blue">
    <color rgba="0 0 0.8 1"/>
  </material>
  <material name="red">
    <color rgba="0.8 0 0 1"/>
  </material>

</robot>
```

## 4.3 Key URDF Elements

*   **`<link>`**: Describes a rigid body of the robot. It can contain:
    *   **`<visual>`**: Defines the visual properties (geometry, material, origin) for rendering.
    *   **`<collision>`**: Defines the collision properties (geometry, origin) for physics simulation and collision detection.
    *   **`<inertial>`**: Defines the mass, center of mass, and inertia matrix for accurate physics simulation.
*   **`<joint>`**: Describes the connection between two links. Key attributes include:
    *   `name`: Unique identifier for the joint.
    *   `type`: Type of joint (e.g., `revolute`, `continuous`, `prismatic`, `fixed`, `floating`, `planar`). `revolute` is common for robot arms.
    *   `parent` / `child`: Specify the links connected by the joint.
    *   `origin`: Relative position and orientation of the child link with respect to the parent.
    *   `axis`: The axis of rotation for revolute/continuous joints or translation for prismatic joints.
    *   `limit`: Defines the joint's operational limits (lower/upper position, velocity, effort).

## 4.4 Xacro: Simplifying Complex URDFs

For complex robots like humanoids, writing a single monolithic URDF file can be tedious and error-prone. **Xacro (XML Macros)** is an XML macro language that allows you to use variables, mathematical expressions, and conditional statements to create more modular and readable robot descriptions. Xacro files (`.urdf.xacro`) are processed into standard URDF files before being used by ROS 2 tools.

**Benefits of Xacro:**

*   **Modularity**: Define common components (e.g., a standard finger, a leg segment) as macros and reuse them.
*   **Parameters**: Easily change robot dimensions or properties by modifying variables.
*   **Readability**: Reduces redundancy and makes the robot description easier to understand and maintain.

In the next section, we will explore example URDF snippets tailored for humanoid parts and discuss how they integrate into a complete humanoid robot model.

## 4.5 Example URDF Snippets for Humanoid Parts

Building a full humanoid URDF from scratch can be extensive. Instead, we'll look at modular snippets for common humanoid components (e.g., legs, arms, head) that can be combined using Xacro.

### Example: Humanoid Torso Link and Pelvis Joint

```xml
<!-- Torso Link -->
<link name="torso_link">
  <visual>
    <geometry><box size="0.2 0.3 0.5" /></geometry>
    <material name="grey"/>
  </visual>
  <collision>
    <geometry><box size="0.2 0.3 0.5" /></geometry>
  </collision>
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="20.0"/>
    <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
  </inertial>
</link>

<!-- Pelvis Joint (connecting to a conceptual base_link or main body) -->
<joint name="pelvis_joint" type="fixed">
  <parent link="base_link"/> <!-- Assuming a base_link exists -->
  <child link="torso_link"/>
  <origin xyz="0 0 0.25" rpy="0 0 0"/> <!-- Adjust origin as needed -->
</joint>
```

### Example: Humanoid Upper Leg (Thigh) with Hip Joint

```xml
<!-- Right Hip Roll Joint (Revolute) -->
<joint name="right_hip_roll_joint" type="revolute">
  <parent link="torso_link"/>
  <child link="right_upper_leg_link"/>
  <origin xyz="0 -0.1 0" rpy="0 0 0"/> <!-- Offset from torso, adjust as needed -->
  <axis xyz="1 0 0"/> <!-- Roll around X-axis -->
  <limit lower="-0.5" upper="0.5" effort="100" velocity="1.0"/>
</joint>

<!-- Right Upper Leg Link (Thigh) -->
<link name="right_upper_leg_link">
  <visual>
    <geometry><cylinder radius="0.05" length="0.4" /></geometry>
    <origin xyz="0 0 -0.2" rpy="1.57079632679 0 0"/> <!-- Rotate to be vertical -->
    <material name="light_grey"/>
  </visual>
  <collision>
    <geometry><cylinder radius="0.05" length="0.4" /></geometry>
    <origin xyz="0 0 -0.2" rpy="1.57079632679 0 0"/>
  </collision>
  <inertial>
    <origin xyz="0 0 -0.2" rpy="0 0 0"/>
    <mass value="5.0"/>
    <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.01"/>
  </inertial>
</link>
```

### Example: Humanoid Upper Arm with Shoulder Joint

```xml
<!-- Left Shoulder Pitch Joint (Revolute) -->
<joint name="left_shoulder_pitch_joint" type="revolute">
  <parent link="torso_link"/>
  <child link="left_upper_arm_link"/>
  <origin xyz="0 0.2 0.2" rpy="0 0 0"/> <!-- Offset from torso -->
  <axis xyz="0 1 0"/> <!-- Pitch around Y-axis -->
  <limit lower="-1.57" upper="1.57" effort="50" velocity="0.5"/>
</joint>

<!-- Left Upper Arm Link -->
<link name="left_upper_arm_link">
  <visual>
    <geometry><capsule radius="0.04" length="0.3" /></geometry>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <material name="grey"/>
  </visual>
  <collision>
    <geometry><capsule radius="0.04" length="0.3" /></geometry>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
  </collision>
  <inertial>
    <origin xyz="0 0 0.15" rpy="0 0 0"/>
    <mass value="3.0"/>
    <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.05" iyz="0.0" izz="0.005"/>
  </inertial>
</link>
```

### Example: Humanoid Head Link with Neck Joint

```xml
<!-- Neck Yaw Joint (Revolute) -->
<joint name="neck_yaw_joint" type="revolute">
  <parent link="torso_link"/>
  <child link="head_link"/>
  <origin xyz="0 0 0.25" rpy="0 0 0"/> <!-- Top of torso -->
  <axis xyz="0 0 1"/> <!-- Yaw around Z-axis -->
  <limit lower="-0.78" upper="0.78" effort="20" velocity="0.2"/>
</joint>

<!-- Head Link -->
<link name="head_link">
  <visual>
    <geometry><sphere radius="0.12" /></geometry>
    <material name="white"/>
  </visual>
  <collision>
    <geometry><sphere radius="0.12" /></geometry>
  </collision>
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="2.0"/>
    <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
  </inertial>
</link>
```

## 4.6 URDF and Gazebo Integration (Conceptual)

**Gazebo** is a powerful 3D robot simulator that can accurately simulate complex robotic systems in realistic environments. URDF models serve as the foundation for bringing robots into Gazebo.

### How URDF is Used by Gazebo:

1.  **Robot Description**: Gazebo directly parses the URDF file to understand the robot's links, joints, and their kinematic and inertial properties.
2.  **Visual Representation**: The `<visual>` tags in the URDF are used by Gazebo to render the robot's 3D model in the simulation environment.
3.  **Collision Detection**: The `<collision>` tags define the geometry used by Gazebo's physics engine for collision detection and response.
4.  **Physics Simulation**: The `<inertial>` tags provide mass, center of mass, and inertia information, enabling Gazebo to apply realistic physics (gravity, friction, forces) to the robot.
5.  **Joint Control**: Gazebo integrates with ROS 2 control interfaces (e.g., `ros2_control`) to allow control of the robot's joints based on the limits and dynamics defined in the URDF.

### Adding Gazebo-Specific Elements (Conceptual)

While URDF describes the robot, **Gazebo-specific elements** (often embedded within the URDF using Xacro and a `<gazebo>` tag) are used to define properties that are only relevant to the simulation environment. These include:

*   **Sensors**: Defining virtual sensors like cameras, LiDAR, IMUs, and their properties.
*   **Plugins**: Attaching Gazebo plugins to links or joints to simulate advanced functionalities (e.g., motor control plugins, force/torque sensors).
*   **Materials**: Specifying advanced rendering properties for realistic visuals.
*   **Initial Poses**: Setting the initial position and orientation of the robot in the simulation world.

**Example: Adding a Conceptual Camera Sensor to a Humanoid Head (via Xacro/Gazebo extension)**

```xml
<!-- Inside a .urdf.xacro file, extending the head_link -->
<gazebo reference="head_link">
  <material>Gazebo/White</material>
  <sensor name="head_camera" type="camera">
    <pose>0.1 0 0 0 0 0</pose> <!-- Offset from head_link origin -->
    <visualize>true</visualize>
    <update_rate>30.0</update_rate>
    <camera>
      <horizontal_fov>1.3962634</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.02</near>
        <far>300</far>
      </clip>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros> <!-- ROS 2 specific configuration for the plugin -->
        <namespace>camera</namespace>
        <argument>--ros-args -r __ns:=/head_camera</argument>
        <remap>/image_raw:=image_raw</remap>
        <remap>/camer-info:=camer-info</remap>
      </ros>
      <cameraName>head_camera</cameraName>
      <imageTopicName>image_raw</imageTopicName>
      <cameraInfoTopicName>camer-info</cameraInfoTopicName>
      <frameName>head_camera_frame</frameName>
      <hackBaseline>0.07</hackBaseline>
    </plugin>
  </sensor>
</gazebo>
```

This conceptual example demonstrates how a camera sensor, along with its ROS 2 interface plugin, can be integrated with a URDF-defined `head_link` for use in Gazebo. This modular approach allows for rich simulation without cluttering the base URDF with simulation-specific details.