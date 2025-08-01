from pydantic import BaseModel, Field


class PublisherStats(BaseModel):
    followers: int | None = None
    average_rating: float | None = None
    ratings: int | None = None
    male_percentage: int | None = None
    female_percentage: int | None = None


class PublisherItem(BaseModel):
    url: str
    title: str
    img_url: str


class PublisherAuthor(BaseModel):
    url: str
    name: str
    img_url: str


class Publisher(BaseModel):
    id: int
    name: str
    description: str | None = None
    website: str | None = None
    stats: PublisherStats = Field(default_factory=PublisherStats)
    last_releases: list[PublisherItem] = Field(default_factory=list)
