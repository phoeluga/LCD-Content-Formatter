"""HD44780 display controller with frame-based content management."""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass

from ._driver import PCF8574Driver
from .frame import Frame, FrameRow


class HD44780:
    """HD44780 LCD controller with scrolling, pagination, prefix/postfix support.

    This class drives an HD44780-compatible LCD via a PCF8574 I2C expander.
    It does *not* depend on RPLCD — communication is handled natively through
    :mod:`smbus2`.

    Args:
        i2c_expander: Expander IC type string. Currently only ``"PCF8574"``
            is supported.
        address: I2C address of the expander (e.g. ``0x27``).
        cols: Number of character columns on the physical display.
        rows: Number of character rows on the physical display.
        port: Linux I2C bus number (default ``1`` → ``/dev/i2c-1``).
        backlight: Whether to turn on the backlight at startup.

    Example::

        from lcd_content_formatter import HD44780

        lcd = HD44780("PCF8574", 0x27, cols=20, rows=4)

        frame = lcd.Frame()
        row_temp = frame.add("temp", "-", prefix="Temp: ", postfix=" °C")

        row_temp.text = "23.5"
        frame.update_row(row_temp)
        lcd.scroll_frame(frame)
        lcd.close()
    """

    # Expose Frame as a class attribute so ``lcd.Frame()`` still works
    # (backward-compatible with v1 usage pattern).
    Frame = Frame

    def __init__(
        self,
        i2c_expander: str,
        address: int,
        cols: int,
        rows: int,
        port: int = 1,
        backlight: bool = True,
    ) -> None:
        if i2c_expander.upper() != "PCF8574":
            raise ValueError(
                f"Unsupported I2C expander '{i2c_expander}'. Currently only 'PCF8574' is supported."
            )
        self._cols = cols
        self._rows = rows
        self._driver = PCF8574Driver(address=address, cols=cols, port=port, backlight=backlight)
        self._current_page: int = 1

    # ------------------------------------------------------------------
    # Resource management
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Release the I2C bus. Call when finished with the display."""
        self._driver.close()

    def __enter__(self) -> HD44780:
        return self

    def __exit__(self, *_) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------

    def _page_count(self, frame: Frame) -> int:
        n = len(frame)
        pages, remainder = divmod(n, self._rows)
        return pages + (1 if remainder else 0)

    def _page_range(self, frame: Frame, page: int) -> range:
        """Return the row-index slice for *page* (1-based)."""
        start = (page - 1) * self._rows
        end = min(page * self._rows, len(frame))
        return range(start, end)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write_frame(self, frame: Frame, page: int = 1, _scrolling: bool = False) -> None:
        """Render one page of *frame* to the LCD.

        Args:
            frame: The :class:`~lcd_content_formatter.Frame` to display.
            page: 1-based page number. Defaults to ``1``.
            _scrolling: Internal flag used by :meth:`scroll_frame`. When
                ``True`` the postfix is omitted because :meth:`scroll_frame`
                embeds it in the sliding text window. Do not set this manually.
        """
        if self._current_page != page:
            self._driver.clear()
        self._current_page = page

        all_rows = frame.rows()
        page_range = self._page_range(frame, page)

        for display_row, row_idx in enumerate(page_range):
            row = all_rows[row_idx]
            if _scrolling:
                text = row.prefix + row.text
            else:
                text = row.prefix + row.text + row.postfix

            self._driver.set_cursor(display_row)
            self._driver.write_string(text.ljust(self._cols)[: self._cols])

        # Blank any unused display rows below the content
        for display_row in range(len(page_range), self._rows):
            self._driver.set_cursor(display_row)
            self._driver.write_string(" " * self._cols)

    def scroll_frame(
        self,
        frame: Frame,
        scroll_in: bool = False,
        scroll_to_blank: bool = False,
        scroll_if_fit: bool = False,
        delay: float = 0.5,
        show_first_after_scroll: bool = True,
    ) -> None:
        """Display *frame* with optional horizontal scrolling.

        Text that is longer than the display width scrolls left automatically.
        When multiple pages exist, each page is scrolled in sequence.

        Args:
            frame: The :class:`~lcd_content_formatter.Frame` to display.
            scroll_in: When ``True``, text enters from the right edge instead
                of starting fully visible.
            scroll_to_blank: When ``True``, text scrolls fully off the left
                edge before moving to the next page. Otherwise scrolling stops
                once all text is visible.
            scroll_if_fit: When ``True``, apply the ``scroll_in`` /
                ``scroll_to_blank`` animation even for rows that would fit
                on-screen without scrolling.
            delay: Seconds to wait between each scroll step (controls speed).
            show_first_after_scroll: When ``True`` (default), reset the display
                to page 1 of *frame* after all pages have been shown.
        """

        @dataclass
        class _ScrollState:
            padding: str  # Leading blank padding for scroll_in effect
            pos: int  # Current window offset into the constructed text

        all_rows = frame.rows()
        tmp_frame = copy.deepcopy(frame)
        tmp_rows = tmp_frame.rows()

        # Pre-compute per-row padding (only relevant for scroll_in)
        states: list[_ScrollState] = []
        for row in all_rows:
            if scroll_in and (
                scroll_if_fit or (len(row.prefix) + len(row.text) + len(row.postfix) > self._cols)
            ):
                padding = " " * (self._cols - len(row.prefix))
            else:
                padding = ""
            states.append(_ScrollState(padding=padding, pos=0))

        for page in range(1, self._page_count(frame) + 1):
            page_range = self._page_range(frame, page)

            max_iters = self._max_scroll_iterations(
                all_rows, page_range, states, scroll_in, scroll_to_blank
            )

            if max_iters <= 0:
                # Content fits — display statically and pause
                self.write_frame(frame, page)
                time.sleep(delay * 2)
                continue

            for _ in range(max_iters):
                for ri in page_range:
                    row = all_rows[ri]
                    state = states[ri]
                    spaces_left = 0
                    if scroll_if_fit:
                        spaces_left = max(
                            0,
                            self._cols - (len(row.prefix) + len(row.text) + len(row.postfix)),
                        )

                    self._maybe_reset_state(
                        ri,
                        row,
                        state,
                        tmp_rows,
                        states,
                        scroll_in,
                        scroll_to_blank,
                        scroll_if_fit,
                        spaces_left,
                    )

                    # Build the text window and advance the scroll position
                    window_text = (
                        state.padding + row.text + row.postfix + state.padding + " " * spaces_left
                    )
                    tmp_rows[ri].text = window_text[state.pos : state.pos + self._cols]

                    should_advance = scroll_if_fit and (scroll_in or scroll_to_blank)
                    if not should_advance:
                        should_advance = (
                            len(row.text) + len(row.postfix) + len(row.prefix) > self._cols
                        )
                    if should_advance:
                        state.pos += 1

                self.write_frame(tmp_frame, page, _scrolling=True)
                time.sleep(delay)

            if not scroll_to_blank:
                time.sleep(delay * 2)

        if show_first_after_scroll:
            self.write_frame(frame)

    # ------------------------------------------------------------------
    # Backward-compatible aliases (v1 API)
    # ------------------------------------------------------------------

    def writeFrame(
        self, framebuffer: Frame, pageNumber: int = 1, scrollingFrame: bool = False
    ) -> None:
        """Deprecated alias for :meth:`write_frame`."""
        return self.write_frame(framebuffer, pageNumber, scrollingFrame)

    def scrollFrame(
        self,
        framebuffer: Frame,
        scrollIn: bool = False,
        scrollToBlank: bool = False,
        scrollIfFit: bool = False,
        delay: float = 0.5,
        showFirstFrameAfterScroll: bool = True,
    ) -> None:
        """Deprecated alias for :meth:`scroll_frame`."""
        return self.scroll_frame(
            framebuffer, scrollIn, scrollToBlank, scrollIfFit, delay, showFirstFrameAfterScroll
        )

    # ------------------------------------------------------------------
    # Internal scroll helpers
    # ------------------------------------------------------------------

    def _max_scroll_iterations(
        self,
        all_rows,
        page_range,
        states,
        scroll_in: bool,
        scroll_to_blank: bool,
    ) -> int:
        """Calculate the number of animation frames needed for this page."""
        if scroll_in:
            if scroll_to_blank:
                return max(
                    len(all_rows[ri].text) + 1 + (self._cols - len(all_rows[ri].prefix))
                    for ri in page_range
                )
            else:
                return max(
                    len(all_rows[ri].text) + len(all_rows[ri].postfix) + 1 for ri in page_range
                )
        else:
            if scroll_to_blank:
                return max(
                    len(all_rows[ri].text) + len(all_rows[ri].postfix) + 1 for ri in page_range
                )
            else:
                return max(
                    len(all_rows[ri].text)
                    + len(all_rows[ri].postfix)
                    + len(all_rows[ri].prefix)
                    - self._cols
                    + 1
                    for ri in page_range
                )

    def _maybe_reset_state(
        self,
        ri: int,
        row: FrameRow,
        state,
        tmp_rows,
        states,
        scroll_in: bool,
        scroll_to_blank: bool,
        scroll_if_fit: bool,
        spaces_left: int,
    ) -> None:
        """Reset the scroll position for *ri* if it has gone past the end."""
        if scroll_to_blank:
            padding_len = len(state.padding) * scroll_in - scroll_in
            limit = padding_len + len(row.text) + len(row.postfix) + spaces_left
            if state.pos + spaces_left > limit:
                state.pos = 0
                tmp_rows[ri].text = row.text
                tmp_rows[ri].prefix = row.prefix
                tmp_rows[ri].postfix = row.postfix
        else:
            padding_factor = int(scroll_in) + int(scroll_to_blank)
            limit = (
                len(state.padding) * padding_factor
                + len(row.text)
                + len(row.postfix)
                + len(row.prefix)
                - self._cols
            )
            if state.pos - spaces_left > limit:
                state.pos = 0
                tmp_rows[ri].text = row.text
                tmp_rows[ri].prefix = row.prefix
                tmp_rows[ri].postfix = row.postfix
