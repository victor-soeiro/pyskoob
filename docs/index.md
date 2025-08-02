# PySkoob Documentation

Welcome to the **PySkoob** documentation. This site provides usage examples and a reference of the available services.

## Installation

```bash
pip install scraper-skoob
```

## Usage

```python
from pyskoob import SkoobClient

with SkoobClient() as client:
    books = client.books.search("python").results
```

## API Reference

::: pyskoob.client
::: pyskoob.auth
::: pyskoob.books
::: pyskoob.authors
::: pyskoob.users
::: pyskoob.profile
::: pyskoob.publishers
