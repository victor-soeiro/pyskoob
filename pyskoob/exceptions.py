class HTTPClientError(Exception):
    """Custom exception for HTTP request failures."""

    pass


class ParsingError(Exception):
    """Custom exception for errors during HTML parsing."""

    pass
