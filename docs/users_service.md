# Users Service

The `UserService` searches and retrieves Skoob user profiles.

## Example

```python
from pyskoob import SkoobClient

with SkoobClient() as client:
    # TIP: use environment variables or a secrets manager instead of hard-coding credentials
    client.auth.login(email="you@example.com", password="secret")
    results = client.users.search("victor")
    for user in results.results:
        print(user.name, user.id)
```

::: pyskoob.users
