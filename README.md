# PySkoob

[![PyPI](https://img.shields.io/pypi/v/scraper-skoob?color=blue)](https://pypi.org/project/scraper-skoob/)
[![CI](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml/badge.svg)](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/scraper-skoob)](https://pypi.org/project/scraper-skoob/)
[![License](https://img.shields.io/github/license/victor-soeiro/pyskoob)](LICENSE)

**PySkoob** is a Python client that makes it easy to interact with the Skoob website. It takes care of authentication and HTML parsing so you can focus on your automation or data collection tasks.

## Features

- Search books by title, author or ISBN
- Retrieve detailed book information and reviews
- Access user profiles and reading statistics
- Authenticate using email/password or an existing session cookie

## Installation

Install the latest release from PyPI:

```bash
python -m pip install scraper-skoob
```

Or install the bleeding edge version from GitHub:

```bash
python -m pip install git+https://github.com/victor-soeiro/pyskoob.git
```

## Usage examples

### Search for books

```python
from pyskoob.client import SkoobClient
from pyskoob.models.enums import BookSearch

with SkoobClient() as client:
    results = client.books.search("Harry Potter", BookSearch.TITLE)
    for book in results.results:
        print(book.title, book.book_id)
```

### Fetch book details

```python
from pyskoob.client import SkoobClient

with SkoobClient() as client:
    book = client.books.get_by_id(1)  # replace with a real edition ID
    print(book.title, book.publisher.name)
```

### Authenticate and access your profile

```python
from pyskoob.client import SkoobClient

with SkoobClient() as client:
    # TIP: use environment variables or a secrets manager instead of hard-coding credentials
    me = client.auth.login(email="you@example.com", password="secret")
    print(me.name)
```

## Learn more

- [Examples](examples)
- [Documentation](https://victor-soeiro.github.io/pyskoob/)
- [Contributing guidelines](CONTRIBUTING.md)
