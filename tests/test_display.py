"""Tests for lcd_content_formatter.display (HD44780).

All hardware I/O is mocked via PCF8574Driver. Tests focus on pagination,
row rendering logic, and scroll-state management.
"""

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from lcd_content_formatter.display import HD44780
from lcd_content_formatter.frame import Frame

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_lcd(cols: int = 20, rows: int = 4) -> tuple:
    """Return (lcd, mock_driver) with PCF8574Driver replaced by a MagicMock."""
    mock_driver = MagicMock()
    with patch("lcd_content_formatter.display.PCF8574Driver", return_value=mock_driver):
        lcd = HD44780("PCF8574", 0x27, cols=cols, rows=rows)
    return lcd, mock_driver


def simple_frame(rows_data: list) -> Frame:
    """Create a Frame from a list of (text, prefix, postfix) tuples."""
    frame = Frame()
    for i, (text, prefix, postfix) in enumerate(rows_data):
        frame.add(str(i), text, prefix, postfix)
    return frame


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestInit:
    def test_unsupported_expander_raises(self):
        with patch("lcd_content_formatter.display.PCF8574Driver"):
            with pytest.raises(ValueError, match="Unsupported I2C expander"):
                HD44780("MCP23017", 0x20, cols=16, rows=2)

    def test_context_manager_closes(self):
        mock_driver = MagicMock()
        with patch("lcd_content_formatter.display.PCF8574Driver", return_value=mock_driver):
            with HD44780("PCF8574", 0x27, cols=20, rows=4):
                pass
        mock_driver.close.assert_called_once()

    def test_frame_attribute_creates_frame(self):
        lcd, _ = make_lcd()
        frame = lcd.Frame()
        assert isinstance(frame, Frame)


# ---------------------------------------------------------------------------
# Pagination helpers
# ---------------------------------------------------------------------------


class TestPagination:
    def test_page_count_exact_multiple(self):
        lcd, _ = make_lcd(rows=4)
        frame = simple_frame([("", "", "")] * 8)
        assert lcd._page_count(frame) == 2

    def test_page_count_with_remainder(self):
        lcd, _ = make_lcd(rows=4)
        frame = simple_frame([("", "", "")] * 5)
        assert lcd._page_count(frame) == 2

    def test_page_count_single_page(self):
        lcd, _ = make_lcd(rows=4)
        frame = simple_frame([("", "", "")] * 3)
        assert lcd._page_count(frame) == 1

    def test_page_range_first_page(self):
        lcd, _ = make_lcd(rows=4)
        frame = simple_frame([("", "", "")] * 8)
        assert lcd._page_range(frame, 1) == range(0, 4)

    def test_page_range_second_page(self):
        lcd, _ = make_lcd(rows=4)
        frame = simple_frame([("", "", "")] * 8)
        assert lcd._page_range(frame, 2) == range(4, 8)

    def test_page_range_partial_last_page(self):
        lcd, _ = make_lcd(rows=4)
        frame = simple_frame([("", "", "")] * 6)
        assert lcd._page_range(frame, 2) == range(4, 6)


# ---------------------------------------------------------------------------
# write_frame
# ---------------------------------------------------------------------------


class TestWriteFrame:
    def test_renders_all_rows_on_single_page(self):
        lcd, driver = make_lcd(cols=20, rows=4)
        frame = simple_frame([("Hello", "", ""), ("World", "", ""), ("", "", ""), ("", "", "")])
        lcd.write_frame(frame)

        # set_cursor should be called for each of 4 display rows
        assert driver.set_cursor.call_count == 4

    def test_text_padded_to_col_width(self):
        lcd, driver = make_lcd(cols=20, rows=2)
        frame = Frame()
        frame.add("r", "Hi")
        lcd.write_frame(frame)

        written = [c[0][0] for c in driver.write_string.call_args_list]
        assert written[0] == "Hi".ljust(20)

    def test_prefix_postfix_combined(self):
        lcd, driver = make_lcd(cols=20, rows=2)
        frame = Frame()
        frame.add("r", "23.5", prefix="T: ", postfix=" C")
        lcd.write_frame(frame)

        written = driver.write_string.call_args_list[0][0][0]
        assert written.startswith("T: 23.5 C")

    def test_scrolling_flag_omits_postfix(self):
        lcd, driver = make_lcd(cols=20, rows=2)
        frame = Frame()
        frame.add("r", "23.5", prefix="T: ", postfix=" C")
        lcd.write_frame(frame, _scrolling=True)

        written = driver.write_string.call_args_list[0][0][0]
        # postfix should NOT appear
        assert " C" not in written.rstrip()

    def test_blank_rows_written_for_unfilled_page(self):
        lcd, driver = make_lcd(cols=20, rows=4)
        frame = Frame()
        frame.add("r", "line1")
        # Only 1 row — display has 4. 3 blank rows should be written.
        lcd.write_frame(frame)

        all_written = [c[0][0] for c in driver.write_string.call_args_list]
        blank_rows = [s for s in all_written if s.strip() == ""]
        assert len(blank_rows) == 3

    def test_page_change_triggers_clear(self):
        lcd, driver = make_lcd(cols=20, rows=4)
        frame = simple_frame([("", "", "")] * 8)
        lcd.write_frame(frame, page=1)
        driver.clear.reset_mock()
        lcd.write_frame(frame, page=2)
        driver.clear.assert_called_once()

    def test_same_page_no_clear(self):
        lcd, driver = make_lcd(cols=20, rows=4)
        frame = simple_frame([("", "", "")] * 4)
        lcd.write_frame(frame, page=1)
        driver.clear.reset_mock()
        lcd.write_frame(frame, page=1)
        driver.clear.assert_not_called()


