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

# Run the test suite
pytest -q

# Optionally format and lint
ruff --fix
```

Open your PR on GitHub and fill in a brief summary of your changes. A maintainer will review it as soon as possible.

## Best Practices

- Follow the project's coding style; `ruff` is used for linting and formatting.
- Add tests for any new functionality.
- Update documentation whenever behavior changes.
