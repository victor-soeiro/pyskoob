# Publishers Service

The `PublisherService` fetches information about publishers and their releases on Skoob.

## Example

```python
from pyskoob import SkoobClient

with SkoobClient() as client:
    publisher = client.publishers.get_by_id(1)
    print(publisher.name)
```

::: pyskoob.publishers