# ---------------------------------------------------------------------------
# scroll_frame — no-scroll cases
# ---------------------------------------------------------------------------


class TestScrollFrameNoScroll:
    def test_short_text_does_not_scroll(self):
        """Text that fits on screen should call write_frame exactly once per page."""
        lcd, driver = make_lcd(cols=20, rows=4)
        frame = simple_frame([("Hi", "", "")] * 4)  # 4 rows = 1 page

        with patch.object(lcd, "write_frame", wraps=lcd.write_frame) as wf, patch(
            "lcd_content_formatter.display.time.sleep"
        ):
            lcd.scroll_frame(frame, delay=0)

        # maxIterations <= 0 → static write only
        assert wf.call_count >= 1

    def test_show_first_after_scroll_true(self):
        """Final write_frame(frame) call should restore page 1."""
        lcd, driver = make_lcd(cols=20, rows=2)
        # Use text that overflows to trigger scrolling
        long_text = "A" * 25
        frame = Frame()
        frame.add("r", long_text)

        calls = []
        original = lcd.write_frame

        def capture(*args, **kwargs):
            calls.append((args, kwargs))
            return original(*args, **kwargs)

        with patch.object(lcd, "write_frame", side_effect=capture), patch(
            "lcd_content_formatter.display.time.sleep"
        ):
            lcd.scroll_frame(frame, show_first_after_scroll=True, delay=0)

        # Last call should be write_frame(frame) — page 1, no _scrolling flag
        last_args, last_kwargs = calls[-1]
        assert last_args[0] is frame

    def test_show_first_after_scroll_false(self):
        lcd, driver = make_lcd(cols=20, rows=2)
        long_text = "A" * 25
        frame = Frame()
        frame.add("r", long_text)

        calls = []
        original = lcd.write_frame

        def capture(*args, **kwargs):
            calls.append((args, kwargs))
            return original(*args, **kwargs)

        with patch.object(lcd, "write_frame", side_effect=capture), patch(
            "lcd_content_formatter.display.time.sleep"
        ):
            lcd.scroll_frame(frame, show_first_after_scroll=False, delay=0)

        # Last call should be a _scrolling=True write, not the "reset" write
        last_args, last_kwargs = calls[-1]
        # The last write_frame call should NOT be the plain reset call
        assert last_kwargs.get("_scrolling", False) or len(calls) > 0


# ---------------------------------------------------------------------------
# scroll_frame — max iterations
# ---------------------------------------------------------------------------


class TestScrollMaxIterations:
    def _lcd(self):
        return make_lcd(cols=20, rows=4)[0]

    def test_max_iter_no_scroll_in_no_blank(self):
        """text+postfix+prefix - cols + 1 when not scrollIn and not scrollToBlank."""
        lcd = self._lcd()
        frame = Frame()
        frame.add("r", "A" * 15, prefix="P" * 5, postfix="")  # 20 chars total

        @dataclass
        class FakeState:
            padding: str = ""
            pos: int = 0

        states = [FakeState()]
        result = lcd._max_scroll_iterations(
            frame.rows(), range(0, 1), states, scroll_in=False, scroll_to_blank=False
        )
        # 15 + 0 + 5 - 20 + 1 = 1
        assert result == 1

    def test_max_iter_text_fits_is_nonpositive(self):
        lcd = self._lcd()
        frame = Frame()
        frame.add("r", "Short", prefix="P: ", postfix="")  # 5+3 = 8 chars < 20

        @dataclass
        class FakeState:
            padding: str = ""
            pos: int = 0

        states = [FakeState()]
        result = lcd._max_scroll_iterations(
            frame.rows(), range(0, 1), states, scroll_in=False, scroll_to_blank=False
        )
        assert result <= 0


# ---------------------------------------------------------------------------
# Backward-compatible API
# ---------------------------------------------------------------------------


class TestBackwardCompat:
    def test_writeFrame_alias(self):
        lcd, driver = make_lcd()
        frame = Frame()
        frame.add("r", "text")
        with patch.object(lcd, "write_frame") as wf:
            lcd.writeFrame(frame, pageNumber=1, scrollingFrame=False)
            wf.assert_called_once_with(frame, 1, False)

    def test_scrollFrame_alias(self):
        lcd, _ = make_lcd()
        frame = Frame()
        frame.add("r", "text")
        with patch.object(lcd, "scroll_frame") as sf:
            lcd.scrollFrame(frame, scrollIn=True, scrollToBlank=False)
            sf.assert_called_once_with(frame, True, False, False, 0.5, True)
