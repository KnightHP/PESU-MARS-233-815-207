import sys
import os

lib_path = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.insert(0, lib_path)

from controller import Supervisor

robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

keyboard = robot.getKeyboard()
keyboard.enable(timestep)

# Nodes
red_ball = robot.getFromDef('RED_BALL')
green_ball = robot.getFromDef('GREEN_BALL')
robot_node = robot.getSelf()

red_translation = red_ball.getField('translation')
green_translation = green_ball.getField('translation')
robot_translation = robot_node.getField('translation')

selected_ball = 'RED'

print("FINAL SYSTEM: Smooth Movement + Accurate Detection")
print("="*60)

# Detection state
prev_red = False
prev_green = False

# Movement speed (smooth)
step_size = 0.015

# 🔥 FIXED DETECTION FUNCTION (IMPORTANT CHANGE)
def is_in_front(ball_pos, robot_pos):
    dx = ball_pos[0] - robot_pos[0]
    dz = ball_pos[2] - robot_pos[2]

    return (
        abs(dx) < 0.4 and   # wide detection
        dz > 0 and          # 🔥 FIXED DIRECTION
        abs(dz) < 1.0       # depth range
    )

while robot.step(timestep) != -1:

    # -------- KEYBOARD --------
    key = keyboard.getKey()

    if key == ord('R'):
        selected_ball = 'RED'
        print("Selected: RED")

    elif key == ord('G'):
        selected_ball = 'GREEN'
        print("Selected: GREEN")

    elif key in (315, ord('W'), 317, ord('S'), 314, ord('A'), 316, ord('D')):
        field = red_translation if selected_ball == 'RED' else green_translation
        pos = field.getSFVec3f()

        if key in (315, ord('W')):
            pos[2] -= step_size
            print(f"Moving {selected_ball} forward")

        elif key in (317, ord('S')):
            pos[2] += step_size
            print(f"Moving {selected_ball} backward")

        elif key in (314, ord('A')):
            pos[0] -= step_size
            print(f"Moving {selected_ball} left")

        elif key in (316, ord('D')):
            pos[0] += step_size
            print(f"Moving {selected_ball} right")

        field.setSFVec3f(pos)

    # -------- DETECTION --------
    red_pos = red_translation.getSFVec3f()
    green_pos = green_translation.getSFVec3f()
    robot_pos = robot_translation.getSFVec3f()

    current_red = is_in_front(red_pos, robot_pos)
    current_green = is_in_front(green_pos, robot_pos)

    # Print only when entering detection zone
    if current_red and not prev_red:
        print("🔴 RED BALL DETECTED!")

    elif current_green and not prev_green:
        print("🟢 GREEN BALL DETECTED!")

    prev_red = current_red
    prev_green = current_green