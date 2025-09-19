
from maestro_linux_driver import Controller
from direction_module import Direction_Module
from frame_module import Frame_Module

def main():
    camera = Frame_Module()
    navigator = Direction_Module(tolerance=10)
    controller = Controller()

    print("Starting water gun control. Press Ctrl+C to stop.")

    try:
        while True:
            # Simulate getting a frame from the camera
            frame = camera.get_frame()

            # Get direction from the navigator
            h, v = navigator.get_direction(frame)

            # Control the water gun based on direction

            h_direction = "cw" if h==1 else "ccw"
            v_direction = "cw" if v==1 else "ccw"

            if h == 1:
                controller.move_step(channel=0, direction="cw", speed=50)  # Rotate right
            elif h == -1:
                controller.rotate(channel=0, direction="ccw", speed=50)  # Rotate left
            else:
                controller.stop(channel=0)  # Stop horizontal movement

            if v == 1:
                controller.rotate(channel=1, direction=1, speed=50)  # Rotate up
            elif v == -1:
                controller.rotate(channel=1, direction=-1, speed=50)  # Rotate down
            else:
                controller.stop(channel=1)

if __name__ == '__main__':
    main()
