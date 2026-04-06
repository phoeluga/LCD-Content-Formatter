"""Helper utilities for the sample application.

These functions read Linux-specific system files and are intended to run on
a Raspberry Pi or similar embedded Linux board.
"""

import fcntl
import socket
import struct


def get_cpu_temperature() -> float:
    """Return the CPU temperature in °C (Linux thermal zone 0)."""
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        return round(int(f.read()) / 1000, 1)


def get_ip_address(interface: str) -> str:
    """Return the IPv4 address for *interface*, or ``"UNKNOWN"`` on failure."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack("256s", interface[:15].encode()),
            )[20:24]
        )
    except OSError as exc:
        print(f"Unable to get IP for '{interface}': {exc}")
        return "UNKNOWN"
