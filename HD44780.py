"""Backward-compatibility shim for v1 users.

.. deprecated::
    Import from ``lcd_content_formatter`` instead::

        from lcd_content_formatter import HD44780

    This file will be removed in a future release.
"""

import warnings

warnings.warn(
    "Importing from 'HD44780' is deprecated and will be removed in a future version. "
    "Use 'from lcd_content_formatter import HD44780' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from lcd_content_formatter import HD44780  # noqa: F401, E402

__all__ = ["HD44780"]
