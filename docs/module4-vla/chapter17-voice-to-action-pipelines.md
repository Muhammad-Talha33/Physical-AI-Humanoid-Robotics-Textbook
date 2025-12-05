# Chapter 17: Voice-to-Action Pipelines (Whisper)

## 17.1 The Role of Speech in Human-Robot Interaction

**Speech** is the most natural form of human communication, making it a critical modality for intuitive human-robot interaction (HRI). For humanoid robots, enabling them to understand and respond to spoken commands allows for:

*   **Intuitive Control**: Users can issue commands without physical interfaces.
*   **Accessibility**: Provides an alternative input for users with limited mobility.
*   **Contextual Understanding**: Spoken language often contains rich contextual cues.
*   **Multitasking**: Humans can issue commands while performing other tasks.

### Challenges of Speech-Based HRI

*   **Noise**: Background noise can degrade speech recognition accuracy.
*   **Accents and Variations**: Diverse speech patterns make robust recognition difficult.
*   **Ambiguity**: Spoken language can be ambiguous and require clarification.
*   **Real-time Processing**: Speech-to-text and command parsing must happen quickly.

## 17.2 OpenAI Whisper: State-of-the-Art Speech Recognition

**OpenAI Whisper** is a powerful, open-source automatic speech recognition (ASR) system trained on a massive dataset of diverse audio and text. Its key features make it highly suitable for robotics applications:

*   **High Accuracy**: Achieves state-of-the-art performance across various languages and acoustic conditions.
*   **Robustness**: Handles background noise, accents, and different speaking styles well.
*   **Multilingual**: Supports transcription in many languages and translation to English.
*   **Open Source**: Freely available for research and commercial use.
*   **Versatility**: Can be used for transcription, language identification, and translation.

### Whisper Architecture (High-Level)

```mermaid
graph LR
    AudioInput[Audio Input<br/>(Robot Microphone)] --> Preprocessing[Audio Preprocessing<br/>(Spectrogram)]
    Preprocessing --> Encoder[Encoder<br/>(Transformer Blocks)]
    Encoder --> Decoder[Decoder<br/>(Transformer Blocks)]
    Decoder --> Output[Text Output<br/>(Transcription)]

    style Encoder fill:#FFE4B5
    style Decoder fill:#87CEEB
```

**Figure 17.1**: High-level architecture of the OpenAI Whisper model.

### Whisper Models and Sizes

| Model | Parameters | VRAM (fp16) | Relative Speed | Use Case |
|-------|------------|-------------|----------------|----------|
| `tiny`  | 39M        | ~1GB        | ~32x           | Fast, low-resource |
| `base`  | 74M        | ~1GB        | ~16x           | General-purpose |
| `small` | 244M       | ~2GB        | ~6x            | Balanced performance |
| `medium`| 769M       | ~5GB        | ~2x            | High accuracy |
| `large` | 1550M      | ~10GB       | 1x             | Highest accuracy, slow |

**For Robotics**: `base` or `small` models offer a good balance of speed and accuracy, suitable for real-time processing on embedded systems (e.g., NVIDIA Jetson).

## 17.3 Integrating Whisper into a ROS 2 Pipeline

To integrate Whisper into a humanoid robot's VLA pipeline, we need to connect the robot's audio input to the Whisper ASR system and then pass the transcribed text to a Natural Language Understanding (NLU) module.

### 1. Audio Acquisition (ROS 2 `audio_common`)

ROS 2 `audio_common` provides packages for capturing audio from microphones and publishing it as ROS 2 messages.

```python
# Conceptual ROS 2 launch for audio acquisition
import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_audio_launch_description():
    return LaunchDescription([
        Node(
            package='audio_capture',
            executable='audio_capture',
            name='robot_mic_capture',
            parameters=[
                {'sample_rate': 16000},
                {'channels': 1},
                {'format': 'S16LE'},
                {'topic_name': '/audio/raw'},
            ],
            output='screen',
        )
    ])
```

### 2. Whisper ROS 2 Node

A custom ROS 2 node can subscribe to the raw audio, process it with Whisper, and publish the transcribed text.

