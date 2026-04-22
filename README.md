# Ball Detection System Using Stationary Robot with Webots and OpenCV

## Overview

This project implements a vision-based system that detects and localizes red and green balls using a **stationary robot** equipped with a camera in the Webots simulation environment. The robot remains completely still while colored balls are manually moved into its field of view. Once a ball enters the camera frame, the system identifies its color and calculates its position in real-time. The robot does not move toward or track the ball.

## Features

- Real-time red and green ball detection
- Ball localization using centroid calculation
- HSV color space conversion for robust detection under varying lighting
- Robot remains stationary (no movement)
- Manual ball movement for controlled testing
- Webots simulation environment (no physical hardware required)
- Python implementation with OpenCV

## Tools and Technologies

| Tool | Purpose |
|------|---------|
| Python | Primary programming language |
| Webots | Robotics simulation environment |
| OpenCV | Image processing and color detection |
| NumPy | Array manipulation |

## Project Structure
BallDetection_Project/
├── controllers/
│ └── ball_detector_controller/
│ └── ball_detector_controller.py
├── worlds/
│ └── BallDetection1.wbt
├── README.md
---


## How It Works

1. A stationary robot with a forward-facing RGB camera is placed in a Webots world
2. The robot's motors are set to velocity 0, ensuring it never moves
3. Red and green balls are placed in the scene
4. The user manually drags balls into the camera's field of view
5. The Python controller continuously captures images from the camera
6. Each image is converted from RGB to HSV color space
7. Hue ranges for red (0-10, 160-179) and green (40-80) are applied to create binary masks
8. Contour detection identifies the largest ball-shaped region
9. Centroid calculation localizes the ball's position in the image frame
10. The console outputs the ball color and coordinates

## Algorithms Used

| Algorithm | Purpose |
|-----------|---------|
| HSV Color Space Conversion | Isolate ball colors from lighting variations |
| Contour Detection | Identify ball-shaped regions |
| Ball Localization | Calculate centroid coordinates |
| Color Classification | Distinguish between red and green |
| Morphological Filtering | Remove noise from binary masks |

## Setup Instructions

### Prerequisites

- Webots (Download from [cyberbotics.com](https://cyberbotics.com))
- Python 3.7 or higher
- OpenCV and NumPy installed

### Installation

1. Install Webots on your system

2. Install required Python packages:
```bash
pip install opencv-python numpy
