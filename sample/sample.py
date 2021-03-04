import os
import sys
import inspect
import time
from datetime import date, datetime

# Add the parent path to sys.path for the instantiation of HD44780. This is only for the possibility of importing.
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


##########################################################
###  Implementation of the actual sample application.  ###
##########################################################
# Import the actual extension library
from HD44780 import HD44780
# In config.py you can adapt the settings of the display
import config
# The logic functions have been outsourced to focus this example on the actual implementation of the HD44780 library.
import sampleFunctions

# Helper function to consolidate the calls to change the text in a frame row
def changeAndUpdateSampleFrameRowText(frameRow, text):
    frameRow.text = str(text)
    sampleFrame.updateFrameRow(frameRow)

# Instantiation of the extending library
lcd = HD44780(config.lcdI2cExpanderType, config.lcdI2cAddress, config.lcdColumnCount, config.lcdRowCount)

# Instantiation of a display frame
sampleFrame = lcd.Frame()

# Instantiation of several frame row and adding to frame

# Sample of adding a frame row with user defined ID "ipEth0"
sampleFrameRowIpEth0 = sampleFrame.add("ipEth0", "-", "IP eth0: ")
sampleFrameRowIpWlan0 = sampleFrame.add("ipWifi0", "-", "IP wlan0: ")
sampleFrameRowTemp = sampleFrame.add("cpuTemp", "-", "CPU temp.: ", " °C")
# Sample of adding a frame row with no user defined ID
sampleFrameRowCounter = sampleFrame.addWithGuid("-", "Count: ", " iterations")

# Adding more frame rows.
# In this example we use a 2004 display. This means we can address 4 rows. 
# By adding these additional rows, pages are automatically created in the
# background that the library scrolls through when they are shown.
sampleFrameRowDate = sampleFrame.addWithGuid("-", "Date: ")
sampleFrameRowTime = sampleFrame.addWithGuid("-", "Time: ")
sampleFrameRowMoreText = sampleFrame.addWithGuid("Lorem ipsum dolor sit!", "Text: ")

# Loop to change and display the values to be shown on the LCD
while True:
    changeAndUpdateSampleFrameRowText(sampleFrameRowIpEth0, sampleFunctions.getIpAddress('eth0'))
    changeAndUpdateSampleFrameRowText(sampleFrameRowIpWlan0, sampleFunctions.getIpAddress('wlan0'))
    changeAndUpdateSampleFrameRowText(sampleFrameRowTemp, sampleFunctions.getCpuTemperature())
    changeAndUpdateSampleFrameRowText(sampleFrameRowCounter, config.sampleCounter)
    changeAndUpdateSampleFrameRowText(sampleFrameRowDate, date.today())
    changeAndUpdateSampleFrameRowText(sampleFrameRowTime, datetime.now().strftime("%H:%M:%S")) 

    # Play around with the three parameters 'scrollIn', 'scrollToBlank' and 'scrollIfFit' to see the different display styles.
    # The three parameters 'scrollIn', 'scrollToBlank' and 'scrollIfFit' each have the default value 'False' 
    # and therefore do not have to be specified in the function call.
    lcd.scrollFrame(sampleFrame, False, False, False)

    config.sampleCounter += 1
