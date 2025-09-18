import time
from maestro_controller import MaestroServoController


class ServoChannelTester:
    """Test suite for Maestro servo controller channels"""

    def __init__(self, controller: MaestroServoController):
        """
        Initialize the channel tester

        Args:
            controller: MaestroServoController instance
        """
        self.controller = controller

    def test_individual_channel(self, channel: int, test_duration: float = 2.0):
        """
        Test a single servo channel

        Args:
            channel: Servo channel to test (0-23)
            test_duration: Duration for each test phase (seconds)
        """
        print(f"\nTesting channel {channel}:")

        # Test forward rotation
        print(f"  → Forward rotation at 75% speed")
        self.controller.rotate(channel, 1, 75)
        time.sleep(test_duration)

        # Test reverse rotation
        print(f"  → Reverse rotation at 50% speed")
        self.controller.rotate(channel, -1, 50)
        time.sleep(test_duration)

        # Test position control
        print(f"  → Position control test")
        self.controller.set_position(channel, 5000)
        time.sleep(1)
        self.controller.set_position(channel, 7000)
        time.sleep(1)

        # Stop servo
        print(f"  → Stopping channel {channel}")
        self.controller.stop(channel)
        time.sleep(0.5)

    def test_all_channels(self, test_duration: float = 2.0):
        """
        Test all servo channels sequentially

        Args:
            test_duration: Duration for each channel test (seconds)
        """
        print("Starting comprehensive test of all 24 channels...")
        print("Press Ctrl+C to interrupt the test\n")

        for channel in range(24):
            try:
                self.test_individual_channel(channel, test_duration)
            except KeyboardInterrupt:
                print(f"\nTest interrupted at channel {channel}")
                self.controller.stop_all()
                raise

        print("\n✓ All channels tested successfully!")

    def test_speed_variations(self, channel: int):
        """
        Test different speed settings on a specific channel

        Args:
            channel: Servo channel to test (0-23)
        """
        print(f"\nTesting speed variations on channel {channel}:")

        speeds = [25, 50, 75, 100]

        for speed in speeds:
            print(f"  → Testing {speed}% speed forward")
            self.controller.rotate(channel, 1, speed)
            time.sleep(1.5)

            print(f"  → Testing {speed}% speed reverse")
            self.controller.rotate(channel, -1, speed)
            time.sleep(1.5)

        self.controller.stop(channel)
        print(f"  → Speed test completed for channel {channel}")

    def test_position_sweep(self, channel: int, steps: int = 5):
        """
        Test position sweep across servo range

        Args:
            channel: Servo channel to test (0-23)
            steps: Number of position steps to test
        """
        print(f"\nTesting position sweep on channel {channel}:")

        positions = []
        for i in range(steps):
            pos = int(self.controller.SERVO_MIN +
                     (self.controller.SERVO_MAX - self.controller.SERVO_MIN) * i / (steps - 1))
            positions.append(pos)

        for pos in positions:
            print(f"  → Moving to position {pos}")
            self.controller.set_position(channel, pos)
            time.sleep(1)

        self.controller.stop(channel)
        print(f"  → Position sweep completed for channel {channel}")


def quick_demo():
    """Quick demonstration of servo control features"""
    print("=== Quick Servo Control Demo ===")

    with MaestroServoController() as controller:
        if not controller.is_connected():
            print("❌ Could not connect to Maestro controller.")
            print("Please check that your Maestro is connected.")
            return

        tester = ServoChannelTester(controller)

        # Test channel 0 with various operations
        print("\n1. Testing individual channel control:")
        tester.test_individual_channel(0, test_duration=1.5)

        print("\n2. Testing speed variations:")
        tester.test_speed_variations(0)

        print("\n3. Testing position sweep:")
        tester.test_position_sweep(0, steps=3)

        print("\n✓ Demo completed successfully!")


def comprehensive_test():
    """Comprehensive test of all channels"""
    print("=== Comprehensive Channel Test ===")
    print("This will test all 24 channels (takes ~2 minutes)")

    response = input("Continue? (y/N): ").lower().strip()
    if response != 'y':
        print("Test cancelled.")
        return

    with MaestroServoController() as controller:
        if not controller.is_connected():
            print("❌ Could not connect to Maestro controller.")
            return

        tester = ServoChannelTester(controller)

        try:
            tester.test_all_channels(test_duration=2.0)
        except KeyboardInterrupt:
            print("Test interrupted by user")


def interactive_test():
    """Interactive test mode for manual channel testing"""
    print("=== Interactive Channel Test ===")
    print("Commands:")
    print("  test <channel>     - Test specific channel")
    print("  rotate <channel> <direction> <speed> - Rotate servo")
    print("  stop <channel>     - Stop specific channel")
    print("  stop_all          - Stop all channels")
    print("  quit              - Exit")

    with MaestroServoController() as controller:
        if not controller.is_connected():
            print("❌ Could not connect to Maestro controller.")
            return

        tester = ServoChannelTester(controller)

        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue

                cmd = command[0].lower()

                if cmd == 'quit':
                    break
                elif cmd == 'test' and len(command) == 2:
                    channel = int(command[1])
                    tester.test_individual_channel(channel, 1.0)
                elif cmd == 'rotate' and len(command) == 4:
                    channel, direction, speed = int(command[1]), int(command[2]), int(command[3])
                    controller.rotate(channel, direction, speed)
                elif cmd == 'stop' and len(command) == 2:
                    channel = int(command[1])
                    controller.stop(channel)
                elif cmd == 'stop_all':
                    controller.stop_all()
                else:
                    print("Invalid command. Type 'quit' to exit.")

            except (ValueError, IndexError):
                print("Invalid command format.")
            except KeyboardInterrupt:
                break

        print("Exiting interactive mode...")


def main():
    """Main function with test mode selection"""
    print("Maestro Servo Controller Test Suite")
    print("=" * 40)
    print("1. Quick Demo")
    print("2. Comprehensive Test (all channels)")
    print("3. Interactive Test Mode")
    print("4. Exit")

    try:
        choice = input("\nSelect test mode (1-4): ").strip()

        if choice == '1':
            quick_demo()
        elif choice == '2':
            comprehensive_test()
        elif choice == '3':
            interactive_test()
        elif choice == '4':
            print("Goodbye!")
        else:
            print("Invalid choice.")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == '__main__':
    main()
