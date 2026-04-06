# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
\-
### Fixed
\-

---

## [2.0.1] — 2026-04-06

### Fixed
- Resolved ruff lint errors: replaced deprecated `typing.List` / `typing.Dict` with built-in generics (`list`, `dict`), removed unused imports (`I2CError` in `display.py`, `field` in `frame.py`), removed quoted return type annotation in `HD44780.__enter__`
- Applied ruff auto-formatter to bring all source files to consistent style

### Added
- `workflow_dispatch` trigger added to the CI workflow so it can be re-run manually from the GitHub Actions UI

---

## [2.0.0] — 2026-04-05

Complete rewrite with proper Python packaging and no RPLCD dependency.

### Added
- `lcd_content_formatter` Python package, installable from PyPI via `pip install lcd-content-formatter`
- Direct HD44780 driver over PCF8574 I2C expander using `smbus2` — RPLCD is no longer required
- `pyproject.toml` with full PyPI metadata, Hatchling build backend, and Ruff linting config
- Type hints throughout the public API
- `FrameRow.full_text` property returning `prefix + text + postfix`
- `Frame.__len__`, `Frame.__iter__` dunder methods
- `Frame.add_with_guid`, `Frame.get_row`, `Frame.remove`, `Frame.update_row` snake_case methods
- `HD44780.scroll_frame`, `HD44780.write_frame` snake_case methods
- Context-manager support: `with HD44780(...) as lcd:`
- `I2CError`, `FrameRowNotFoundError`, `DuplicateFrameRowError` exceptions
- 61-test suite with full mock-based coverage (no hardware required)
- GitHub Actions CI workflow: lint (ruff) + test matrix Python 3.8–3.12
- GitHub Actions Release workflow: build → PyPI trusted publishing (OIDC) → GitHub Release
- `RELEASING.md` — step-by-step release and deployment guide

### Changed
- Package entry point: `from lcd_content_formatter import HD44780` (was `from HD44780 import HD44780`)
- `HD44780.__init__` parameters reordered to remove RPLCD-inherited kwargs; `cols` and `rows` are now explicit keyword arguments

### Fixed
- Scrolling reset condition off-by-one when both `scroll_in` and `scroll_to_blank` are active (inherited bug from v1)

### Backward compatible
- All v1 method names (`scrollFrame`, `writeFrame`, `addWithGuid`, `getFrame`, `removeByIndex`, `updateFrameRow`) are kept as deprecated aliases

---

## [1.0.2103.0601]

### Fixed
- Fixed an issue where the maximum iterations were wrong when scrolled in and scrolled to blank simultaneously.

## [1.0.2103.0401]

### Fixed
- Fixed scrolling issue related to the introduction of the `postfix` field.

## [1.0.2102.1401]

Initial release.

---

[Unreleased]: https://github.com/rednoid/LCD-Content-Formatter/compare/v2.0.1...HEAD
[2.0.1]: https://github.com/rednoid/LCD-Content-Formatter/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/rednoid/LCD-Content-Formatter/compare/v1.0.2103.0601...v2.0.0
[1.0.2103.0601]: https://github.com/rednoid/LCD-Content-Formatter/compare/v1.0.2103.0401...v1.0.2103.0601
[1.0.2103.0401]: https://github.com/rednoid/LCD-Content-Formatter/compare/v1.0.2102.1401...v1.0.2103.0401
[1.0.2102.1401]: https://github.com/rednoid/LCD-Content-Formatter/compare/v1.0.0.0...v1.0.2102.1401
