# Chapter 15: Reinforcement Learning & Sim-to-Real

## 15.1 Reinforcement Learning for Humanoid Control

**Reinforcement Learning (RL)** is a powerful paradigm where an agent learns to make optimal decisions by interacting with an environment and receiving rewards or penalties. For complex, high-dimensional control problems like humanoid locomotion and manipulation, RL offers a promising approach to develop highly adaptive and robust behaviors.

### Why RL for Humanoids?

*   **Complex Dynamics**: Humanoid control involves intricate balance, multi-joint coordination, and dynamic stability, which are difficult to model analytically.
*   **Adaptive Behaviors**: RL agents can learn to adapt to new terrains, unexpected disturbances, and varying payloads.
*   **Emergent Skills**: RL can discover novel and efficient locomotion patterns that might not be intuitively designed.
*   **Less Hand-Tuning**: Reduces the need for manual parameter tuning in traditional control.

### Key Components of an RL System

```mermaid
graph LR
    Agent[RL Agent<br/>(Policy, Value Function)] --> Action[Action Space<br/>(Joint Torques, Velocities)]
    Action --> Environment[Environment<br/>(Humanoid Robot, Physics Sim)]
    Environment --> Observation[Observation Space<br/>(Sensor Readings, Joint States)]
    Environment --> Reward[Reward Signal<br/>(Goal Achievement, Stability)]

    Observation --> Agent
    Reward --> Agent

    style Agent fill:#87CEEB
    style Environment fill:#FFE4B5
```

**Figure 15.1**: Fundamental components of a Reinforcement Learning system for robotics.

## 15.2 Designing RL Environments for Humanoids

Creating effective RL environments is crucial for successful training. These environments are typically built in high-fidelity simulators like Isaac Sim or Gazebo.

### 1. Observation Space

What information the agent receives about the environment and itself.

*   **Joint Positions and Velocities**: Current state of all robot joints.
*   **IMU Data**: Linear accelerations and angular velocities (for balance).
*   **End-Effector Poses**: Position and orientation of hands/feet.
*   **Center of Mass (CoM)**: Current CoM position relative to base.
*   **External Sensors**: LiDAR scans, depth camera images (for navigation/perception).
*   **Goal State**: Position of the target or task-specific information.

```python
# Conceptual observation space for a humanoid (Python dictionary)
observation_space = {
    "joint_pos": np.array([...]),    # N joint positions
    "joint_vel": np.array([...]),    # N joint velocities
    "imu_accel": np.array([...]),    # 3D acceleration
    "imu_gyro": np.array([...]),     # 3D angular velocity
    "com_pos_2d": np.array([...]),   # 2D CoM relative to foot
    "target_pos": np.array([...]),   # 3D target position
    # "lidar_scan": np.array([...]), # If navigation is part of task
}
```

### 2. Action Space

How the agent influences the environment (the commands it can send to the robot).

*   **Joint Torques**: Direct control over motor forces (high-fidelity).
*   **Joint Positions/Velocities**: Target positions or velocities for PD controllers (easier to learn).
*   **End-Effector Forces**: For manipulation tasks.
*   **High-Level Commands**: Gait parameters (e.g., step length, frequency) for locomotion.

```python
# Conceptual action space (Python array)
action_space = np.array([...]) # N joint position/velocity targets
```

### 3. Reward Function

Defines the objective of the task. Crucial for guiding the agent's learning.

*   **Task Success**: Positive reward for reaching a goal, picking an object.
*   **Stability**: Penalty for falling, large CoM deviation.
*   **Efficiency**: Penalty for high energy consumption or jerky movements.
*   **Smoothness**: Penalty for rapid changes in joint commands.
*   **Proximity to Goal**: Shaped rewards for getting closer to the target.

```python
# Conceptual reward function
def compute_reward(observation, action, next_observation, done, task_goal):
    reward = 0.0
    # Reward for reaching goal
    dist_to_goal = np.linalg.norm(next_observation["com_pos_2d"] - task_goal)
    reward += 1.0 / (1.0 + dist_to_goal) # Shaped reward

    # Penalty for falling
    if done and robot_is_fallen(next_observation):
        reward -= 100.0

    # Penalty for high torque (energy efficiency)
    reward -= 0.01 * np.sum(np.square(action))

    return reward
```

### 4. Episode Termination Conditions

When a training episode ends.

*   **Task Completion**: Goal reached.
*   **Failure**: Robot falls, collides with critical obstacle.
*   **Time Limit**: Maximum number of simulation steps reached.

