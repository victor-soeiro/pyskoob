# PySkoob
[![Latest Tag](https://img.shields.io/github/v/tag/victor-soeiro/pyskoob?sort=semver&style=flat-square)](https://github.com/victor-soeiro/pyskoob/releases)
[![PyPI Version](https://img.shields.io/pypi/v/pyskoob?style=flat-square&logo=pypi)](https://pypi.org/project/pyskoob/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyskoob?style=flat-square&logo=python)](https://pypi.org/project/pyskoob/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pyskoob?style=flat-square)](https://pypi.org/project/pyskoob/)
[![CI](https://img.shields.io/github/actions/workflow/status/victor-soeiro/pyskoob/ci.yml?style=flat-square)](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml)
[![Coverage](https://raw.githubusercontent.com/victor-soeiro/pyskoob/main/coverage.svg)](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-latest-blue?style=flat-square)](https://victor-soeiro.github.io/pyskoob/)
[![License](https://img.shields.io/github/license/victor-soeiro/pyskoob?style=flat-square)](LICENSE)

**PySkoob** is a Python client that makes it easy to interact with the Skoob website. It takes care of authentication and HTML parsing so you can focus on your automation or data collection tasks.

## Features

* Search books by title, author or ISBN
* Retrieve detailed book information and reviews
* Access user profiles and reading statistics
* Authenticate using email/password or an existing session cookie

## Installation

Install the latest release from PyPI:

```bash
python -m pip install pyskoob
```

Or install the bleeding edge version from GitHub:

```bash
python -m pip install git+https://github.com/victor-soeiro/pyskoob.git
```

## Authentication

You can authenticate in two different ways:

1. **Email and password**

   ```python
   from pyskoob import SkoobClient

   with SkoobClient() as client:
       me = client.auth.login(email="you@example.com", password="secret")
   ```

2. **Session cookie**

   ```python
   from pyskoob import SkoobClient

   with SkoobClient() as client:
       me = client.auth.login_with_cookies("PHPSESSID_TOKEN")
   ```

Once authenticated you can access all other services.

## Usage example

### Search for books

```python
from pyskoob import SkoobClient
from pyskoob.models.enums import BookSearch

with SkoobClient() as client:
    results = client.books.search("Harry Potter", BookSearch.TITLE)
    for book in results.results:
        print(book.title, book.book_id)
```

### Fetch book details

```python
from pyskoob import SkoobClient

with SkoobClient() as client:
    book = client.books.get_by_id(1)  # replace with a real edition ID
    print(book.title, book.publisher.name)
```

### Authenticate and access your profile

```python
from pyskoob import SkoobClient

with SkoobClient() as client:
    # TIP: use environment variables or a secrets manager instead of hard-coding credentials
    me = client.auth.login(email="you@example.com", password="secret")
    print(me.name)
```

## Running tests

Install the project in editable mode and run the test suite:

```bash
uv pip install -e .[dev]
pytest -vv
```

## Contributing

Before working on new features, set up a local development environment:

```bash
# Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate

# Install the project with development dependencies
uv pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Verify linting, formatting, and tests
pre-commit run --all-files
pytest -vv
```

Once everything is ready:

1. Fork the repository and create a branch for your feature.
2. Implement your change and add tests.
3. Format your code with Ruff:

   ```bash
   ruff format .
   ```
4. Ensure formatting and lint checks pass:

   ```bash
   ruff format --check .
   ruff check .
   ```
5. Run `pre-commit run --all-files` and `pytest -vv` and ensure everything passes.
6. Open a pull request describing your changes.

## Learn more

* [Examples](examples)
* [Documentation](https://victor-soeiro.github.io/pyskoob/)
* [Contributing guidelines](CONTRIBUTING.md)
