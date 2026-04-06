"""Helper utilities for the sample application (snake_case module name).

Delegates to sampleFunctions for backward compatibility.
"""

from sampleFunctions import get_cpu_temperature, get_ip_address

__all__ = ["get_cpu_temperature", "get_ip_address"]
