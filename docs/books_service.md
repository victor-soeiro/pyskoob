# Books Service

The `BookService` allows searching for books and retrieving detailed information.

## Example

```python
from pyskoob import SkoobClient
from pyskoob.models.enums import BookSearch

with SkoobClient() as client:
    results = client.books.search("Duna", BookSearch.TITLE)
    for book in results.results:
        print(book.title, book.book_id)
```

::: pyskoob.books.BookService
