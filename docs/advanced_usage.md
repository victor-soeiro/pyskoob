# Advanced Usage

This section shows more involved examples of working with PySkoob.

## Handling Pagination

Several services return a `Pagination` object that exposes the
`has_next_page` flag. You can use this flag to iterate over all pages:

```python
from pyskoob import SkoobClient
from pyskoob.models.enums import BookSearch

with SkoobClient() as client:
    page = 1
    while True:
        results = client.books.search("Python", BookSearch.TITLE, page=page)
        for book in results.results:
            print(f"[{page}] {book.title}")
        if not results.has_next_page:
            break
        page += 1
```

## Asynchronous HTTP Client

PySkoob ships with `HttpxAsyncClient` for making asynchronous HTTP requests.
While the high level services are synchronous, you can use the async client
when integrating with an async application:

```python
import asyncio
from pyskoob import HttpxAsyncClient

async def main() -> None:
    client = HttpxAsyncClient()
    resp = await client.get("https://www.skoob.com.br")
    print(resp.text[:100])
    await client.close()

asyncio.run(main())
```
