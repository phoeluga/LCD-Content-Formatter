import os,sys,inspect,time
import socket
import fcntl
import struct
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from HD44780 import HD44780
import config

from subprocess import PIPE, Popen

def getCpuTemperature():
    file = open("/sys/class/thermal/thermal_zone0/temp", "r")
    cpuTemperature = file.readline()
    file.close()
    return round(int(cpuTemperature)/1000, 1)

def getIpAddress(interface):
    ip = "UNKNOWN1234567889"
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



lcd = HD44780(config.lcdI2cExpanderType, config.lcdI2cAddress, config.lcdColumnCount, config.lcdRowCount)

sampleFrame = lcd.Frame()

sampleFrameRowIpEth0 = sampleFrame.add("ipEth0", "-", "IP eth0: ")
sampleFrameRowIpWlan0 = sampleFrame.add("ipWifi0", "-", "IP wlan0: ")


# Sample of adding a frame row with user defined ID "heatsinktemp"
sampleFrameRowTemp = sampleFrame.add("cpuTemp", "-", "CPU temp.: ", " °C")
# Sample of adding a frame row with no user defined ID
sampleFrameRowCounter = sampleFrame.add("kuchen", "-", "Count: ", " iterations")



counter = 123
while True:
    sampleFrameRowIpEth0.text = str(getIpAddress('eth0'))
    sampleFrame.updateFrameRow(sampleFrameRowIpEth0)

    sampleFrameRowIpWlan0.text = str(getIpAddress('wlan0'))
    sampleFrame.updateFrameRow(sampleFrameRowIpWlan0)

    sampleFrameRowCounter.text = str(counter)
    sampleFrame.updateFrameRow(sampleFrameRowCounter)

    sampleFrameRowTemp.text = str(getCpuTemperature())
    sampleFrame.updateFrameRow(sampleFrameRowTemp)

    sampleFrameRowCounter.text = str(counter)
    sampleFrame.updateFrameRow(sampleFrameRowCounter)

    lcd.scrollFrame(sampleFrame, True, True, False)

    counter += 1
    time.sleep(5)