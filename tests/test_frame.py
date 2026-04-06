"""Tests for lcd_content_formatter.frame."""

import pytest

from lcd_content_formatter.exceptions import DuplicateFrameRowError, FrameRowNotFoundError
from lcd_content_formatter.frame import Frame, FrameRow

# ---------------------------------------------------------------------------
# FrameRow
# ---------------------------------------------------------------------------


class TestFrameRow:
    def test_full_text_all_parts(self):
        row = FrameRow(id="r", text="23.5", prefix="Temp: ", postfix=" °C")
        assert row.full_text == "Temp: 23.5 °C"

    def test_full_text_text_only(self):
        row = FrameRow(id="r", text="Hello")
        assert row.full_text == "Hello"

    def test_full_text_empty(self):
        row = FrameRow(id="r")
        assert row.full_text == ""


# ---------------------------------------------------------------------------
# Frame.add / add_with_guid
# ---------------------------------------------------------------------------


class TestFrameAdd:
    def test_add_returns_row(self):
        frame = Frame()
        row = frame.add("id1", text="hello", prefix="p", postfix="q")
        assert isinstance(row, FrameRow)
        assert row.id == "id1"
        assert row.text == "hello"
        assert row.prefix == "p"
        assert row.postfix == "q"

    def test_add_stores_row(self):
        frame = Frame()
        frame.add("id1", "hello")
        assert len(frame) == 1

    def test_add_duplicate_raises(self):
        frame = Frame()
        frame.add("id1")
        with pytest.raises(DuplicateFrameRowError):
            frame.add("id1")

    def test_add_with_guid_unique_ids(self):
        frame = Frame()
        r1 = frame.add_with_guid("a")
        r2 = frame.add_with_guid("b")
        assert r1.id != r2.id
        assert len(frame) == 2

    def test_add_with_guid_backward_compat(self):
        frame = Frame()
        row = frame.addWithGuid("hello", "pre", "post")
        assert row.text == "hello"
        assert row.prefix == "pre"
        assert row.postfix == "post"


# ---------------------------------------------------------------------------
# Frame.get_row
# ---------------------------------------------------------------------------


class TestFrameGetRow:
    def test_get_existing_row(self):
        frame = Frame()
        added = frame.add("x", "val")
        retrieved = frame.get_row("x")
        assert retrieved is added

    def test_get_missing_creates_empty(self):
        frame = Frame()
        row = frame.get_row("new_id")
        assert row.id == "new_id"
        assert row.text == ""
        assert len(frame) == 1

    def test_get_missing_raises_when_no_create(self):
        frame = Frame()
        with pytest.raises(FrameRowNotFoundError):
            frame.get_row("missing", create_if_missing=False)

    def test_backward_compat_getFrame(self):
        frame = Frame()
        frame.add("k", "v")
        row = frame.getFrame("k")
        assert row.text == "v"


# ---------------------------------------------------------------------------
# Frame.remove
# ---------------------------------------------------------------------------


class TestFrameRemove:
    def test_remove_existing(self):
        frame = Frame()
        frame.add("a")
        frame.remove("a")
        assert len(frame) == 0

    def test_remove_missing_raises(self):
        frame = Frame()
        with pytest.raises(FrameRowNotFoundError):
            frame.remove("nope")

    def test_backward_compat_removeByIndex(self):
        frame = Frame()
        frame.add("a")
        frame.removeByIndex("a")
        assert len(frame) == 0


# ---------------------------------------------------------------------------
# Frame.update_row
# ---------------------------------------------------------------------------


class TestFrameUpdateRow:
    def test_update_existing_row(self):
        frame = Frame()
        row = frame.add("u", "old")
        row.text = "new"
        frame.update_row(row)
        assert frame.get_row("u").text == "new"

    def test_update_missing_raises(self):
        frame = Frame()
        row = FrameRow(id="ghost", text="x")
        with pytest.raises(FrameRowNotFoundError):
            frame.update_row(row)

    def test_backward_compat_updateFrameRow(self):
        frame = Frame()
        row = frame.add("u", "old")
        row.text = "updated"
        frame.updateFrameRow(row)
        assert frame.get_row("u").text == "updated"


# ---------------------------------------------------------------------------
# Frame.clear
# ---------------------------------------------------------------------------


class TestFrameClear:
    def test_clear_removes_all_rows(self):
        frame = Frame()
        frame.add("a")
        frame.add("b")
        frame.add("c")
        frame.clear()
        assert len(frame) == 0

    def test_clear_empty_frame_is_noop(self):
        frame = Frame()
        frame.clear()
        assert len(frame) == 0


# ---------------------------------------------------------------------------
# Frame.rows / iteration
# ---------------------------------------------------------------------------


class TestFrameRows:
    def test_rows_returns_ordered_list(self):
        frame = Frame()
        frame.add("a", "A")
        frame.add("b", "B")
        frame.add("c", "C")
        texts = [r.text for r in frame.rows()]
        assert texts == ["A", "B", "C"]

    def test_iteration_order(self):
        frame = Frame()
        frame.add("x", "1")
        frame.add("y", "2")
        ids = [r.id for r in frame]
        assert ids == ["x", "y"]
