# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
- Initial structure for the changelog.
- AuthorService for searching authors.
- Example script demonstrating AuthorService usage.
- Documentation for pagination and asynchronous usage examples.
- List of stable public API exports.
### Fixed
- Avoided ``httpx`` deprecation warning when posting raw bytes or text.

### Changed
- Removed the standalone lint workflow and moved Ruff earlier in the CI job.
- Added a dedicated step to install Ruff before running linting.
- Fixed installation command for Ruff to target the system environment.
- Standardized logging statements to use parameterized style instead of f-strings.

## [0.1.0] - 2025-07-30
### Added
- Initial release.
