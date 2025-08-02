"""Helper utilities for parsing Skoob URLs.

These functions extract numeric identifiers for books, editions, users, and
authors from their respective Skoob links.
"""


def get_book_id_from_url(url: str) -> str:
    """
    Extracts the book ID from a Skoob book URL.

    Parameters
    ----------
    url : str
        The Skoob book URL.

    Returns
    -------
    str
        The book ID.

    Examples
    --------
    >>> get_book_id_from_url('https://www.skoob.com.br/livro/1-ed1.html')
    '1'
    """
    filename = url.split("/")[-1]
    parts = filename.split("-")
    if parts[0].isdigit():
        return parts[0]
    else:
        return parts[-1].split("ed")[0].strip()


def get_book_edition_id_from_url(url: str) -> str:
    """
    Extracts the book edition ID from a Skoob book URL.

    Parameters
    ----------
    url : str
        The Skoob book URL.

    Returns
    -------
    str
        The book edition ID.

    Examples
    --------
    >>> get_book_edition_id_from_url('https://www.skoob.com.br/livro/1-ed10.html')
    '10'
    """
    return url.split("ed")[-1].replace(".html", "")


def get_user_id_from_url(url: str) -> str:
    """
    Extracts the user ID from a Skoob user URL.

    Parameters
    ----------
    url : str
        The Skoob user URL.

    Returns
    -------
    str
        The user ID.

    Examples
    --------
    >>> get_user_id_from_url('https://www.skoob.com.br/usuario/5-name')
    '5'
    """
    return url.split("/")[-1].split("-")[0]


def get_author_id_from_url(url: str) -> str:
    """Extract the author ID from a Skoob author URL.

    Parameters
    ----------
    url : str
        The Skoob author URL.

    Returns
    -------
    str
        The author ID.

    Examples
    --------
    >>> get_author_id_from_url('https://www.skoob.com.br/autor/50-name')
    '50'
    """
    return url.split("/")[-1].split("-")[0]