## 15.3 Domain Randomization for Sim-to-Real Transfer

**Domain randomization** is a powerful technique used in RL to bridge the **sim-to-real gap**. By randomly varying non-essential simulation parameters during training, the agent is forced to learn a policy that is robust to variations, making it more likely to generalize to the real world.

### Why Domain Randomization is Essential for Humanoids

*   **Unmodeled Real-World Effects**: Accounts for small discrepancies between simulated and real physics (e.g., slight differences in joint friction, sensor noise).
*   **Robustness**: Trains agents to perform well despite unknown real-world conditions.
*   **Reduces Fine-Tuning**: Minimizes the need for extensive real-world parameter tuning.

### Randomizable Parameters in Isaac Sim

Isaac Sim provides extensive support for domain randomization, allowing variation of:

1.  **Physics Parameters**: Mass, friction coefficients, joint damping, spring stiffness.
2.  **Visual Properties**: Textures, colors, lighting, material properties, background environments.
3.  **Sensor Properties**: Camera noise, LiDAR dropout, IMU bias and drift.
4.  **External Forces**: Random pushes or pulls on the robot.

```python
# Isaac Sim Python: Example of domain randomization setup for an RL environment
from omni.isaac.core.articulations import ArticulationView
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.torch.maths import quat_apply_yaw
import random
import torch

class HumanoidEnv:
    def __init__(self, world):
        self.world = world
        self.asset_root_path = get_assets_root_path()

        # Load robot
        self.robot = world.scene.add_asset(
            asset_path=os.path.join(self.asset_root_path, "Isaac/Robots/Franka/franka_alt_fingers.usd"), # Placeholder
            prim_path="/World/Humanoid",
            position=torch.tensor([0.0, 0.0, 1.0])
        )

        # Define randomizable ranges
        self.friction_range = [0.5, 1.5]
        self.mass_scale_range = [0.8, 1.2]
        self.light_intensity_range = [500, 2000]

    def randomize_env(self):
        # Randomize friction
        friction = random.uniform(*self.friction_range)
        # Apply friction to ground plane or robot feet (conceptual)
        # self.world.scene.get_default_ground_plane().set_friction(friction)

        # Randomize robot mass
        mass_scale = random.uniform(*self.mass_scale_range)
        # Apply mass scale to robot links (conceptual)
        # self.robot.apply_mass_scale(mass_scale)

        # Randomize lighting
        light_intensity = random.uniform(*self.light_intensity_range)
        # self.world.scene.get_light("/World/defaultLight").set_intensity(light_intensity)

        # Randomize textures/materials (conceptual)
        # ...

    def post_reset(self):
        self.randomize_env()
        # Reset robot to initial state with randomization applied
        # ...
```

### Randomization Workflow for RL Training

```mermaid
flowchart TD
    Start[RL Training Start] --> EpisodeInit[Initialize Episode]
    EpisodeInit --> Randomize[Apply Domain Randomization<br/>(Physics, Visuals, Sensors)]
    Randomize --> Observe[Agent Observes State]
    Observe --> Decide[Agent Decides Action]
    Decide --> Act[Robot Acts in Sim]
    Act --> Simulate[Simulate Physics Step]
    Simulate --> Reward[Compute Reward]
    Reward --> Done{Episode Done?}
    Done -->|No| Observe
    Done -->|Yes| NextEpisode[Next Episode]
    NextEpisode -->|If not max episodes| EpisodeInit
    NextEpisode --> Finish[Training Finished]

    style Randomize fill:#90EE90
    style Simulate fill:#FFE4B5
```

**Figure 15.2**: RL training loop with integrated domain randomization.

## 15.4 Sim-to-Real Transfer Techniques

Successful sim-to-real transfer is the ultimate goal of training humanoid robots in simulation. Beyond domain randomization, several other techniques enhance this process.

### 1. System Identification

Accurately identifying the physical parameters of the real robot (mass, inertia, friction, joint compliance) and matching them in simulation reduces the sim-to-real gap.

### 2. Dynamics Randomization

Explicitly randomizing dynamic parameters (masses, inertias, friction) during training. This is a subset of domain randomization focused on physics.

### 3. Reality Gap Minimization

*   **High-Fidelity Simulators**: Using physically accurate simulators (Isaac Sim, MuJoCo).
*   **Accurate Sensor Models**: Matching real-world sensor noise and characteristics.
*   **Teleoperation**: Using a human to control the simulated robot to generate realistic interaction data.

### 4. Transfer Learning and Fine-Tuning

