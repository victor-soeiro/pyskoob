# PySkoob

[![PyPI](https://img.shields.io/pypi/v/scraper-skoob?color=blue)](https://pypi.org/project/scraper-skoob/)
[![CI](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml/badge.svg)](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/scraper-skoob)](https://pypi.org/project/scraper-skoob/)
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
pip install scraper-skoob
```

Or install the bleeding edge version from GitHub:

```bash
pip install git+https://github.com/victor-soeiro/pyskoob.git
```

## Authentication and Quick Start

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

   with SkoobClient(cookie="your_session_cookie") as client:
       me = client.auth.me()
   ```

Example: Search for a book after authenticating

```python
from pyskoob import SkoobClient
from pyskoob.models.enums import BookSearch

with SkoobClient() as client:
    client.auth.login(email="you@example.com", password="secret")
    results = client.books.search("Harry Potter", BookSearch.TITLE)
    for book in results.results:
        print(book.title, book.book_id)
```

More examples can be found in the [`examples/`](examples) folder and in the [project documentation](https://victor-soeiro.github.io/pyskoob/).

## Development

Clone the repository and install in editable mode:

```bash
pip install -e .
```

Run `ruff` and `pytest` to ensure code style and tests pass:

```bash
ruff check .
pytest
```

## Contributing

Pull requests are welcome! Please open an issue first to discuss any changes.

## Documentation

The full API reference and guides are published at [https://victor-soeiro.github.io/pyskoob/](https://victor-soeiro.github.io/pyskoob/).
