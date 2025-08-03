"""Helper utilities for parsing Skoob URLs.

These functions extract numeric identifiers for books, editions, users, and
authors from their respective Skoob links.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse


def get_book_id_from_url(url: str) -> str:
    """Extract the book ID from a Skoob book URL.

    Parameters
    ----------
    url : str
        The Skoob book URL.

    Returns
    -------
    str
        The book ID.

    Raises
    ------
    ValueError
        If the URL does not contain a book ID.

    Examples
    --------
    >>> get_book_id_from_url('https://www.skoob.com.br/livro/1-ed1.html')
    '1'
    """
    path = urlparse(url).path
    match = re.search(r"(\d+)", path)
    if not match:
        raise ValueError(f"Book ID not found in URL: {url}")
    return match.group(1)


def get_book_edition_id_from_url(url: str) -> str:
    """Extract the book edition ID from a Skoob book URL.

    Parameters
    ----------
    url : str
        The Skoob book URL.

    Returns
    -------
    str
        The book edition ID.

    Raises
    ------
    ValueError
        If the URL does not contain an edition ID.

    Examples
    --------
    >>> get_book_edition_id_from_url('https://www.skoob.com.br/livro/1-ed10.html')
    '10'
    """
    path = urlparse(url).path
    match = re.search(r"ed(\d+)", path)
    if not match:
        raise ValueError(f"Book edition ID not found in URL: {url}")
    return match.group(1)


def get_user_id_from_url(url: str) -> str:
    """Extract the user ID from a Skoob user URL.

    Parameters
    ----------
    url : str
        The Skoob user URL.

    Returns
    -------
    str
        The user ID.

    Raises
    ------
    ValueError
        If the URL does not contain a user ID.

    Examples
    --------
    >>> get_user_id_from_url('https://www.skoob.com.br/usuario/5-name')
    '5'
    """
    path = urlparse(url).path
    match = re.search(r"/usuario/(\d+)", path)
    if not match:
        raise ValueError(f"User ID not found in URL: {url}")
    return match.group(1)


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

    Raises
    ------
    ValueError
        If the URL does not contain an author ID.

    Examples
    --------
    >>> get_author_id_from_url('https://www.skoob.com.br/autor/50-name')
    '50'
    """
    path = urlparse(url).path
    match = re.search(r"/autor/(\d+)", path)
    if not match:
        raise ValueError(f"Author ID not found in URL: {url}")
    return match.group(1)
