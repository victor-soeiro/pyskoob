from pydantic import BaseModel, Field


class AuthorSearchResult(BaseModel):
    name: str
    url: str
    nickname: str
    followers: int
    readers: int
    books: int
    img_url: str


class AuthorStats(BaseModel):
    followers: int | None = None
    readers: int | None = None
    ratings: int | None = None
    average_rating: float | None = None
    star_ratings: dict[str, float] = Field(default_factory=dict)


class AuthorBook(BaseModel):
    url: str | None = None
    title: str | None = None
    img_url: str | None = None


class AuthorVideo(BaseModel):
    url: str | None = None
    thumbnail_url: str | None = None
    title: str | None = None


class AuthorProfile(BaseModel):
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
