# PySkoob Documentation

Welcome to the **PySkoob** documentation. This site provides usage examples and a reference of the available services.

## Installation

```bash
pip install pyskoob
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

## Further Reading

- [Advanced Usage](advanced_usage.md)
- [Stable Public API](stable_api.md)
