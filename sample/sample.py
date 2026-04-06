"""Sample application demonstrating lcd-content-formatter.

Adjust the I2C settings in config.py to match your hardware before running:

    python sample/sample.py

The sample displays IP addresses, CPU temperature, a counter, date, and time
on a 20×4 HD44780 LCD. Text that overflows the row width scrolls automatically.
"""

import os
import sys
import time
from datetime import date, datetime

# Allow running from the repo root without installing the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lcd_content_formatter import HD44780

import config
import sample_functions


def main() -> None:
    with HD44780(
        config.lcd_i2c_expander_type,
        config.lcd_i2c_address,
        cols=config.lcd_column_count,
        rows=config.lcd_row_count,
    ) as lcd:
        frame = lcd.Frame()

        # Rows with explicit IDs so they can be updated by reference
        row_ip_eth0  = frame.add("ip_eth0",  "-",  prefix="IP eth0:  ")
        row_ip_wlan0 = frame.add("ip_wlan0", "-",  prefix="IP wlan0: ")
        row_temp     = frame.add("cpu_temp", "-",  prefix="CPU temp: ", postfix=" °C")
        row_counter  = frame.add("counter",  "-",  prefix="Count: ",    postfix=" iter.")

        # Adding more rows than the display height creates additional pages.
        # scroll_frame() iterates through them automatically.
        row_date = frame.add_with_guid("-", prefix="Date: ")
        row_time = frame.add_with_guid("-", prefix="Time: ")
        row_long = frame.add_with_guid("Lorem ipsum dolor sit amet!", prefix="Text: ")

        while True:
            row_ip_eth0.text  = sample_functions.get_ip_address("eth0")
            row_ip_wlan0.text = sample_functions.get_ip_address("wlan0")
            row_temp.text     = str(sample_functions.get_cpu_temperature())
            row_counter.text  = str(config.sample_counter)
            row_date.text     = str(date.today())
            row_time.text     = datetime.now().strftime("%H:%M:%S")

            for row in (row_ip_eth0, row_ip_wlan0, row_temp, row_counter, row_date, row_time):
                frame.update_row(row)

            # Play with scroll_in / scroll_to_blank / scroll_if_fit to see
            # the different animation styles described in the README.
            lcd.scroll_frame(frame, scroll_in=False, scroll_to_blank=False)

            config.sample_counter += 1


if __name__ == "__main__":
    main()
