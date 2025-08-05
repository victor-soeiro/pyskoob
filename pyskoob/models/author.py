"""Pydantic models representing authors and related data."""

from pydantic import BaseModel, ConfigDict, Field


class AuthorSearchResult(BaseModel):
    """Result entry returned by the author search endpoint.

    Attributes
    ----------
    id : int
        Unique identifier of the author.
    name : str
        Author's display name.
    url : str
        Full URL to the author's profile.
    nickname : str
        Nickname or alias for the author.
    img_url : str
        URL to the author's avatar image.
    """

    id: int
    name: str
    url: str
    nickname: str
    img_url: str

    model_config = ConfigDict(from_attributes=True)


class AuthorStats(BaseModel):
    """Aggregate statistics for an author profile.

    Attributes
    ----------
    followers : int | None
        Number of users following the author.
    readers : int | None
        Number of users who have read books by the author.
    ratings : int | None
        Total count of ratings received across all works.
    average_rating : float | None
        Average rating for the author's works.
    star_ratings : dict[str, float]
        Mapping of star values to their respective percentages.
    """

    followers: int | None = None
    readers: int | None = None
    ratings: int | None = None
    average_rating: float | None = None
    star_ratings: dict[str, float] = Field(default_factory=dict)


class AuthorBook(BaseModel):
    """Lightweight representation of a book associated with an author.

    Attributes
    ----------
    url : str | None
        Link to the book's page on Skoob.
    title : str | None
        Title of the book.
    img_url : str | None
        URL to the book cover image.
    """

    url: str | None = None
    title: str | None = None
    img_url: str | None = None


class AuthorVideo(BaseModel):
    """Video related to the author.

    Attributes
    ----------
    url : str | None
        Link to the video on Skoob or external platform.
    thumbnail_url : str | None
        URL of the video's thumbnail image.
    title : str | None
        Title of the video.
    """

    url: str | None = None
    thumbnail_url: str | None = None
    title: str | None = None


class AuthorProfile(BaseModel):
    """Detailed profile information about an author.

    Attributes
    ----------
    name : str
        Author's full name.
    photo_url : str | None
        Link to the author's photo.
    links : dict[str, str]
        Mapping of social network names to URLs.
    description : str
        Free-form biography text.
    tags : list[str]
        List of genres or categories associated with the author.
    birth_date : str | None
        Author's birth date.
    location : str | None
        Location of birth or residence.
    gender_percentages : dict[str, float]
        Percentage distribution of readers by gender.
    books : list[AuthorBook]
        Books written by the author.
    videos : list[AuthorVideo]
        Related videos featuring the author.
    stats : AuthorStats
        Aggregated statistics.
    created_at : str | None
        Creation timestamp of the profile.
    created_by : str | None
        Username of the profile creator.
    edited_at : str | None
        Last edit timestamp.
    edited_by : str | None
        Username of the last editor.
    approved_at : str | None
        When the profile was approved.
    approved_by : str | None
        Username of the approver.
    """

    name: str
    photo_url: str | None = None
    links: dict[str, str] = Field(default_factory=dict)
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    birth_date: str | None = None
    location: str | None = None
    gender_percentages: dict[str, float] = Field(default_factory=dict)
    books: list[AuthorBook] = Field(default_factory=list)
    videos: list[AuthorVideo] = Field(default_factory=list)
    stats: AuthorStats = Field(default_factory=AuthorStats)
    created_at: str | None = None
    created_by: str | None = None
    edited_at: str | None = None
    edited_by: str | None = None
    approved_at: str | None = None
    approved_by: str | None = None
