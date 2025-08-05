"""Project-wide custom exceptions."""


class ParsingError(Exception):
    """Custom exception for errors during HTML parsing."""

    pass


class RequestError(Exception):
    """Custom exception for HTTP request failures."""

    pass


class ProfileError(Exception):
    """Custom exception for profile-related operation failures."""

    pass
