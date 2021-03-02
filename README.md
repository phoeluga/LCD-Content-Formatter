# LCD-Content-Formatter

With this extension you can easily show any text on your LCD without thinking about the text length or amount of rows.

This small library will extend [RPLCD](https://github.com/dbrgn/RPLCD) with the following functions:

- Scrolling text
- Pagination
- Prefix
- Postfix
- Structuring

## Preface

This extension was build due to another project what will implement a usage of a HD44780 LCD display.
The display was used via I2C extender on a Raspberry Pi.

## Prerequisites

The following prerequisites needs to be met in software and hardware.

### Software

- Python version >= 3.7
- RPLCD library from *dbrgn* ([https://github.com/dbrgn/RPLCD](https://github.com/dbrgn/RPLCD))  
Can be installed via PIP ([https://pypi.org/project/RPLCD](https://pypi.org/project/RPLCD))

### Hardware

- LCD display HD44780 2004 or 1602
- I2C extender for HD44780
- Raspberry Pi or any other device what is able to control the I2C LCD display in dependence to the needed software prerequisites

## Concept

The following figure illustrates the concept of this library extension using the example of a 2004 HD44780 LCD display.

![LibConcept](https://raw.githubusercontent.com/rednoid/LCD-Content-Formatter/docu/images/HD44780_Concept.png)

### Frame
A frame will be used to hold the information to display.
The frame will consists of frame rows. The maximum number of frame rows a frame can show depends on the number the hardware HD44780 display can show. In this sample four.

### Page
If more rows then the frame can show exist, the library will manage this in automatically paginate the rows. In the above sample, eight frame rows exist so two pages exist.

### Frame row
A frame row will contain the actual information and text that is shown on the display. The frame row consists of four parts:

- **ID**  
Each frame row will get an own ID were you can simply address them and be able to change the values to your needs.
The ID can be configured optional. If an ID is not needed for the row, you must not specify one. In this case a random GUID will taken.

- **Prefix**  
Displays like above mentioned will usually used to show data like sensor values etc. The prefix allowes you keep a constant text like *"Temp."* - for Temperature - in front of your actual value. You then only need to change the temperature value and not the whole line.  
(This files is optional and must not be used if not needed)

- **Text**  
This is the actual value that you want to show on the display.

- **Postfix**  
The postfix allowes you keep a constant text like "*°C"* - for Temperature - right behind of your actual value. You then only need to change the temperature value and not the whole line.  
(This files is optional and must not be used if not needed)

