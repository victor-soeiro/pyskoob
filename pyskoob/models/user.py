"""Pydantic models representing Skoob users and related data."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class UserSearch(BaseModel):
    """Minimal user information returned by search queries."""

    id: int
    username: str
    name: str
    url: str

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """Profile information for a Skoob user."""

    id: int
    name: str = Field(..., alias="nome")
    nickname: str = Field(..., alias="apelido")
    abbreviation: str = Field(..., alias="abbr")

    profile_url: str = Field(..., alias="url")
    username: str = Field(..., alias="skoob")

    photo_mini: HttpUrl = Field(..., alias="foto_mini")
    photo_small: HttpUrl = Field(..., alias="foto_pequena")
    photo_medium: HttpUrl = Field(..., alias="foto_media")
    photo_large: HttpUrl = Field(..., alias="foto_grande")

    is_premium: bool = Field(..., alias="premium")
    is_beta_user: bool = Field(..., alias="beta")

    about: str
    signup_year: int = Field(..., alias="ano")
    signup_month: int = Field(..., alias="mes")
    signup_term: datetime = Field(..., alias="termo")

    stats: "UserStats" = Field(..., alias="estatisticas")

    model_config = ConfigDict(from_attributes=True)


class UserBook(BaseModel):
    """Status of a specific book in a user's shelf."""

    user_id: int
    book_id: int
    edition_id: int

    rating: float | None = None
    is_favorite: bool = False
    is_wishlist: bool = False
    is_tradable: bool = False
    is_owned: bool = False
    is_loaned: bool = False
    reading_goal_year: int | None = None
    pages_read: int | None = None

    model_config = ConfigDict(from_attributes=True)


class UserReadStats(BaseModel):
    """Reading progress statistics for a particular year."""

    user_id: int
    year: int

    books_read: int = 0
    pages_read: int = 0
    total_pages: int = 0
    percent_complete: int = 0
    books_total: int = 0
    reading_speed: int = 0
    ideal_reading_speed: int = 0

    model_config = ConfigDict(from_attributes=True)


class UserStats(BaseModel):
    """Aggregated counts describing the user's activity on Skoob."""

    books: int = Field(0, alias="livros")
    magazines: int = Field(0, alias="revistas")
    comics: int = Field(0, alias="quadrinhos")
    friends: int = Field(0, alias="amigos")
    following: int = Field(0, alias="seguidos")
    followers: int = Field(0, alias="seguidores")
    messages: int = Field(0, alias="recados")
    pages_read: int = Field(0, alias="paginometro")
    books_read: int = Field(0, alias="lido")
    currently_reading: int = Field(0, alias="lendo")
    want_to_read: int = Field(0, alias="vouler")
    rereading: int = Field(0, alias="relendo")
    abandoned: int = Field(0, alias="abandonei")
    owned: int = Field(0, alias="tenho")
    tradable: int = Field(0, alias="troco")
    loaned: int = Field(0, alias="emprestados")
    favorites: int = Field(0, alias="favoritos")
    wishlist: int = Field(0, alias="desejados")
    reading_goal: int = Field(0, alias="meta")
    videos: int = Field(0, alias="videos")

    model_config = ConfigDict(from_attributes=True)
