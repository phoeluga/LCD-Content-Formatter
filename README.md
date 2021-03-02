# LCD-Content-Formatter

[![Version](https://img.shields.io/badge/version-1.0.2102.1401-brightgreen)](https://github.com/rednoid/LCD-Content-Formatter)
[![Python Version](https://img.shields.io/badge/python-%3Ev3.7-blue)](https://github.com/rednoid/LCD-Content-Formatter)
[![Release](https://img.shields.io/badge/release-stable-orange)](https://github.com/rednoid/LCD-Content-Formatter)
[![GitHubCheck](https://img.shields.io/github/checks-status/rednoid/LCD-Content-Formatter/main)](https://github.com/rednoid/LCD-Content-Formatter)
[![Issues](https://img.shields.io/github/issues/rednoid/LCD-Content-Formatter)](https://github.com/rednoid/LCD-Content-Formatter)
[![License](https://img.shields.io/pypi/l/RPLCD.svg)](https://github.com/rednoid/LCD-Content-Formatter)

With this extension you can easily display any text on your LCD without worrying about the text length or the number of lines. Also it is possible to create a constant prefix and postfix to make data display easy and fast.

This small library extends [RPLCD](https://github.com/dbrgn/RPLCD) with the following functions:

- Scrolling text
- Pagination
- Prefix
- Postfix
- Structuring

## Preface

This extension was created based on another project which implements the use of a HD44780 LCD. The idea was to make it easy to use an LCD without having to take formatting into account.  
The display was connected to a Raspberry Pi via an I2C extender.

## Prerequisites

The following requirements must be met in software and hardware.

### Software

- Python version >= 3.7
- RPLCD library from *dbrgn* ([https://github.com/dbrgn/RPLCD](https://github.com/dbrgn/RPLCD))  
Can be installed via PIP ([https://pypi.org/project/RPLCD](https://pypi.org/project/RPLCD))

### Hardware

- LCD HD44780 - 2004 or 1602
- I2C extender for HD44780
- Raspberry Pi or other device capable of addressing the I2C display, depending on the required software prerequisites

## Concept

The following figure illustrates the concept of this library extension using the example of a 2004 HD44780 LCD.

<p align="center">
	<img src="/../docu/images/HD44780_Concept.png?raw=true" width="80%"/>
</p>

### Frame
A frame is used to hold the information to be displayed.
The frame consists of frame rows. The maximum number of frame rows that a frame can show depends on the number that the hardware - HD44780 Display - can display. In this example, four.

### Page
If there are more rows than the frame can display, the library manages this by automatically grouping the rows into pages. In the example above, there are eight frame rows, so two pages.

### Frame row
A frame row contains the actual information and texts that are shown on the display. The frame row consists of four parts:

- **ID**  
Each frame row gets its own ID, which you can easily address and whose values can be changed according to your needs.
The ID can be configured optionally. If an ID is not needed for the row, you do not have to specify one. In this case a random GUID will be taken.

- **Prefix**  
Displays, like the one above, are often used to show data like sensor values, etc. The prefix allows you to keep a constant text like *"Temp. "* - for temperature - in front of your current value. You then only need to change the temperature value and not the whole line.  
(This field is optional and need not be used if it is not needed)

- **Text**  
This is the actual value you want to show on the display.

- **Postfix**  
The postfix allows you to put a constant text like "*°C "* - for temperature - directly after your current value. You then only need to change the temperature value and not the whole line.  
(This field is optional and need not be used if it is not needed)

## Usage
TODO

## Sample
TODO

## Changelog

**1.0.2102.1401**  
Initial release
