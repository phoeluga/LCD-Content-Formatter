##################################################################################
#### General configuration
##################################################################################
import os
import inspect
# Do not change folder structure of the scripts [config in subfolder relative to main.py]
version = "1.0.2102.1401"
configScriptDir = os.path.dirname(__file__)
rootScriptDir = os.path.dirname(configScriptDir)


##################################################################################
#### LCD configuration
##################################################################################
lcdI2cExpanderType = "PCF8574"
lcdI2cAddress = 0x27
lcdColumnCount = 20
lcdRowCount = 4
