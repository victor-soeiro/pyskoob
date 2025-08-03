# Profile Service

The `SkoobProfileService` lets you modify your Skoob profile by labeling, shelving and rating books.

## Example

```python
from pyskoob import SkoobClient
from pyskoob.models.enums import BookStatus

with SkoobClient() as client:
    client.auth.login(email="you@example.com", password="secret")
    client.profile.update_book_status(10, BookStatus.READ)
```

::: pyskoob.profile
