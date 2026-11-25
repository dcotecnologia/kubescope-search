# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.0] - 2026-11-25

### Changed

- The extension imports nothing from `PySide6`, in its code or in its tests: its page is a plain object that holds its widget, and every widget, timer, icon, text and test helper comes from the SDK (`ctx.ui.components`, `translate`) by @danilogco

## [1.0.1] - 2026-11-20

### Fixed

- Update the locked dependencies and the pre-commit hooks by @danilogco

## [1.0.0] - 2026-11-20

### Added

- The global search of KubeScope as an extension written against the SDK only: `/` and `Ctrl+K` find a screen, a list or a resource of any namespace by its name and open it

[Unreleased]: https://github.com/dcotecnologia/kubescope-search/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/dcotecnologia/kubescope-search/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/dcotecnologia/kubescope-search/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/dcotecnologia/kubescope-search/releases/tag/v1.0.0