Train a policy fully in simulation, then fine-tune it with limited real-world data.

```mermaid
graph LR
    SimTrain[RL Training in Simulation<br/>(Domain Randomization)] --> PolicySim[Trained Policy (Sim)]
    PolicySim --> RealDeploy[Deploy Policy to Real Robot]
    RealDeploy --> RealCollect[Collect Real-World Data]
    RealCollect --> FineTune[Fine-tune Policy<br/>(Limited Real Data)]
    FineTune --> PolicyReal[Optimized Policy (Real)]

    style SimTrain fill:#87CEEB
    style RealDeploy fill:#FFE4B5
    style FineTune fill:#90EE90
```

**Figure 15.3**: Sim-to-real transfer workflow using fine-tuning.

### 5. Adversarial Training

Train a discriminator to distinguish between real and simulated data, forcing the simulator to generate more realistic data or the policy to become more robust.

## 15.5 Case Study: Learning Humanoid Locomotion

### Environment

*   **Simulator**: Isaac Sim (high-fidelity physics)
*   **Robot**: Humanoid model (e.g., NVIDIA's digit or unitree H1-like)
*   **Observation**: Joint positions/velocities, IMU (accel, gyro), CoM, foot contact states.
*   **Action**: Joint position targets (PD controlled).
*   **Reward**: Forward velocity, minimal joint effort, maintaining balance, penalty for falling.
*   **Randomization**: Randomize ground friction, link masses, joint damping, external forces.

### Training Process

1.  **Initial Policy**: Start with a simple walking gait or random policy.
2.  **Iterative Training**: Millions of simulation steps over thousands of episodes.
3.  **Progressive Difficulty**: Gradually increase terrain complexity (flat -> uneven -> stairs).
4.  **Domain Randomization**: Applied at the start of each episode.
5.  **RL Algorithm**: Proximal Policy Optimization (PPO) or Soft Actor-Critic (SAC) commonly used.

### Results

*   Emergent, natural-looking gaits.
*   Robustness to various terrains and external pushes.
*   Successful transfer to a physical humanoid robot with minimal fine-tuning.

## 15.6 Challenges and Future Directions

### Challenges

*   **Computational Cost**: Training complex humanoid policies requires significant GPU resources and time.
*   **Reward Engineering**: Designing effective reward functions is non-trivial.
*   **Exploration**: Humanoids have high-dimensional action spaces, making exploration challenging.
*   **Safety in Real World**: Ensuring learned policies are safe for physical deployment.
*   **Long-Horizon Planning**: Integrating RL with high-level cognitive planning.

### Future Directions

*   **Foundation Models for Robotics**: Pre-training large models on massive datasets.
*   **Human-in-the-Loop RL**: Incorporating human feedback during training.
*   **Offline RL**: Learning from existing datasets without direct environment interaction.
*   **Multi-Agent RL**: Coordination of multiple humanoids or robots.
*   **Continual Learning**: Humanoids learning new skills throughout their lifetime.

## Summary

Reinforcement Learning, coupled with advanced simulation platforms like Isaac Sim and techniques like domain randomization, is revolutionizing humanoid robot control. By enabling agents to learn complex, adaptive behaviors from interaction, RL offers a powerful path to overcome the limitations of traditional control methods. Key takeaways:

*   **RL is ideal for high-dimensional, dynamic control problems** inherent in humanoids.
*   **Careful design of observation space, action space, and reward functions** is crucial.
*   **Domain randomization is indispensable for bridging the sim-to-real gap**.
*   **Sim-to-real transfer is enhanced** by system identification, dynamics randomization, and fine-tuning.

As simulation fidelity increases and RL algorithms become more efficient, we are closer than ever to developing truly autonomous and intelligent humanoid robots that can operate robustly in the real world. This module has laid the foundation for understanding how these powerful tools come together to create the "AI-Robot Brain."

## Further Reading

*   [NVIDIA Isaac Gym (RL with Isaac Sim)](https://docs.omniverse.nvidia.com/app_isaacsim/4.0/isaac_gym/index.html)
*   [OpenAI Spinning Up in Deep RL](https://spinningup.openai.com/en/latest/)
*   S. Levine, P. Pastor, A. Krizhevsky, H. Ibarz, and M. Abbeel, "Learning Contact-Rich Manipulation Skills with Guided Policy Search," *arXiv:1603.00371*, 2016.
*   J. Hwang and J. J. Choi, "Deep Reinforcement Learning for Humanoid Robot Locomotion with Footstep Planning," *Robotics and Autonomous Systems*, 2021.
