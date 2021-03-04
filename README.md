# LCD-Content-Formatter

[![Version](https://img.shields.io/badge/version-1.0.2103.0401-brightgreen)](https://github.com/rednoid/LCD-Content-Formatter)
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
1. Install the required libraries from Software Prerequisites.
2. Download this repository and extract it.
3. Copy the module `HD44780.py` to your project
4. Import the module:  
    ```python
    from HD44780 import HD44780
    ```
5. Instantiate the class:  
    ```python
    lcd = HD44780(config.lcdI2cExpanderType, config.lcdI2cAddress, config.lcdColumnCount, config.lcdRowCount)
    ```
6. Create a frame:
    ```python
    sampleFrame = lcd.Frame()
    ```
7. Create frame row/s:
    ```python
    sampleFrameRowDate = sampleFrame.addWithGuid("-", "Date: ")
    sampleFrameRowTime = sampleFrame.addWithGuid("-", "Time: ")
    ```
8. Show the frame on the display:
    ```python
    lcd.scrollFrame(sampleFrame)
    ```

## Sample

Find a detailed sample script in the folder `sample` of this repository.
You should be able to run it from scratch with just adapting the LCD I2C settings in the `config.py` file.

## API Reference

### Classes

* <u>`HD44780(CharLCD)`</u>  
    This is the main class that inherits `RPLCD.i2c CharLCD` from [RPLCD](https://github.com/dbrgn/RPLCD)

    #### Public functions:
    * <u>`__init__(i2c_expander, address, cols, rows, dotsize=8, expander_params=None, port=1, charmap='A00', linebreaks=True, backlight=True)`</u>  
        The constructor of this module passes the provided parameters to the parent class `RPLCD.i2c CharLCD` from the [RPLCD](https://github.com/dbrgn/RPLCD) library. The parameters of the I2C expander (`i2c_expander`), the I2C address of the expander (`address`) and the number of columns (`cols`) and rows (`rows`) of the physical display must be provided. All other parameters are optional and have the default value of the parent `RPLCD.i2c CharLCD` class.
    * <u>`writeFrame(framebuffer, pageNumber=1, scrollingFrame=False)`</u>  
        Shows the specified frame as `framebuffer` on the display. If the number of frame rows is larger than the number of rows the display can show, pages are automatically created in the background. The page to be displayed can be specified by the parameter `pageNumber`.  
        The parameter `scrollingFrame` is only needed in the combination by the call through the function `scrollFrame`. Otherwise it must always be False for a correct output.  
		This function only displays the content of a frame and does not include a scrolling feature. For this, the function `scrollFrame` must be called.
    * <u>`scrollFrame(framebuffer, scrollIn=False, scrollToBlank=False, scrollIfFit=False, delay=0.5, showFirstFrameAfterScroll=True)`</u>  
	    This is the main function that should be used to display the frame content provided in the frame as `framebuffer` on the LCD.  
		The remaining parameters provide the following functionality:  
        * <u>`scrollIn`</u>  
		    If `True`, the text is scrolled in from the right side of the LCD. Otherwise, the beginning of the text is displayed before scrolling starts.
		* <u>`scrollToBlank`</u>  
		    If `True`, the text is scrolled out to the left until it is no longer visible. Otherwise, the scrolling stops as soon as the text is completely displayed.
		* <u>`scrollIfFit`</u>  
		    Specifies whether the text should be scrolled by the parameters `scrollIn` and `scrollToBlank` if the text can also be displayed completely in the LCD row without scrolling.
		* <u>`delay`</u>  
		    Specifies the time in seconds to wait between scrolling and before displaying the inserted characters. Defines the scrolling speed.
		* <u>`showFirstFrameAfterScroll`</u>  
		    Specifies whether the display should be reset to the output - before/at the start of scrolling - when the function is ended.
		    

* <u>`Frame()`</u>
    Instantiate this class for getting a object that represents a frame that holds the frame rows. 

    #### Classes
    * <u>`FrameRow`</u>  
        This is a structure that that have the following attributes as String:
        * `id`
        * `text`
        * `prefix`
        * `postfix`

    #### Public functions:  
    * <u>`add(id, text="", prefix="", postfix="")`</u>  
        Adds a frame row with a specific `id` to the parent frame. All other fields are optional to allow you to provide a blank frame row.
    * <u>`addWithGuid(text, prefix="", postfix="")`</u>  
        Adds a frame row  to the parent frame without the need to specific `id`. In case a frame row does not need to be addressed by an ID, then this function can be used, which uses a generated GUID as a reference in the background.
    * <u>`getFrame(id, createEmptyRowIfIdNotExist=True)`</u>  
        Returns a frame row requested by the `id` parameter. If the requested `id` is not found in the parent frame, it can be created if the `createEmptyRowIfIdNotExist` parameter is specified as `True`.
    * <u>`removeByIndex(id)`</u>  
        This function 
    * <u>`clear()`</u>  
        This function clears all attributes to an empty string except the `id`
    * <u>`updateFrameRow(frameRow)`</u>  
        This function will update the provided frame row in the parent frame. 
        
## Changelog
**1.0.2103.0401**  
Fixed scrolling issue related to the introduction of the `postfix`

**1.0.2102.1401**  
Initial release
