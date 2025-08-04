# Publisher Service

The `PublisherService` fetches information about publishers and their releases on Skoob.

## Example

```python
from pyskoob import SkoobClient

with SkoobClient() as client:
    publisher = client.publishers.get_by_id(21)  # replace with a real id
    print(publisher.name)
```

::: pyskoob.publishers
