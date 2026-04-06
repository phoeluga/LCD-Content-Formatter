"""Low-level PCF8574 + HD44780 I2C driver.

This module is private. Use :class:`~lcd_content_formatter.HD44780` as the
public entry point.

PCF8574 → HD44780 pin mapping (standard wiring):
    P0 → RS   (Register Select: 0=command, 1=character data)
    P1 → RW   (Read/Write: always 0=write)
    P2 → EN   (Enable strobe)
    P3 → BL   (Backlight control)
    P4 → D4
    P5 → D5
    P6 → D6
    P7 → D7
"""

from __future__ import annotations

import time

try:
    from smbus2 import SMBus
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "smbus2 is required: pip install smbus2"
    ) from exc

from .exceptions import I2CError

# ---------------------------------------------------------------------------
# PCF8574 pin masks
# ---------------------------------------------------------------------------
_RS = 0x01  # Register Select
_RW = 0x02  # Read/Write (kept 0 = write)
_EN = 0x04  # Enable
_BL = 0x08  # Backlight

# ---------------------------------------------------------------------------
# HD44780 command bytes
# ---------------------------------------------------------------------------
_CMD_CLEAR    = 0x01
_CMD_HOME     = 0x02
_CMD_ENTRY    = 0x04
_CMD_DISPLAY  = 0x08
_CMD_FUNCTION = 0x20
_CMD_DDRAM    = 0x80

# Function-set flags
_F_4BIT  = 0x00
_F_2LINE = 0x08
_F_5x8   = 0x00

# Display-control flags
_D_ON  = 0x04

# Entry-mode flags
_E_LEFT      = 0x02
_E_NO_SHIFT  = 0x00

# Timing (seconds) — kept conservative for 3.3 V / 5 V compatibility
_DELAY_POWER_ON  = 0.05
_DELAY_INIT_LONG = 0.0045
_DELAY_INIT_STD  = 0.00015
_DELAY_ENABLE    = 0.0005   # EN high
_DELAY_SETTLE    = 0.0001   # EN low → next nibble
_DELAY_CLEAR     = 0.002    # clear / home command settle


class PCF8574Driver:
    """HD44780 driver using a PCF8574 I2C I/O expander.

    Args:
        address: I2C address of the PCF8574 expander (e.g. ``0x27``).
        cols: Number of character columns on the physical display.
        port: Linux I2C bus number (default ``1`` = ``/dev/i2c-1``).
        backlight: Whether to switch the backlight on at startup.
    """

    # DDRAM row start addresses (rows 2 & 3 depend on column count)
    _ROW_OFFSETS_BASE = [0x00, 0x40]

    def __init__(
        self,
        address: int,
        cols: int,
        port: int = 1,
        backlight: bool = True,
    ) -> None:
        self._address = address
        self._cols = cols
        self._backlight_mask = _BL if backlight else 0
        try:
            self._bus = SMBus(port)
        except OSError as exc:
            raise I2CError(f"Cannot open I2C bus {port}: {exc}") from exc
        self._row_offsets: list[int] = [
            0x00,
            0x40,
            cols,
            0x40 + cols,
        ]
        self._initialize()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Release the I2C bus."""
        self._bus.close()

    def clear(self) -> None:
        """Clear the display and return cursor to home."""
        self._command(_CMD_CLEAR)
        time.sleep(_DELAY_CLEAR)

    def home(self) -> None:
        """Return cursor to row 0, column 0 without clearing."""
        self._command(_CMD_HOME)
        time.sleep(_DELAY_CLEAR)

    def set_cursor(self, row: int, col: int = 0) -> None:
        """Move cursor to *row*, *col* (both zero-based)."""
        address = self._row_offsets[row] + col
        self._command(_CMD_DDRAM | address)

    def write_char(self, char: str) -> None:
        """Write a single character at the current cursor position."""
        self._write(ord(char), _RS)

    def write_string(self, text: str) -> None:
        """Write every character of *text* at the current cursor position."""
        for char in text:
            self.write_char(char)

    def set_backlight(self, on: bool) -> None:
        """Turn the backlight on (``True``) or off (``False``)."""
        self._backlight_mask = _BL if on else 0
        self._write_byte(self._backlight_mask)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _write_byte(self, data: int) -> None:
        try:
            self._bus.write_byte(self._address, data)
        except OSError as exc:
            raise I2CError(f"I2C write error at address 0x{self._address:02X}: {exc}") from exc

    def _pulse_enable(self, data: int) -> None:
        self._write_byte(data | _EN)
        time.sleep(_DELAY_ENABLE)
        self._write_byte(data & ~_EN)
        time.sleep(_DELAY_SETTLE)

    def _write_nibble(self, nibble: int, mode: int) -> None:
        data = ((nibble & 0x0F) << 4) | mode | self._backlight_mask
        self._pulse_enable(data)

    def _write(self, value: int, mode: int = 0) -> None:
        """Send *value* as two 4-bit nibbles (high nibble first)."""
        self._write_nibble(value >> 4, mode)
        self._write_nibble(value & 0x0F, mode)

    def _command(self, cmd: int) -> None:
        self._write(cmd, 0)

    def _initialize(self) -> None:
        """HD44780 initialisation sequence for 4-bit mode (§ 4 of datasheet)."""
        time.sleep(_DELAY_POWER_ON)

        # Three 8-bit "function set" pulses to guarantee a known state
        for i, delay in enumerate([_DELAY_INIT_LONG, _DELAY_INIT_LONG, _DELAY_INIT_STD]):
            self._write_nibble(0x03, 0)
            time.sleep(delay)

        # Switch to 4-bit mode
        self._write_nibble(0x02, 0)

        # Configure: 4-bit bus, 2-line mode, 5×8 font
        self._command(_CMD_FUNCTION | _F_4BIT | _F_2LINE | _F_5x8)
        # Display on, cursor off, blink off
        self._command(_CMD_DISPLAY | _D_ON)
        # Clear and go home
        self.clear()
        # Entry mode: cursor moves right, display does not shift
        self._command(_CMD_ENTRY | _E_LEFT | _E_NO_SHIFT)
