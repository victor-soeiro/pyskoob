# PySkoob

[![PyPI](https://img.shields.io/pypi/v/pyskoob?color=blue)](https://pypi.org/project/pyskoob/)
[![CI](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml/badge.svg)](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyskoob)](https://pypi.org/project/pyskoob/)
[![License](https://img.shields.io/github/license/victor-soeiro/pyskoob)](LICENSE)

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

1. Fork the repository and create a branch for your feature.
2. Install the dependencies in editable mode:

   ```bash
   uv pip install -e .[dev]
   ```
3. Implement your change and add tests.
4. Format your code with Ruff:

   ```bash
   ruff format .
   ```
5. Ensure formatting and lint checks pass:

   ```bash
   ruff format --check .
   ruff check .
   ```
6. Run `pytest` and ensure everything passes.
7. Open a pull request describing your changes.

## Learn more

* [Examples](examples)
* [Documentation](https://victor-soeiro.github.io/pyskoob/)
* [Contributing guidelines](CONTRIBUTING.md)
