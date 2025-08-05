from pydantic import BaseModel, Field


class PublisherStats(BaseModel):
    """Aggregated statistics about a publisher.

    Attributes
    ----------
    followers : int | None
        Number of users following the publisher.
    average_rating : float | None
        Average rating across the publisher's books.
    ratings : int | None
        Total number of ratings received.
    male_percentage : int | None
        Percentage of male readers.
    female_percentage : int | None
        Percentage of female readers.
    """

    followers: int | None = None
    average_rating: float | None = None
    ratings: int | None = None
    male_percentage: int | None = None
    female_percentage: int | None = None


class PublisherItem(BaseModel):
    """Book entry in a publisher listing.

    Attributes
    ----------
    url : str
        Link to the book's page.
    title : str
        Title of the book.
    img_url : str
        URL to the book cover image.
    """

    url: str
    title: str
    img_url: str


class PublisherAuthor(BaseModel):
    """Author associated with a publisher.

    Attributes
    ----------
    url : str
        Link to the author's profile.
    name : str
        Author's name.
    img_url : str
        URL to the author's photo.
    """

    url: str
    name: str
    img_url: str


class Publisher(BaseModel):
    """Detailed information about a publisher.

    Attributes
    ----------
    id : int
        Unique identifier of the publisher.
    name : str
        Publisher's display name.
    description : str | None
        Short description or history of the publisher.
    website : str | None
        URL to the publisher's official website.
    stats : PublisherStats
        Aggregated statistics about the publisher.
    last_releases : list[PublisherItem]
        Recently released books.
    """

    id: int
    name: str
    description: str | None = None
    website: str | None = None
    stats: PublisherStats = Field(default_factory=PublisherStats)
    last_releases: list[PublisherItem] = Field(default_factory=list)
