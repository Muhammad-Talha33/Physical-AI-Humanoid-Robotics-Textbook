import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  emoji: string;
  description: ReactNode;
  link: string;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Module 1: The Robotic Nervous System (ROS 2)',
    emoji: '🤖',
    description: (
      <>
        Learn the foundation of robot communication with ROS 2. Master nodes, topics,
        services, URDF modeling, and sensor integration to build the nervous system
        that powers humanoid robots.
      </>
    ),
    link: '/docs/module1-ros2/chapter1-introduction-to-ros2',
  },
  {
    title: 'Module 2: The Digital Twin (Gazebo + Unity)',
    emoji: '🌐',
    description: (
      <>
        Create realistic simulations of humanoid robots using Gazebo and Unity.
        Learn physics-based modeling, sensor simulation, and visualization techniques
        for testing before deployment.
      </>
    ),
    link: '/docs/module2-digital-twin/chapter6-introduction-to-digital-twins',
  },
  {
    title: 'Module 3: The AI-Robot Brain (NVIDIA Isaac)',
    emoji: '🧠',
    description: (
      <>
        Harness the power of NVIDIA Isaac Sim and Isaac ROS for advanced perception,
        navigation, and reinforcement learning. Master sim-to-real transfer and
        accelerated AI pipelines.
      </>
    ),
    link: '/docs/module3-ai-robot-brain/chapter11-introduction-nvidia-isaac',
  },
  {
    title: 'Module 4: Vision-Language-Action (VLA)',
    emoji: '💬',
    description: (
      <>
        Bring it all together with multimodal AI. Learn how LLMs, computer vision,
        and voice interfaces enable natural human-robot interaction and autonomous
        task execution.
      </>
    ),
    link: '/docs/module4-vla/chapter16-introduction-to-vla',
  },
];

function Feature({title, emoji, description, link}: FeatureItem) {
  return (
    <div className={clsx('col col--6')} style={{ marginBottom: '2rem' }}>
      <div className="text--center">
        <span style={{ fontSize: '4rem' }} role="img" aria-label={title}>
          {emoji}
        </span>
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
        <a href={link} className="button button--primary button--md">
          Start Reading →
        </a>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
