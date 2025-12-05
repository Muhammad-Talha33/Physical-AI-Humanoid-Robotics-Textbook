import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/Physical-AI-Humanoid-Robotics-Textbook/markdown-page',
    component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/markdown-page', '9ba'),
    exact: true
  },
  {
    path: '/Physical-AI-Humanoid-Robotics-Textbook/docs',
    component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs', 'e78'),
    routes: [
      {
        path: '/Physical-AI-Humanoid-Robotics-Textbook/docs',
        component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs', '48b'),
        routes: [
          {
            path: '/Physical-AI-Humanoid-Robotics-Textbook/docs',
            component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs', 'dbe'),
            routes: [
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/', '63d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter1-introduction-to-ros2',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter1-introduction-to-ros2', '1c9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter2-ros2-core-concepts',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter2-ros2-core-concepts', 'b3e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter3-ros2-in-python',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter3-ros2-in-python', 'f58'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter4-robot-modeling-urdf',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter4-robot-modeling-urdf', '7b6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter5-sensor-integration',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module1-ros2/chapter5-sensor-integration', '5d0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter10-building-realistic-environments',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter10-building-realistic-environments', '934'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter6-introduction-to-digital-twins',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter6-introduction-to-digital-twins', '5ae'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter7-gazebo-simulation-fundamentals',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter7-gazebo-simulation-fundamentals', '933'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter8-simulated-sensors-gazebo',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter8-simulated-sensors-gazebo', '947'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter9-unity-visualization-robotics',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module2-digital-twin/chapter9-unity-visualization-robotics', 'f72'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter11-introduction-nvidia-isaac',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter11-introduction-nvidia-isaac', 'aa5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter12-perception-pipelines-isaac-sim',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter12-perception-pipelines-isaac-sim', 'f74'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter13-isaac-ros-accelerated-perception',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter13-isaac-ros-accelerated-perception', '4d1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter14-navigation-nav2',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter14-navigation-nav2', '426'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter15-reinforcement-learning-sim-to-real',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module3-ai-robot-brain/chapter15-reinforcement-learning-sim-to-real', '7f3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter16-introduction-to-vla',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter16-introduction-to-vla', 'f75'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter17-voice-to-action-pipelines',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter17-voice-to-action-pipelines', 'a5d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter18-llm-based-cognitive-planning',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter18-llm-based-cognitive-planning', '87d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter19-multimodal-interaction',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter19-multimodal-interaction', '0dc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter20-capstone-autonomous-humanoid',
                component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/docs/module4-vla/chapter20-capstone-autonomous-humanoid', 'b83'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/Physical-AI-Humanoid-Robotics-Textbook/',
    component: ComponentCreator('/Physical-AI-Humanoid-Robotics-Textbook/', '637'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
