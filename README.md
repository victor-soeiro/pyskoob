# PySkoob

[![PyPI](https://img.shields.io/pypi/v/scraper-skoob?color=blue)](https://pypi.org/project/scraper-skoob/)
[![CI](https://github.com/YOUR_GITHUB_USER/pyskoob/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_GITHUB_USER/pyskoob/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/scraper-skoob)](https://pypi.org/project/scraper-skoob/)
[![License](https://img.shields.io/github/license/YOUR_GITHUB_USER/pyskoob)](LICENSE)

## Overview
PySkoob is a Python library that simplifies interacting with the Skoob website. It acts as an HTTP client, providing services for authentication, book searches, and profile access. The goal of the project is to streamline integrations and automation while offering an easy‑to‑use interface.

## Documentation
The full documentation is generated using [MkDocs](https://www.mkdocs.org/) and lives in the `docs/` folder. To preview it locally run:

```bash
pip install -e .[docs]
mkdocs serve
```

## Installation
Create a virtual environment using [uv](https://github.com/astral-sh/uv) and
install from PyPI:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install scraper-skoob
```

To always use the latest version from GitHub:

```bash
uv pip install git+https://github.com/YOUR_GITHUB_USER/pyskoob.git
```

## Authentication
You can authenticate in two different ways:

1. **Email and password**

    ```python
    from pyskoob.client import SkoobClient

    with SkoobClient() as client:
        me = client.auth.login(email="you@example.com", password="secret")
    ```

2. **Session cookie**

    ```python
    from pyskoob.client import SkoobClient

    with SkoobClient() as client:
        me = client.auth.login_with_cookies("PHPSESSID_TOKEN")
    ```

Once authenticated you can access all other services.

## Usage example
```python
from pyskoob.client import SkoobClient
from pyskoob.models.enums import BookSearch

with SkoobClient() as client:
    results = client.books.search("Harry Potter", BookSearch.TITLE)
    for book in results.results:
        print(book.title, book.book_id)
```

## Running tests
Install the project in editable mode and run the test suite:

```bash
uv pip install -e .
pytest -vv
```

Generate a coverage report with:

```bash
pytest --cov=pyskoob
```

## Contributing
1. Fork the repository and create a branch for your feature.
2. Install the dependencies in editable mode:

   ```bash
   uv pip install -e .
   ```
3. Implement your change and add tests.
4. Run `ruff` to check code style:

   ```bash
   ruff .
   ```
5. Run `pytest` and ensure everything passes.
6. Open a pull request describing your changes.

Contributions are very welcome!
