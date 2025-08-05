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
- Introduced `AuthenticatedService` base class to centralize login validation for services requiring authentication.
- Pre-commit configuration for Ruff, formatting and tests.
- Security policy describing vulnerability reporting and secret management.
- Automated GitHub Pages workflow to build and deploy documentation.
- ``SkoobClient`` now forwards additional keyword arguments to ``httpx.Client`` for
  configuring timeouts, proxies and other options.
### Fixed
- Avoided ``httpx`` deprecation warning when posting raw bytes or text.
- Updated PyPI publish workflow to use the latest action release, resolving missing metadata errors.
- Installed `mkdocs-material` in the release workflow to resolve missing theme errors.
- Prevented release failures by skipping tag creation when the version tag already exists.

### Changed
- Removed the standalone lint workflow and moved Ruff earlier in the CI job.
- Added a dedicated step to install Ruff before running linting.
- Fixed installation command for Ruff to target the system environment.
- Restricted the release workflow to run only after the Bump Version workflow succeeds on the `main` branch.

## [0.1.0] - 2025-07-30
### Added
- Initial release.
