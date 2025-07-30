from typing import Any

from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement


def safe_find(
    soup: BeautifulSoup | Tag | None,
    name: str,
    attrs: dict | None = None
) -> Tag | None:
    """
    Safely finds a single Tag in a BeautifulSoup object.

    Parameters
    ----------
    soup : BeautifulSoup | Tag | None
        The BeautifulSoup object or Tag to search in.
    name : str
        The name of the tag to find.
    attrs : dict | None, optional
        A dictionary of attributes to filter by, by default None.

    Returns
    -------
    Tag | None
        The found Tag or None if not found or the soup is None.
    """
    if not soup:
        return None
    found = soup.find(name, attrs or {})
    if isinstance(found, Tag):
        return found
    return None


def safe_find_all(
    soup: BeautifulSoup | Tag | None,
    name: str,
    attrs: dict | None = None
) -> list[Tag]:
    """
    Safely finds all Tags in a BeautifulSoup object.

    Parameters
    ----------
    soup : BeautifulSoup | Tag | None
        The BeautifulSoup object or Tag to search in.
    name : str
        The name of the tags to find.
    attrs : dict | None, optional
        A dictionary of attributes to filter by, by default None.

    Returns
    -------
    list[Tag]
        A list of found Tags, or an empty list if none are found or the soup is None.
    """
    if not soup:
        return []
    all_found = soup.find_all(name, attrs or {})
    return [tag for tag in all_found if isinstance(tag, Tag)]


def get_tag_text(
    tag: PageElement | None,
    strip: bool = True
) -> str:
    """
    Gets the text of a Tag, returning an empty string if the tag is None.

    Parameters
    ----------
    tag : PageElement | None
        The Tag to get the text from.
    strip : bool, optional
        Whether to strip whitespace from the text, by default True.

    Returns
    -------
    str
        The text of the Tag or an empty string.
    """
    if tag:
        return tag.get_text(strip=strip)
    return ""


def get_tag_attr(
    tag: Tag | None,
    attr: str,
    default: Any = None
) -> Any:
    """
    Gets an attribute from a Tag, returning a default value if the tag is None.

    Parameters
    ----------
    tag : Tag | None
        The Tag to get the attribute from.
    attr : str
        The name of the attribute.
    default : Any, optional
        The default value to return if the attribute is not found, by default None.

    Returns
    -------
    Any
        The value of the attribute or the default value.
    """
    if tag:
        return tag.get(attr, default)
    return default
