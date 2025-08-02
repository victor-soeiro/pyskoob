# Stable Public API

The following classes and functions are considered stable. They are re-exported
from the :mod:`pyskoob` package and will only change with a deprecation period.
You can import them directly from the package root:

```python
from pyskoob import SkoobClient, HttpxSyncClient
```

- `SkoobClient`
- `AuthService`
- `BookService`
- `AuthorService`
- `UserService`
- `SkoobProfileService`
- `PublisherService`
- `HttpxSyncClient`
- `HttpxAsyncClient`

Anything not listed above should be treated as internal and may change without
notice.
