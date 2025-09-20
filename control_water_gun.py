import datetime

from maestro_linux_driver import Controller
from direction_module import Direction_Module
from frame_module import Frame_Module, display_camera, get_center
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Water gun controller using face direction")
    parser.add_argument('--no-display', action='store_true', help='Disable camera window display')
    parser.add_argument('--disable-horizontal', action='store_true', help='Disable horizontal movement')
    parser.add_argument('--disable-vertical', action='store_true', help='Disable vertical movement')
    parser.add_argument('-d', '--delay', type=float, default=0.1, help='Delay (seconds) between sequence steps or duration for sequence steps')
    parser.add_argument('--speed', type=float, default=0.2, help='Movement speed (default: 0.2)')
    return parser.parse_args()

def main():
    args = parse_args()
    camera = Frame_Module()
    navigator = Direction_Module(tolerance=10)
    controller = Controller()

    print("Starting water gun control. Press Ctrl+C to stop.")

    last_movement = datetime.now()

    while True:
        # Simulate getting a frame from the camera
        frame = camera.get_frame()

        face_position = navigator.get_face_position(frame)
        center = get_center(frame)

        # Get direction from the navigator
        direction = navigator.get_direction(frame)
        h, v = direction

        if not args.no_display:
            display_camera(frame, face_position, direction, center)

        # return if delay is not meat:
        if args.delay > 0:
            current_time = datetime.now()
            time_from_last_movement = current_time - last_movement
            if time_from_last_movement < datetime.timedelta(seconds=args.delay):
                continue



        # Control the water gun based on direction
        h_direction = "cw" if h==1 else "ccw"
        v_direction = "cw" if v==1 else "ccw"

        print(f"{h=}, {h_direction=}, {v=}, {v_direction=}")

        # Horizontal movement
        if args.disable_horizontal:
            if h != 0:
                print("Horizontal movement disabled (would move)")
        else:
            if h != 0:
                controller.move_step(channel=1, direction=h_direction, speed=args.speed)
            else:
                print("Stopping horizontal movement")
                controller.stop(channel=1)  # Stop horizontal movement

        # Vertical movement
        if args.disable_vertical:
            if v != 0:
                print("Vertical movement disabled (would move)")
        else:
            if v != 0:
                controller.move_step(channel=0, direction=v_direction, speed=args.speed)
            else:
                print("Stopping vertical movement")
                controller.stop(channel=0)  # Stop vertical movement

if __name__ == '__main__':
    main()
