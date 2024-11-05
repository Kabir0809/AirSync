# AirSync: Gaming Controls Using Hand Gestures 🕹️✋
AirSync is an innovative, eco-friendly gaming interface that transforms hand gestures into gaming controls, reducing the need for traditional controllers. Leveraging OpenCV and MediaPipe, AirSync provides a responsive, accessible, and sustainable solution that works with just a webcam. Say goodbye to bulky hardware, and hello to hands-on, immersive gaming!

<!-- Optional: Add a visual demo of your project here -->

## 🌟 Features
- Real-Time Hand Detection: With optimized computer vision techniques, AirSync achieves fast, accurate gesture detection.
- Gesture Customization: Customize gestures to map to various game controls, ensuring flexibility across different gaming styles.
- Eco-Friendly Gaming: Reduces the need for physical controllers, minimizing e-waste.
- Accessibility: Inclusive, adaptive gaming experience that doesn't require specialized hardware.

## 📋 Table of Contents
- Installation
- How It Works
- Usage
- Configuration
- Results
- Future Scope
- Contributing
- License

## 🚀 Installation
To run AirSync, ensure you have Python installed, then follow these steps:

### Clone the repository:
git clone https://github.com/Kabir0809/AirSync.git
cd AirSync

### Install required dependencies:
pip install -r requirements.txt

### Run AirSync:
python main.py
Note: A webcam is required for real-time hand detection.

## ⚙️ How It Works
AirSync operates through a series of modules:

- Video Input: Captures video feed from the webcam.
- Hand Detection: Uses OpenCV for initial image processing and MediaPipe’s hand tracking to identify hand landmarks.
- Gesture Recognition: Maps specific hand gestures to game control actions (e.g., "W," "A," "S," "D").
- Control Output: Sends the control signal to the connected game.
- The processing pipeline is optimized for low latency and high accuracy, running efficiently on most standard devices.

## 🎮 Usage
Once the program is running, your hand gestures will be mapped to the game controls by default. To customize gestures:

- Open the configuration UI (included in the project).
- Select the gesture you’d like to map.
- Assign a control (e.g., "Jump," "Move Left").
Try using different gestures for various in-game actions, creating a personalized setup for each game!

## 🛠️ Configuration
AirSync includes customizable gesture mapping:

- Gestures: Assign gestures to specific game controls.
- Sensitivity: Adjust detection sensitivity based on lighting or environmental factors.
- Profiles: Save custom profiles for various games.
- Configuration can be modified directly through the provided UI.

## 📈 Results
AirSync has been tested across different setups:

- Frame Rate: Consistently over 30 FPS for real-time responsiveness.
- Detection Accuracy: High accuracy in detecting gestures across diverse lighting conditions.
- Latency: Minimal delay, ensuring immediate response to gestures.
- User Feedback: Players noted an enhanced gaming experience and appreciated the eco-friendly approach.

## 🔮 Future Scope
We aim to enhance AirSync by exploring:

- Multi-Platform Compatibility: Expanding support for VR/AR applications.
- Improved Gesture Recognition: Integrating machine learning models for higher precision.
- Environmental Adaptability: Enhancing performance in low-light or cluttered environments

### With AirSync, experience gaming in a whole new way—immersive, accessible, and sustainable!
