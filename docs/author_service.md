# Author Service

The `AuthorService` provides search capabilities for authors on Skoob. It scrapes
Skoob's HTML pages and returns lightweight results with the following fields:

- `id`: numeric identifier extracted from the author URL
- `name`: the author's display name
- `nickname`: nickname shown below the name
- `url`: absolute URL to the author's page on Skoob
- `img_url`: avatar image URL

Skoob displays publication, reader and follower counts on the search results
page, but these values are often outdated when compared with the author's
profile page. To avoid exposing misleading data, `AuthorService` intentionally
omits these numbers.

## Example

```python
from pyskoob import SkoobClient

with SkoobClient() as client:
    results = client.authors.search("Asimov")
    for author in results.results:
        print(author.name, author.id)
    if results.has_next_page:
        # fetch the next page of results
        more_results = client.authors.search("Asimov", page=results.next_page)
```

`search()` returns only the first page of results. Use `results.has_next_page` to
fetch additional pages.

::: pyskoob.authors
