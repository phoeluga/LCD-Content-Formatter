"""lcd-content-formatter — HD44780 LCD content management without RPLCD.

Typical usage::

    from lcd_content_formatter import HD44780

    with HD44780("PCF8574", 0x27, cols=20, rows=4) as lcd:
        frame = lcd.Frame()
        row = frame.add("temp", "-", prefix="Temp: ", postfix=" °C")

        row.text = "23.5"
        frame.update_row(row)
        lcd.scroll_frame(frame)
"""

from .display import HD44780
from .exceptions import DuplicateFrameRowError, FrameRowNotFoundError, I2CError, LCDError
from .frame import Frame, FrameRow

__version__ = "2.0.1"
__all__ = [
    "HD44780",
    "Frame",
    "FrameRow",
    "LCDError",
    "FrameRowNotFoundError",
    "DuplicateFrameRowError",
    "I2CError",
]
