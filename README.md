# Traffic Sign and Vehicle Detection using YOLOv8 and OpenCV

## Overview
This script detects traffic signs (pedestrian signals) and vehicles from a video feed using YOLOv8. It also analyzes the color of pedestrian signals (red for "Stop", green for "Walk") and provides voice alerts for both pedestrian signals and large vehicles in the frame.

## Features
- Detects traffic signals and vehicles in a video stream.
- Identifies the color of pedestrian signals using HSV color space.
- Provides real-time voice alerts for traffic signals and nearby vehicles.

## Requirements

To install the required dependencies, run the following command:
```bash
pip install opencv-python ultralytics numpy pyttsx3
