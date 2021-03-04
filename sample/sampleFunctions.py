import socket
import fcntl
import struct
from subprocess import PIPE, Popen

def getCpuTemperature():
    file = open("/sys/class/thermal/thermal_zone0/temp", "r")
    cpuTemperature = file.readline()
    file.close()
    return round(int(cpuTemperature)/1000, 1)

def getIpAddress(interface):
    ip = "UNKNOWN"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(interface[:15], 'utf-8'))
        )[20:24])
    except Exception as e:
        print(f"Unable to get IP for interface '{interface}' - '{e}'")
    return ip