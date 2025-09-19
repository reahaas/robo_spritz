# This script is a controller wrapper to the linux driver.
# This is the help text from the linux driver:
# before using this, make sure to set all the rasperry pi configuration according to the Linux driver readme

# ./UscCmd
# UscCmd, Version=1.6.1.0, Culture=neutral, PublicKeyToken=null
# Select one of the following actions:
#   --list                   list available devices
#   --configure FILE         load configuration file into device
#   --getconf FILE           read device settings and write configuration file
#   --restoredefaults        restore factory settings
#   --program FILE           compile and load bytecode program
#   --status                 display complete device status
#   --bootloader             put device into bootloader (firmware upgrade) mode
#   --stop                   stops the script running on the device
#   --start                  starts the script running on the device
#   --restart                restarts the script at the beginning
#   --step                   runs a single instruction of the script
#   --sub NUM                calls subroutine n (can be hex or decimal)
#   --sub NUM,PARAMETER      calls subroutine n with a parameter (hex or decimal)
#                            placed on the stack
#   --servo NUM,TARGET       sets the target of servo NUM in units of
#                            1/4 microsecond
#   --speed NUM,SPEED        sets the speed limit of servo NUM
#   --accel NUM,ACCEL        sets the acceleration of servo NUM to a value 0-255
# Select which device to perform the action on (optional):
#   --device 00001430        (optional) select device #00001430

# And example commands:
# >UscCmd.exe --servo 0,4000

import os
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ServoCommandResult:
    """Result of executing a servo command."""
    success: bool
    return_code: int
    stdout: str
    stderr: str

    def raise_for_error(self):
        if not self.success:
            raise RuntimeError(f"Servo command failed (code={self.return_code}): {self.stderr or self.stdout}")
        return self


class Controller:
    """Very small wrapper for the Pololu UscCmd utility (Linux Maestro).

    Path resolution is intentionally simple per user request:
      - If executable_path is provided, use it as-is.
      - Otherwise use <this_file_dir>/maestro-linux/UscCmd
    """

    DEFAULT_EXECUTABLE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'maestro-linux',
        'UscCmd'
    )

    def __init__(self, executable_path: Optional[str] = None, device_id: Optional[str] = None, check: bool = True):
        self._executable = executable_path or self.DEFAULT_EXECUTABLE_PATH
        self._device_id = device_id
        if check:
            self._assert_available()

    # --- Public API -----------------------------------------------------
    def set_servo_target(self, channel: int, target: int, *, timeout: float = 3.0, validate: bool = True) -> ServoCommandResult:
        """Set servo target.

        Args:
            channel: Servo channel index (0+). No upper bound enforced here.
            target: Target in units of 1/4 microsecond (typical range 4000-8000 for standard servos).
            timeout: Seconds to wait for the command to complete.
            validate: If True, perform basic argument validation.

        Returns:
            ServoCommandResult
        """
        if validate:
            self._validate_channel(channel)
            self._validate_target(target)

        cmd = [self._executable, '--servo', f'{channel},{target}']
        if self._device_id:
            cmd += ['--device', self._device_id]
        return self._run(cmd, timeout)

    def is_available(self) -> bool:
        """Return True if the underlying executable exists and is executable."""
        return os.path.isfile(self._executable) and os.access(self._executable, os.X_OK)

    def get_executable_path(self) -> str:
        return self._executable

    # Context manager (no persistent resources but convenient for symmetry)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    # --- Internals ------------------------------------------------------
    def _assert_available(self):
        if not os.path.isfile(self._executable):
            raise FileNotFoundError(f"UscCmd executable not found: {self._executable}")
        if not os.access(self._executable, os.X_OK):
            # Try to add execute bit (on Unix-like systems)
            try:
                os.chmod(self._executable, 0o755)
            except OSError:
                pass
            if not os.access(self._executable, os.X_OK):
                raise FileNotFoundError(f"UscCmd not executable: {self._executable}")

    @staticmethod
    def _validate_channel(channel: int):
        if not isinstance(channel, int) or channel < 0:
            raise ValueError('channel must be a non-negative int')

    @staticmethod
    def _validate_target(target: int):
        if not isinstance(target, int) or target < 0:
            raise ValueError('target must be a non-negative int (1/4 microsecond units)')

    @staticmethod
    def _run(cmd: list[str], timeout: float) -> ServoCommandResult:
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as e:
            return ServoCommandResult(False, 127, '', str(e))
        except subprocess.TimeoutExpired as e:
            return ServoCommandResult(False, 124, e.stdout or "", f"Timeout: {e.stderr or ''}".strip())
        success = completed.returncode == 0
        return ServoCommandResult(success, completed.returncode, completed.stdout.strip(), completed.stderr.strip())
