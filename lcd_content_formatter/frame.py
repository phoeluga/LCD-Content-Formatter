from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Iterator

from .exceptions import DuplicateFrameRowError, FrameRowNotFoundError


@dataclass
class FrameRow:
    """A single row of content to be displayed on the LCD.

    Attributes:
        id: Unique identifier for this row within its Frame.
        text: The dynamic value to display (the part that changes).
        prefix: Static text shown before ``text`` (e.g. ``"Temp: "``).
        postfix: Static text shown after ``text`` (e.g. ``" °C"``).
    """

    id: str
    text: str = ""
    prefix: str = ""
    postfix: str = ""

    @property
    def full_text(self) -> str:
        """Combined prefix + text + postfix."""
        return self.prefix + self.text + self.postfix


class Frame:
    """An ordered collection of :class:`FrameRow` objects to be rendered on the LCD.

    Rows are maintained in insertion order. If the number of rows exceeds the
    physical display height, :class:`~lcd_content_formatter.HD44780` automatically
    paginates them.
    """

    def __init__(self) -> None:
        self._rows: dict[str, FrameRow] = {}

    def __len__(self) -> int:
        return len(self._rows)

    def __iter__(self) -> Iterator[FrameRow]:
        return iter(self._rows.values())

    # ------------------------------------------------------------------
    # Row management
    # ------------------------------------------------------------------

    def add(
        self,
        id: str,
        text: str = "",
        prefix: str = "",
        postfix: str = "",
    ) -> FrameRow:
        """Add a row with an explicit ID.

        Args:
            id: Unique identifier for the row.
            text: Initial text value.
            prefix: Static prefix string.
            postfix: Static postfix string.

        Returns:
            The newly created :class:`FrameRow`.

        Raises:
            DuplicateFrameRowError: If *id* already exists in this frame.
        """
        if id in self._rows:
            raise DuplicateFrameRowError(f"Row with ID '{id}' already exists in this frame.")
        row = FrameRow(id=id, text=text, prefix=prefix, postfix=postfix)
        self._rows[id] = row
        return row

    def add_with_guid(
        self,
        text: str = "",
        prefix: str = "",
        postfix: str = "",
    ) -> FrameRow:
        """Add a row using an auto-generated UUID as the ID.

        Use this when you do not need to look up the row by a meaningful key
        later (e.g. static labels).

        Returns:
            The newly created :class:`FrameRow`.
        """
        return self.add(str(uuid.uuid4()), text, prefix, postfix)

    def get_row(self, id: str, create_if_missing: bool = True) -> FrameRow:
        """Retrieve a row by ID.

        Args:
            id: The row identifier.
            create_if_missing: When ``True`` (default) an empty row is created
                and returned if *id* is not found. When ``False`` a
                :class:`FrameRowNotFoundError` is raised instead.

        Returns:
            The matching :class:`FrameRow`.

        Raises:
            FrameRowNotFoundError: If *id* is not found and *create_if_missing*
                is ``False``.
        """
        row = self._rows.get(id)
        if row is not None:
            return row
        if create_if_missing:
            return self.add(id)
        raise FrameRowNotFoundError(f"Row with ID '{id}' not found in this frame.")

    def remove(self, id: str) -> None:
        """Remove a row by ID.

        Raises:
            FrameRowNotFoundError: If *id* does not exist.
        """
        if id not in self._rows:
            raise FrameRowNotFoundError(f"Row with ID '{id}' not found in this frame.")
        del self._rows[id]

    def update_row(self, row: FrameRow) -> None:
        """Replace an existing row with an updated :class:`FrameRow` object.

        The row is matched by ``row.id``.

        Raises:
            FrameRowNotFoundError: If the row's ID does not exist in this frame.
        """
        if row.id not in self._rows:
            raise FrameRowNotFoundError(f"Row with ID '{row.id}' not found in this frame.")
        self._rows[row.id] = row

    def clear(self) -> None:
        """Remove all rows from this frame."""
        self._rows.clear()

    def rows(self) -> list[FrameRow]:
        """Return all rows as an ordered list."""
        return list(self._rows.values())

    # ------------------------------------------------------------------
    # Backward-compatible aliases (v1 API)
    # ------------------------------------------------------------------

    def addWithGuid(self, text: str = "", prefix: str = "", postfix: str = "") -> FrameRow:
        """Deprecated alias for :meth:`add_with_guid`."""
        return self.add_with_guid(text, prefix, postfix)

    def getFrame(self, id: str, createEmptyRowIfIdNotExist: bool = True) -> FrameRow:
        """Deprecated alias for :meth:`get_row`."""
        return self.get_row(id, createEmptyRowIfIdNotExist)

    def removeByIndex(self, id: str) -> None:
        """Deprecated alias for :meth:`remove`."""
        return self.remove(id)

    def updateFrameRow(self, row: FrameRow) -> None:
        """Deprecated alias for :meth:`update_row`."""
        return self.update_row(row)
