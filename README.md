# PySkoob
[![PyPI Version](https://img.shields.io/pypi/v/pyskoob?style=flat-square&logo=pypi)](https://pypi.org/project/pyskoob/)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square&logo=python)
[![Coverage](https://raw.githubusercontent.com/victor-soeiro/pyskoob/main/docs/img/coverage.svg)](https://github.com/victor-soeiro/pyskoob/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-latest-blue?style=flat-square)](https://victor-soeiro.github.io/pyskoob/)
[![License](https://img.shields.io/github/license/victor-soeiro/pyskoob?style=flat-square)](LICENSE)

**PySkoob** is a Python client that makes it easy to interact with the Skoob website. It takes care of authentication and HTML parsing so you can focus on your automation or data collection tasks.

## Features

* Search books by title, author or ISBN
* Retrieve detailed book information and reviews
* Access user profiles and reading statistics
* Authenticate using email/password or an existing session cookie

## Services

Documentation for each service is available on GitHub Pages:

* [Author Service](https://victor-soeiro.github.io/pyskoob/author_service/)
* [Books Service](https://victor-soeiro.github.io/pyskoob/books_service/)
* [Publisher Service](https://victor-soeiro.github.io/pyskoob/publishers_service/)
* [Users Service](https://victor-soeiro.github.io/pyskoob/users_service/)
* [Profile Service](https://victor-soeiro.github.io/pyskoob/profile_service/)

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

## Rate limiting

Skoob may block clients that issue too many requests in a short period of
time. PySkoob includes a basic rate limiter that throttles requests to **one**
per second by default. Adjusting this limit is possible but done entirely at
your own risk—Skoob may block or ban your account. Provide a custom
:class:`pyskoob.utils.RateLimiter` instance to change or disable the limit:

```python
from pyskoob import RateLimiter, SkoobClient

limiter = RateLimiter(max_calls=2, period=1)  # two requests per second (use at your own risk)
with SkoobClient(rate_limiter=limiter) as client:
    ...
```

``SkoobAsyncClient`` accepts the same configuration options and forwards any
extra keyword arguments to ``httpx.AsyncClient``. You may also provide a
pre-configured HTTP client or manage the lifecycle manually using the explicit
``close`` method:

```python
from pyskoob import RateLimiter, SkoobAsyncClient
from pyskoob.http.httpx import HttpxAsyncClient

limiter = RateLimiter(max_calls=2, period=1)
http_client = HttpxAsyncClient(rate_limiter=limiter, timeout=5)
client = SkoobAsyncClient(http_client=http_client)
try:
    ...
finally:
    await client.close()
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
# Install uv if it's not already available
python -m pip install uv

# Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate
# On Windows
.\.venv\Scripts\activate

# Install the project with development dependencies
uv pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Verify linting, formatting, and tests
pytest -vv
pre-commit run --all-files
```

Once everything is ready:

1. Fork the repository and create a branch for your feature.
2. Implement your change and add tests.
3. Format your code with Ruff:

   ```bash
   ruff format .
   ```
4. Ensure lint checks pass:

   ```bash
   ruff check .
   ```
5. Run `pytest -vv` and `pre-commit run --all-files` and ensure everything passes.
6. Open a pull request describing your changes.

## Learn more

* [Examples](https://victor-soeiro.github.io/pyskoob/advanced_usage/)
* [Documentation](https://victor-soeiro.github.io/pyskoob/)
* [Contributing guidelines](https://victor-soeiro.github.io/pyskoob/contributing/)
