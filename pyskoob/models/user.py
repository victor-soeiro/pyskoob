"""Pydantic models representing Skoob users and related data."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class UserSearch(BaseModel):
    """Minimal user information returned by search queries.

    Attributes
    ----------
    id : int
        Unique identifier of the user.
    username : str
        Username in profile URLs.
    name : str
        Display name of the user.
    url : str
        Full URL to the user's profile.
    """

    id: int
    username: str
    name: str
    url: str

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """Profile information for a Skoob user.

    Attributes
    ----------
    id : int
        Unique identifier of the user.
    name : str
        Full name of the user.
    nickname : str
        Display nickname.
    abbreviation : str
        Shorthand used on the site.
    profile_url : str
        Public URL of the profile.
    username : str
        Username handle.
    photo_mini : HttpUrl
        URL to the smallest avatar.
    photo_small : HttpUrl
        URL to the small avatar.
    photo_medium : HttpUrl
        URL to the medium avatar.
    photo_large : HttpUrl
        URL to the large avatar.
    is_premium : bool
        Indicates premium membership.
    is_beta_user : bool
        Indicates participation in the beta program.
    about : str
        Short biography text.
    signup_year : int
        Year when the user joined Skoob.
    signup_month : int
        Month when the user joined Skoob.
    signup_term : datetime
        Timestamp of terms acceptance.
    stats : UserStats
        Aggregated activity statistics.
    """

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
    """Status of a specific book in a user's shelf.

    Attributes
    ----------
    user_id : int
        Identifier of the user.
    book_id : int
        Identifier of the book.
    edition_id : int
        Identifier of the edition.
    rating : float | None
        User rating for the book.
    is_favorite : bool
        Whether the book is marked as favorite.
    is_wishlist : bool
        Whether the book is in the wishlist.
    is_tradable : bool
        Whether the book is available for trade.
    is_owned : bool
        Whether the user owns the book.
    is_loaned : bool
        Whether the book is loaned out.
    reading_goal_year : int | None
        Year of the reading goal including this book.
    pages_read : int | None
        Number of pages the user has read.
    """

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
    """Reading progress statistics for a particular year.

    Attributes
    ----------
    user_id : int
        Identifier of the user.
    year : int
        Year this record summarizes.
    books_read : int
        Total books read.
    pages_read : int
        Total pages read.
    total_pages : int
        Total pages in the goal.
    percent_complete : int
        Percentage of the goal completed.
    books_total : int
        Total books targeted.
    reading_speed : int
        Average pages read per day.
    ideal_reading_speed : int
        Required pages per day to meet the goal.
    """

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
    """Aggregated counts describing the user's activity on Skoob.

    Attributes
    ----------
    books : int
        Number of books in the user's shelves.
    magazines : int
        Number of magazines in the user's shelves.
    comics : int
        Number of comics in the user's shelves.
    friends : int
        Count of friends.
    following : int
        Users this user is following.
    followers : int
        Users following this user.
    messages : int
        Messages exchanged with others.
    pages_read : int
        Total pages read.
    books_read : int
        Books marked as read.
    currently_reading : int
        Books currently being read.
    want_to_read : int
        Books the user wants to read.
    rereading : int
        Books being reread.
    abandoned : int
        Books abandoned by the user.
    owned : int
        Books owned by the user.
    tradable : int
        Books available for trade.
    loaned : int
        Books loaned to others.
    favorites : int
        Books marked as favorite.
    wishlist : int
        Books added to the wishlist.
    reading_goal : int
        Books included in the reading goal.
    videos : int
        Uploaded videos.
    """

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
