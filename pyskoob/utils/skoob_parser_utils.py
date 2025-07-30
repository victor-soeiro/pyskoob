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
    """
    filename = url.split('/')[-1]
    parts = filename.split('-')
    if parts[0].isdigit():
        return parts[0]
    else:
        return parts[-1].split('ed')[0].strip()


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
    """
    return url.split('ed')[-1].replace('.html', '')


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
    """
    return url.split('/')[-1].split('-')[0]