```python
import rclpy
from rclpy.node import Node
from audio_common_msgs.msg import AudioData # Or similar raw audio message
from std_msgs.msg import String
import whisper
import numpy as np

class WhisperASRNode(Node):
    def __init__(self):
        super().__init__('whisper_asr_node')
        self.subscription = self.create_subscription(
            AudioData,
            '/audio/raw',
            self.audio_callback,
            10 # QoS history depth
        )
        self.publisher = self.create_publisher(String, '/speech/transcribed_text', 10)
        self.model = whisper.load_model("base") # Load Whisper model
        self.audio_buffer = []

    def audio_callback(self, msg):
        # Accumulate audio data
        self.audio_buffer.extend(np.frombuffer(msg.data, dtype=np.int16))

        # Process audio in chunks (e.g., every 5 seconds or when silence detected)
        if len(self.audio_buffer) > 16000 * 5: # 5 seconds of 16kHz audio
            audio_segment = np.array(self.audio_buffer[-16000*5:], dtype=np.float32) / 32768.0
            result = self.model.transcribe(audio_segment)
            transcribed_text = result["text"]

            if transcribed_text.strip(): # Publish non-empty transcriptions
                self.get_logger().info(f'Transcribed: "{transcribed_text}"')
                string_msg = String()
                string_msg.data = transcribed_text
                self.publisher.publish(string_msg)
            self.audio_buffer = [] # Clear buffer or keep only last segment

def main(args=None):
    rclpy.init(args=args)
    node = WhisperASRNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 3. Speech Recognition to Command Parsing

The transcribed text from Whisper needs to be parsed into actionable robot commands. This is where Natural Language Understanding (NLU) comes in, often using another LLM or a rule-based system.

```mermaid
graph LR
    Mic[Robot Microphone] --> AudioCapture[ROS 2: /audio/raw]
    AudioCapture --> WhisperNode[Whisper ASR Node] --> TranscribedText[ROS 2: /speech/transcribed_text]
    TranscribedText --> NLUModule[NLU Module<br/>(LLM / Rule-Based Parser)] --> RobotCommand[Robot Action Command]
    RobotCommand --> RobotControl[Humanoid Control System]

    style WhisperNode fill:#87CEEB
    style NLUModule fill:#FFE4B5
```

**Figure 17.2**: Voice-to-action pipeline using Whisper and an NLU module.

## 17.4 Designing for Robust Command Parsing

### 1. Intent Recognition

Identifying the user's goal (e.g., "move", "grasp", "answer").

```python
# Example: Simple intent recognition using keywords
def get_intent(text):
    text = text.lower()
    if "move" in text or "go to" in text:
        return "MOVE"
    elif "pick up" in text or "grasp" in text:
        return "GRASP"
    elif "what is" in text or "tell me" in text:
        return "QUERY"
    return "UNKNOWN"
```

### 2. Entity Extraction

Extracting key information (objects, locations, parameters) from the command.

*   **Objects**: "the red cup", "my phone"
*   **Locations**: "on the table", "to the kitchen"
*   **Quantities**: "two steps forward", "turn 90 degrees"

LLMs are particularly effective at entity extraction due to their contextual understanding.

### 3. Context Management

Maintaining a dialogue history to resolve co-references (e.g., "that one" referring to a previously mentioned object) and ambiguous commands.

*   **Dialogue State**: Track previous commands and robot actions.
*   **Visual Grounding**: Use visual perception to clarify ambiguous references (e.g., if multiple "red cups" are present).

### 4. Disambiguation Strategies

When a command is unclear, the robot needs to ask clarifying questions.

*   "Which red cup do you mean? The one on the left or the one on the right?"
*   "Do you want me to pick it up or push it?"

## 17.5 Best Practices for Voice-to-Action Pipelines

1.  **Optimize Whisper Model**: Choose an appropriate Whisper model size for your robot's computational resources (e.g., `base` or `small` on Jetson).
2.  **Noise Reduction**: Implement audio pre-processing techniques (e.g., noise suppression, echo cancellation) to improve Whisper accuracy.
3.  **Silence Detection**: Use voice activity detection (VAD) to segment audio and trigger transcription only when speech is present.
4.  **Custom Vocabulary**: Fine-tune Whisper or use custom dictionaries for domain-specific terms (e.g., robot part names, tool names).
5.  **Robust NLU**: Combine LLMs with rule-based parsers for reliable intent and entity extraction.
6.  **Error Handling**: Design the pipeline to gracefully handle misinterpretations, ask for clarification, or provide alternative suggestions.
7.  **Feedback**: Provide audio or visual feedback to the user on command reception and execution status.

## Summary

The voice-to-action pipeline, spearheaded by state-of-the-art speech recognition systems like OpenAI Whisper, is a fundamental component of Vision-Language-Action (VLA) for humanoid robots. It enables natural and intuitive human-robot interaction by:

*   **Accurately converting spoken commands to text** with Whisper's robust ASR capabilities.
*   **Parsing text commands into actionable robot instructions** through intent recognition and entity extraction.
*   **Managing context and disambiguating ambiguous language** using NLU modules.

Integrating Whisper into a ROS 2 pipeline, coupled with careful design for robust command parsing, allows humanoid robots to move beyond pre-programmed behaviors and respond dynamically to human instructions. This capability is crucial for empowering humanoids to operate effectively and collaboratively in complex, real-world environments.

In the next chapter, we will delve into the powerful role of Large Language Models (LLMs) in the cognitive planning stage, exploring how they enable robots to decompose tasks, reason about the environment, and handle complex constraints to achieve high-level goals.

## Further Reading

*   [OpenAI Whisper GitHub Repository](https://github.com/openai/whisper)
*   [ROS 2 `audio_common` Documentation](https://github.com/ros-drivers/audio_common)
*   [Human-Robot Interaction: A Review](https://www.annualreviews.org/doi/abs/10.1146/annurev-control-053018-023700)
