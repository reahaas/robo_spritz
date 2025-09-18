import maestro
import serial.tools.list_ports
from typing import Optional


class MaestroServoController:
    """Clean interface for controlling Pololu Maestro servo controllers"""

    # Standard servo pulse width constants (microseconds * 4 for Maestro)
    SERVO_MIN = 4000      # ~1.0ms pulse width
    SERVO_NEUTRAL = 6000  # ~1.5ms pulse width (stop for continuous rotation)
    SERVO_MAX = 8000      # ~2.0ms pulse width

    # FS90R specific constants (these servos may need different ranges)
    FS90R_MIN = 700      # ~0.8ms pulse width for FS90R
    FS90R_NEUTRAL = 1500  # ~1.5ms pulse width (stop)
    FS90R_MAX = 2300      # ~2.2ms pulse width for FS90R

    def __init__(self, port: Optional[str] = None, servo_type: str = "standard"):
        """
        Initialize the Maestro servo controller

        Args:
            port: COM port string (e.g., 'COM4'). If None, auto-detect.
            servo_type: "standard", "fs90r", or "custom"
        """
        self.controller = None
        self.port = port or self._find_maestro_port()
        self.servo_type = servo_type.lower()

        # Set pulse width ranges based on servo type
        if self.servo_type == "fs90r":
            self.pulse_min = self.FS90R_MIN
            self.pulse_neutral = self.FS90R_NEUTRAL
            self.pulse_max = self.FS90R_MAX
            print(f"Using FS90R servo settings: {self.pulse_min}-{self.pulse_neutral}-{self.pulse_max}")
        else:
            self.pulse_min = self.SERVO_MIN
            self.pulse_neutral = self.SERVO_NEUTRAL
            self.pulse_max = self.SERVO_MAX
            print(f"Using standard servo settings: {self.pulse_min}-{self.pulse_neutral}-{self.pulse_max}")

        if self.port:
            self._connect()

    def _find_maestro_port(self) -> Optional[str]:
        """Find the COM port for the Maestro servo controller"""
        ports = list(serial.tools.list_ports.comports())

        # Look for USB Serial devices (likely candidates for Maestro)
        for port in ports:
            if "USB Serial Device" in port.description:
                print(f"Found potential Maestro port: {port.device} - {port.description}")
                return port.device

        # If no USB Serial Device found, try other ports
        if ports:
            print("No USB Serial Device found. Available COM ports:")
            for port in ports:
                print(f"  {port.device} - {port.description}")
            return ports[0].device  # Return first available port as fallback

        return None

    def _connect(self):
        """Establish connection to the Maestro controller"""
        try:
            self.controller = maestro.Controller(self.port)
            print(f"Successfully connected to Maestro on {self.port}")
        except Exception as e:
            print(f"Failed to connect to Maestro on {self.port}: {e}")
            self.controller = None
            raise

    def is_connected(self) -> bool:
        """Check if controller is connected"""
        return self.controller is not None

    def rotate(self, channel: int, direction: int, speed: int, debug: bool = False):
        """
        Rotate a continuous rotation servo

        Args:
            channel: Servo channel (0-23)
            direction: Rotation direction (-1 for reverse, 1 for forward)
            speed: Speed percentage (0-100)
            debug: Print detailed position information
        """
        if not self.is_connected():
            raise RuntimeError("Controller not connected")

        if not (-1 <= direction <= 1):
            raise ValueError("Direction must be -1 (reverse), 0 (stop), or 1 (forward)")

        if not (0 <= speed <= 100):
            raise ValueError("Speed must be between 0 and 100")

        if direction == 0:
            self.stop(channel, debug)
            return

        # Calculate servo position based on direction and speed
        speed_range = (self.pulse_max - self.pulse_neutral) * (speed / 100)

        if direction > 0:  # Forward
            position = int(self.pulse_neutral + speed_range)
        else:  # Reverse
            position = int(self.pulse_neutral - speed_range)

        # Clamp to valid range
        position = max(self.pulse_min, min(self.pulse_max, position))

        self.controller.setTarget(channel, position)

        if debug:
            pulse_width_ms = position / 4000  # Convert to milliseconds
            print(f"Channel {channel}: Rotating {['reverse', 'stop', 'forward'][direction + 1]} at {speed}% speed")
            print(f"  → Position: {position} (pulse width: {pulse_width_ms:.2f}ms)")
        else:
            print(f"Channel {channel}: Rotating {['reverse', 'stop', 'forward'][direction + 1]} at {speed}% speed (position: {position})")

    def stop(self, channel: int, debug: bool = False):
        """
        Stop a servo (set to neutral position)

        Args:
            channel: Servo channel (0-23)
            debug: Print detailed position information
        """
        if not self.is_connected():
            raise RuntimeError("Controller not connected")

        self.controller.setTarget(channel, self.pulse_neutral)

        if debug:
            pulse_width_ms = self.pulse_neutral / 4000
            print(f"Channel {channel}: Stopped (position: {self.pulse_neutral}, pulse width: {pulse_width_ms:.2f}ms)")
        else:
            print(f"Channel {channel}: Stopped (position: {self.pulse_neutral})")

    def stop_all(self):
        """Stop all servos"""
        if not self.is_connected():
            raise RuntimeError("Controller not connected")

        for channel in range(24):
            self.controller.setTarget(channel, self.pulse_neutral)
        print("All servos stopped")

    def set_position(self, channel: int, position: int, debug: bool = False):
        """
        Set servo to specific position (for standard servos)

        Args:
            channel: Servo channel (0-23)
            position: Position value (typically 4000-8000)
            debug: Print detailed position information
        """
        if not self.is_connected():
            raise RuntimeError("Controller not connected")

        position = max(self.pulse_min, min(self.pulse_max, position))
        self.controller.setTarget(channel, position)

        if debug:
            pulse_width_ms = position / 4000
            print(f"Channel {channel}: Set to position {position} (pulse width: {pulse_width_ms:.2f}ms)")
        else:
            print(f"Channel {channel}: Set to position {position}")

    def test_fs90r_calibration(self, channel: int):
        """
        Test different pulse widths to find the correct range for FS90R servo

        Args:
            channel: Servo channel to test (0-23)
        """
        if not self.is_connected():
            raise RuntimeError("Controller not connected")

        print(f"\nCalibrating FS90R servo on channel {channel}")
        print("Testing different pulse widths to find rotation points...")

        # Test various pulse widths
        test_positions = [
            (3200, "0.8ms - Should rotate fast reverse"),
            (4000, "1.0ms - Should rotate medium reverse"),
            (5000, "1.25ms - Should rotate slow reverse"),
            (5800, "1.45ms - Should barely rotate reverse"),
            (6000, "1.5ms - Should STOP"),
            (6200, "1.55ms - Should barely rotate forward"),
            (7000, "1.75ms - Should rotate slow forward"),
            (8000, "2.0ms - Should rotate medium forward"),
            (8800, "2.2ms - Should rotate fast forward")
        ]

        for position, description in test_positions:
            print(f"\nTesting position {position} ({description})")
            self.controller.setTarget(channel, position)
            input("Press Enter to continue to next position...")

        # Return to neutral
        self.controller.setTarget(channel, 6000)
        print(f"\nCalibration complete. Servo returned to neutral position.")

    def get_position(self, channel: int) -> int:
        """
        Get current position of a servo

        Args:
            channel: Servo channel (0-23)

        Returns:
            Current servo position
        """
        if not self.is_connected():
            raise RuntimeError("Controller not connected")

        return self.controller.getPosition(channel)

    def is_moving(self, channel: int) -> bool:
        """
        Check if a servo is currently moving

        Args:
            channel: Servo channel (0-23)

        Returns:
            True if servo is moving, False otherwise
        """
        if not self.is_connected():
            raise RuntimeError("Controller not connected")

        return self.controller.isMoving(channel)

    def close(self):
        """Clean up and close the connection"""
        if self.controller:
            self.stop_all()  # Stop all servos before closing
            self.controller.close()
            self.controller = None
            print("Maestro controller connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
