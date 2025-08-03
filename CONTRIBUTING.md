# Contributing Guide

Thank you for wanting to contribute to **PySkoob**! The following guidelines will help you open good issues and pull requests.

## Reporting Issues

- Search the existing [issues](https://github.com/victor-soeiro/pyskoob/issues) to avoid duplicates.
- Provide clear steps to reproduce the problem and describe what you expected to happen.
- Include logs, stack traces and your environment information when applicable.

## Pull Requests

1. Fork the repository and create a new branch from `main`.
2. Keep your changes focused on a single topic or feature.
3. Write descriptive commit messages and link your PR to an open issue when possible.
4. Make sure tests pass locally before submitting the PR.

### Quick Start

```bash
# Create a virtual environment with uv
uv venv .venv
source .venv/bin/activate

# Install dependencies in editable mode
uv pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run all checks
pre-commit run --all-files
```

Run `pre-commit run --all-files` to ensure formatting, linting and tests pass locally. The CI workflow runs the same hooks to verify submitted changes.

Open your PR on GitHub and fill in a brief summary of your changes. A maintainer will review it as soon as possible.

## Coding Standards

- Adhere to [PEP 8](https://peps.python.org/pep-0008/) and keep lines under 140 characters.
- Run `ruff --fix` to format and lint the codebase.
- Provide type hints and docstrings for all public modules, classes, and functions.

## Commit Message Format

This project follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

- Use the structure `<type>: <short description>` in the imperative mood.
- Common types include `feat`, `fix`, `docs`, `refactor`, `test`, and `chore`.
- Limit the first line to 72 characters and reference issues when relevant, e.g., `fix: handle edge case (#123)`.

## Best Practices

- Review the coding standards and commit message format above before submitting your work.
- Add tests for any new functionality.
- Update documentation whenever behavior changes.

## Release Process

To publish a new version and deploy documentation:

1. Trigger the **Release** workflow from the GitHub Actions tab.
2. Choose the desired semantic version bump (`patch`, `minor`, or `major`).
3. The workflow will bump the version, tag the commit, publish to PyPI, build the documentation, and push it to GitHub Pages.

