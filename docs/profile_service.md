# Profile Service

The `SkoobProfileService` lets you modify your Skoob profile by labeling, shelving and rating books.

## Example

```python
import os
from pyskoob import SkoobClient
from pyskoob.models.enums import BookStatus

with SkoobClient() as client:
    client.auth.login(
        email=os.getenv("SKOOB_EMAIL"),
        password=os.getenv("SKOOB_PASSWORD"),
    )
    client.profile.update_book_status(10, BookStatus.READ)
```

::: pyskoob.profile
