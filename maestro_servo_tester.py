import sys
import argparse
import time
from maestro_linux_driver import Controller


def test_servo_sequence(channel: int, device: str = None, executable_path: str = None, speed: float = 1.0, step_duration: float = 1.0):
    """Run a simple sequence using high-level controller methods.
    Sequence: step cw -> step ccw -> stop (implicit in each step) then explicit final stop.
    """
    with Controller(executable_path=executable_path, device_id=device) as ctrl:
        print(f"Step CW channel {channel} speed={speed} duration={step_duration}s")
        ctrl.move_step(channel, 'cw', speed, step_duration)
        print(f"Step CCW channel {channel} speed={speed} duration={step_duration}s")
        ctrl.move_step(channel, 'ccw', speed, step_duration)
        print(f"Explicit final stop channel {channel}")
        ctrl.stop(channel)


def main():
    parser = argparse.ArgumentParser(description="Simple tester for Pololu Maestro using maestro_linux_driver.py")
    parser.add_argument('-c', '--channel', type=int, help='Servo channel (0-based index)', default=0)
    parser.add_argument('-t', '--target', type=int, help='Servo target (1/4 microsecond units, e.g. 4000-8000)')
    parser.add_argument('--device', type=str, default=None, help='Optional Maestro device ID')
    parser.add_argument('--sequence', action='store_true', help='Run CW/CCW/Stop sequence (high-level)')
    parser.add_argument('-x', '--executable', dest='executable', type=str, default=None,
                        help='Path to UscCmd executable (overrides default <script_dir>/maestro-linux/UscCmd)')
    parser.add_argument('-s', '--speed', type=float, default=1.0, help='Normalized speed 0..1 for cw/ccw moves')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='Delay (seconds) between sequence steps or duration for sequence steps')
    parser.add_argument('--step', action='store_true', help='Run a single timed step (requires --direction and --duration)')
    parser.add_argument('--direction', type=str, help="Direction for --step or single step: 'cw' or 'ccw'")
    parser.add_argument('--duration', type=float, help='Duration (seconds) for --step single movement')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--cw', action='store_true', help='Move clockwise using high-level API')
    group.add_argument('--ccw', action='store_true', help='Move counter-clockwise using high-level API')
    group.add_argument('--stop', action='store_true', help='Send stop/neutral using high-level API')

    args = parser.parse_args()

    # High-level single action shortcuts
    if args.cw or args.ccw or args.stop or args.step:
        try:
            with Controller(executable_path=args.executable, device_id=args.device) as ctrl:
                if args.step:
                    if not args.direction or args.duration is None:
                        print("--step requires --direction and --duration")
                        sys.exit(1)
                    print(f"Stepping {args.direction} channel {args.channel} speed={args.speed} duration={args.duration}s")
                    ctrl.move_step(args.channel, args.direction, args.speed, args.duration)
                elif args.cw:
                    print(f"Moving CW channel {args.channel} speed={args.speed}")
                    ctrl.move_cw(args.channel, args.speed)
                elif args.ccw:
                    print(f"Moving CCW channel {args.channel} speed={args.speed}")
                    ctrl.move_ccw(args.channel, args.speed)
                else:  # stop
                    print(f"Stopping channel {args.channel}")
                    ctrl.stop(args.channel)
            return
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    # High-level sequence
    if args.sequence:
        test_servo_sequence(args.channel, args.device, args.executable, args.speed, args.delay)
        return

    # Legacy direct target mode
    channel = args.channel
    target = args.target

    if channel is None:
        try:
            channel = int(input('Enter servo channel (0+): '))
        except Exception:
            print('Invalid channel input.')
            sys.exit(1)
    if target is None:
        try:
            target = int(input('Enter servo target (e.g. 4000-8000): '))
        except Exception:
            print('Invalid target input.')
            sys.exit(1)

    try:
        with Controller(executable_path=args.executable, device_id=args.device) as ctrl:
            result = ctrl.set_servo_target(channel, target)
            if result.success:
                print(f"Success: Servo {channel} set to {target}.")
            else:
                print(f"Failed: {result.stderr or result.stdout}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()