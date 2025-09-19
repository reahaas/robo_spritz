import sys
import argparse
import time
from maestro_linux_driver import Controller

def test_servo_sequence(channel: int, device: str = None):
    positions = [
        ("Stop (neutral)", 6000),
        ("Clockwise (CW)", 8000),
        ("Counterclockwise (CCW)", 4000),
        ("Stop (neutral)", 6000),
    ]
    with Controller(device_id=device) as ctrl:
        for label, pos in positions:
            print(f"Setting servo {channel} to {label} ({pos})...")
            result = ctrl.set_servo_target(channel, pos)
            if result.success:
                print(f"  Success.")
            else:
                print(f"  Failed: {result.stderr or result.stdout}")
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Simple tester for Pololu Maestro using maestro_linux_driver.py")
    parser.add_argument('-c', '--channel', type=int, help='Servo channel (0-based index)', default=0)
    parser.add_argument('-t', '--target', type=int, help='Servo target (1/4 microsecond units, e.g. 4000-8000)')
    parser.add_argument('--device', type=str, default=None, help='Optional Maestro device ID')
    parser.add_argument('--sequence', action='store_true', help='Run CW/CCW/Stop sequence')
    args = parser.parse_args()

    if args.sequence:
        test_servo_sequence(args.channel, args.device)
        return

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
        with Controller(device_id=args.device) as ctrl:
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