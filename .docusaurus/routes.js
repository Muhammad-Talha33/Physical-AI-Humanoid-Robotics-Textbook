import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', 'a94'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '080'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '630'),
            routes: [
              {
                path: '/docs/',
                component: ComponentCreator('/docs/', '4a8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module1-ros2/chapter1-introduction-to-ros2',
                component: ComponentCreator('/docs/module1-ros2/chapter1-introduction-to-ros2', '0c0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module1-ros2/chapter2-ros2-core-concepts',
                component: ComponentCreator('/docs/module1-ros2/chapter2-ros2-core-concepts', 'b15'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module1-ros2/chapter3-ros2-in-python',
                component: ComponentCreator('/docs/module1-ros2/chapter3-ros2-in-python', '6a2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module1-ros2/chapter4-robot-modeling-urdf',
                component: ComponentCreator('/docs/module1-ros2/chapter4-robot-modeling-urdf', '7b1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module1-ros2/chapter5-sensor-integration',
                component: ComponentCreator('/docs/module1-ros2/chapter5-sensor-integration', '23d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module2-digital-twin/chapter10-building-realistic-environments',
                component: ComponentCreator('/docs/module2-digital-twin/chapter10-building-realistic-environments', '45b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module2-digital-twin/chapter6-introduction-to-digital-twins',
                component: ComponentCreator('/docs/module2-digital-twin/chapter6-introduction-to-digital-twins', 'b32'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module2-digital-twin/chapter7-gazebo-simulation-fundamentals',
                component: ComponentCreator('/docs/module2-digital-twin/chapter7-gazebo-simulation-fundamentals', '605'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module2-digital-twin/chapter8-simulated-sensors-gazebo',
                component: ComponentCreator('/docs/module2-digital-twin/chapter8-simulated-sensors-gazebo', 'bfd'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module2-digital-twin/chapter9-unity-visualization-robotics',
                component: ComponentCreator('/docs/module2-digital-twin/chapter9-unity-visualization-robotics', 'e2a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module3-ai-robot-brain/chapter11-introduction-nvidia-isaac',
                component: ComponentCreator('/docs/module3-ai-robot-brain/chapter11-introduction-nvidia-isaac', 'b15'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module3-ai-robot-brain/chapter12-perception-pipelines-isaac-sim',
                component: ComponentCreator('/docs/module3-ai-robot-brain/chapter12-perception-pipelines-isaac-sim', '5c7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module3-ai-robot-brain/chapter13-isaac-ros-accelerated-perception',
                component: ComponentCreator('/docs/module3-ai-robot-brain/chapter13-isaac-ros-accelerated-perception', 'dd7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module3-ai-robot-brain/chapter14-navigation-nav2',
                component: ComponentCreator('/docs/module3-ai-robot-brain/chapter14-navigation-nav2', '569'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module3-ai-robot-brain/chapter15-reinforcement-learning-sim-to-real',
                component: ComponentCreator('/docs/module3-ai-robot-brain/chapter15-reinforcement-learning-sim-to-real', 'd22'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module4-vla/chapter16-introduction-to-vla',
                component: ComponentCreator('/docs/module4-vla/chapter16-introduction-to-vla', '574'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module4-vla/chapter17-voice-to-action-pipelines',
                component: ComponentCreator('/docs/module4-vla/chapter17-voice-to-action-pipelines', '131'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module4-vla/chapter18-llm-based-cognitive-planning',
                component: ComponentCreator('/docs/module4-vla/chapter18-llm-based-cognitive-planning', '0e8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module4-vla/chapter19-multimodal-interaction',
                component: ComponentCreator('/docs/module4-vla/chapter19-multimodal-interaction', '06a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module4-vla/chapter20-capstone-autonomous-humanoid',
                component: ComponentCreator('/docs/module4-vla/chapter20-capstone-autonomous-humanoid', '185'),
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
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
