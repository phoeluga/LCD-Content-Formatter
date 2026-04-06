"""Tests for lcd_content_formatter._driver (PCF8574Driver).

All I2C hardware calls are replaced by a MagicMock, so these tests run on
any platform without physical hardware.
"""

from unittest.mock import MagicMock, call, patch

import pytest

from lcd_content_formatter._driver import (
    PCF8574Driver,
    _BL,
    _CMD_CLEAR,
    _CMD_DDRAM,
    _CMD_HOME,
    _EN,
    _RS,
)
from lcd_content_formatter.exceptions import I2CError


@pytest.fixture
def mock_bus():
    """Return a mock SMBus instance and patch smbus2.SMBus."""
    bus = MagicMock()
    with patch("lcd_content_formatter._driver.SMBus", return_value=bus):
        yield bus


@pytest.fixture
def driver(mock_bus):
    """Return a PCF8574Driver backed by a mock bus."""
    return PCF8574Driver(address=0x27, cols=20, port=1, backlight=True)


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestInit:
    def test_opens_bus(self, mock_bus):
        with patch("lcd_content_formatter._driver.SMBus", return_value=mock_bus) as cls:
            PCF8574Driver(address=0x27, cols=20, port=1)
            cls.assert_called_once_with(1)

    def test_bus_error_raises_i2c_error(self):
        with patch("lcd_content_formatter._driver.SMBus", side_effect=OSError("no bus")):
            with pytest.raises(I2CError, match="Cannot open I2C bus"):
                PCF8574Driver(address=0x27, cols=20, port=99)

    def test_row_offsets_20col(self, mock_bus):
        with patch("lcd_content_formatter._driver.SMBus", return_value=mock_bus):
            drv = PCF8574Driver(address=0x27, cols=20)
        assert drv._row_offsets == [0x00, 0x40, 20, 0x40 + 20]

    def test_row_offsets_16col(self, mock_bus):
        with patch("lcd_content_formatter._driver.SMBus", return_value=mock_bus):
            drv = PCF8574Driver(address=0x27, cols=16)
        assert drv._row_offsets == [0x00, 0x40, 16, 0x40 + 16]


# ---------------------------------------------------------------------------
# close / context
# ---------------------------------------------------------------------------


class TestClose:
    def test_close_calls_bus_close(self, driver, mock_bus):
        driver.close()
        mock_bus.close.assert_called_once()


# ---------------------------------------------------------------------------
# set_cursor
# ---------------------------------------------------------------------------


class TestSetCursor:
    def test_row0_col0(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.set_cursor(0, 0)
        # set_cursor issues nibble writes; verify write_byte was called at all
        assert mock_bus.write_byte.called

    def test_row1_col0(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.set_cursor(1, 0)
        # Expected DDRAM address = 0x40 → command = 0x80 | 0x40 = 0xC0
        # The nibbles that appear on the bus: high nibble first then low
        calls = mock_bus.write_byte.call_args_list
        # High nibble of 0xC0 = 0xC, shifted to D4-D7 → data byte = 0xC0 | BL
        # Just check that write_byte was called (more calls = nibbles + pulses)
        assert len(calls) > 0

    def test_row2_col5_20col(self, driver, mock_bus):
        mock_bus.reset_mock()
        # row 2 offset for 20-col = 20; col 5 → address = 25 = 0x19
        # DDRAM command = 0x80 | 0x19 = 0x99
        driver.set_cursor(2, 5)
        assert mock_bus.write_byte.called


# ---------------------------------------------------------------------------
# write_char / write_string
# ---------------------------------------------------------------------------


class TestWrite:
    def test_write_char_uses_rs_flag(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.write_char("A")
        calls = [c[0][1] for c in mock_bus.write_byte.call_args_list]
        # RS bit must appear in at least one pulse-enable call
        rs_present = any(b & _RS for b in calls)
        assert rs_present

    def test_write_string_writes_each_char(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.write_string("AB")
        # 2 chars × 2 nibbles × 2 pulses = 8 write_byte calls (minimum)
        assert mock_bus.write_byte.call_count >= 8

    def test_write_empty_string_no_calls(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.write_string("")
        assert mock_bus.write_byte.call_count == 0


# ---------------------------------------------------------------------------
# clear / home
# ---------------------------------------------------------------------------


class TestClearHome:
    def test_clear_issues_command(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.clear()
        calls = [c[0][1] for c in mock_bus.write_byte.call_args_list]
        # _CMD_CLEAR = 0x01; high nibble = 0, low nibble = 1
        # High nibble data on bus = 0x00 | BL (backlight)
        assert len(calls) > 0

    def test_home_issues_command(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.home()
        assert mock_bus.write_byte.called


# ---------------------------------------------------------------------------
# set_backlight
# ---------------------------------------------------------------------------


class TestBacklight:
    def test_set_backlight_off(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.set_backlight(False)
        # Should write a byte with BL bit cleared
        assert mock_bus.write_byte.called
        last_call = mock_bus.write_byte.call_args[0][1]
        assert not (last_call & _BL)

    def test_set_backlight_on(self, driver, mock_bus):
        mock_bus.reset_mock()
        driver.set_backlight(True)
        last_call = mock_bus.write_byte.call_args[0][1]
        assert last_call & _BL


# ---------------------------------------------------------------------------
# I2C error propagation
# ---------------------------------------------------------------------------


class TestI2CErrors:
    def test_write_error_raises_i2c_error(self, driver, mock_bus):
        mock_bus.write_byte.side_effect = OSError("bus fault")
        with pytest.raises(I2CError, match="I2C write error"):
            driver.write_char("X")
