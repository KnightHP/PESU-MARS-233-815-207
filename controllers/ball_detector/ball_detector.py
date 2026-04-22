"""
Ball Detection System for Stationary Robot using Webots and OpenCV
The robot does NOT move. It only detects red or green balls when they
are manually moved into the camera's field of view.
"""

from controller import Robot
import cv2
import numpy as np
import sys

# ============================================================================
# INITIALIZATION
# ============================================================================

# Create robot instance
robot = Robot()

# Get timestep (simulation step duration in milliseconds)
timestep = int(robot.getBasicTimeStep())

# Initialize camera
camera = robot.getDevice("camera")
if camera is None:
    print("ERROR: Camera device not found. Please check your robot configuration.")
    sys.exit(1)

camera.enable(timestep)

# Get camera dimensions
camera_width = camera.getWidth()
camera_height = camera.getHeight()
camera_center = camera_width // 2

# Get motors (but we will NOT use them - robot remains stationary)
# Motors are obtained only to ensure they exist, but velocities are set to 0
try:
    left_motor = robot.getDevice("left wheel motor")
    right_motor = robot.getDevice("right wheel motor")
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)   # Stationary
    right_motor.setVelocity(0.0)  # Stationary
    print("Motors initialized and set to stationary mode (velocity = 0)")
except:
    print("Note: Motors not found - robot may have different motor names")
    print("Robot will remain stationary by default")

print("=" * 55)
print("BALL DETECTION SYSTEM - STATIONARY ROBOT")
print("=" * 55)
print(f"Camera Resolution: {camera_width} x {camera_height}")
print(f"Camera Center: {camera_center}")
print("Robot is STATIONARY. It will NOT move.")
print("Manually move red or green balls into the camera's field of view.")
print("=" * 55)

# ============================================================================
# BALL DETECTION FUNCTION
# ============================================================================

def detect_ball(frame):
    """
    Detect red or green ball in the given image frame.
    
    Parameters:
        frame: BGR image from the robot's camera
    
    Returns:
        color: String indicating "red", "green", or None
        center_x: X-coordinate of ball centroid (pixels)
        center_y: Y-coordinate of ball centroid (pixels)
        area: Area of detected ball contour (pixels)
    """
    
    # Convert BGR to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # ----- RED BALL DETECTION -----
    # Red color wraps around the hue spectrum (0-10 and 160-179)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    
    # ----- GREEN BALL DETECTION -----
    # Green color range (40-80 on hue wheel)
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # Combine masks
    mask_combined = cv2.bitwise_or(mask_red, mask_green)
    
    # Apply morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    mask_cleaned = cv2.morphologyEx(mask_combined, cv2.MORPH_OPEN, kernel)
    mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest contour (most likely the ball)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Minimum area threshold to filter out noise
        MIN_AREA_THRESHOLD = 100
        
        if area > MIN_AREA_THRESHOLD:
            # Calculate centroid using image moments
            M = cv2.moments(largest_contour)
            
            if M["m00"] != 0:
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])
                
                # Determine color by checking which mask had the contour
                if center_y < mask_red.shape[0] and center_x < mask_red.shape[1]:
                    if mask_red[center_y, center_x] > 0:
                        color = "red"
                    elif mask_green[center_y, center_x] > 0:
                        color = "green"
                    else:
                        # Fallback: check average around centroid
                        roi_size = 5
                        y_start = max(0, center_y - roi_size)
                        y_end = min(mask_red.shape[0], center_y + roi_size)
                        x_start = max(0, center_x - roi_size)
                        x_end = min(mask_red.shape[1], center_x + roi_size)
                        
                        red_roi = mask_red[y_start:y_end, x_start:x_end]
                        green_roi = mask_green[y_start:y_end, x_start:x_end]
                        
                        if np.sum(red_roi) > np.sum(green_roi):
                            color = "red"
                        else:
                            color = "green"
                    
                    return color, center_x, center_y, area
        
        return None, None, None, None
    
    return None, None, None, None

# ============================================================================
# MAIN CONTROL LOOP (ROBOT DOES NOT MOVE)
# ============================================================================

detection_count = 0
frame_count = 0
last_detection_frame = 0

# Ensure robot is stationary (set velocities to 0 periodically)
try:
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)
except:
    pass

print("\nSystem ready. Waiting for ball detection...\n")

while robot.step(timestep) != -1:
    frame_count += 1
    
    # Keep robot stationary (redundant safety check)
    try:
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
    except:
        pass
    
    # Get image from camera
    image = camera.getImage()
    
    if image:
        # Convert Webots image to NumPy array
        img_array = np.frombuffer(image, dtype=np.uint8).reshape(camera_height, camera_width, 4)
        
        # Convert BGRA (Webots format) to BGR (OpenCV format)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
        
        # Detect ball in the current frame
        color, center_x, center_y, area = detect_ball(img_bgr)
        
        # Display result when ball is detected
        if color is not None:
            # Avoid duplicate detections of the same ball (cooldown)
            if frame_count - last_detection_frame > 30:
                detection_count += 1
                last_detection_frame = frame_count
                
                # Determine horizontal position relative to camera center
                if center_x < camera_center - 50:
                    position_text = "LEFT"
                elif center_x > camera_center + 50:
                    position_text = "RIGHT"
                else:
                    position_text = "CENTER"
                
                print("=" * 50)
                print(f"[DETECTION #{detection_count}]")
                print(f"  Color: {color.upper()}")
                print(f"  Position: X={center_x}, Y={center_y} ({position_text})")
                print(f"  Area: {area:.0f} pixels")
                print("=" * 50)
            
        else:
            # Optional: Print status periodically (every 500 frames)
            if frame_count % 500 == 0:
                print(f"[Status] Frame {frame_count}: No ball detected. Robot stationary.")

# ============================================================================
# SIMULATION ENDED
# ============================================================================

print("\n" + "=" * 55)
print(f"SIMULATION ENDED")
print(f"Total frames processed: {frame_count}")
print(f"Total ball detections: {detection_count}")
print("=" * 55)
