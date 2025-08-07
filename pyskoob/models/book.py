"""Pydantic models representing books and their statistics."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookStats(BaseModel):
    """Aggregated statistics about a book derived from Skoob's API.

    Attributes
    ----------
    readers : int
        Users who finished the book.
    currently_reading : int
        Users currently reading the book.
    want_to_read : int
        Users who want to read the book.
    rereading : int
        Users rereading the book.
    abandoned : int
        Users who abandoned the book.
    reviews_count : int
        Number of reviews written for the book.
    average_rating : float
        Average rating of the book.
    ratings_count : int
        Number of individual ratings submitted.
    favorites_count : int
        Users who have favorited the book.
    wishlist_count : int
        Users who added the book to their wishlist.
    tradable_count : int
        Users willing to trade the book.
    loaned_count : int
        Users who loaned their copy.
    owned_count : int
        Users who own the book.
    reading_goals_count : int
        Reading challenge entries.
    female_readers_count : int
        Female readers count.
    male_readers_count : int
        Male readers count.
    shelves_count : int
        Number of shelves the book appears in.
    """

    readers: int = Field(..., alias="qt_lido")
    currently_reading: int = Field(..., alias="qt_lendo")
    want_to_read: int = Field(..., alias="qt_vouler")
    rereading: int = Field(..., alias="qt_relendo")
    abandoned: int = Field(..., alias="qt_abandonei")

    reviews_count: int = Field(..., alias="qt_resenhas")
    average_rating: float = Field(..., alias="ranking")
    ratings_count: int = Field(..., alias="qt_avaliadores")
    favorites_count: int = Field(..., alias="qt_favoritos")
    wishlist_count: int = Field(..., alias="qt_desejados")
    tradable_count: int = Field(..., alias="qt_troco")
    loaned_count: int = Field(..., alias="qt_emprestados")
    owned_count: int = Field(..., alias="qt_tenho")
    reading_goals_count: int = Field(..., alias="qt_meta")
    female_readers_count: int = Field(..., alias="qt_mulheres")
    male_readers_count: int = Field(..., alias="qt_homens")
    shelves_count: int = Field(..., alias="qt_estantes")

    model_config = ConfigDict(from_attributes=True)


class Book(BaseModel):
    """Detailed information about a book edition.

    Attributes
    ----------
    book_id : int
        Identifier of the work.
    edition_id : int
        Identifier of this edition.
    title : str
        Edition title.
    subtitle : str | None
        Subtitle of the edition.
    series : str | None
        Series to which the edition belongs.
    volume : str | None
        Volume within the series.
    authors : str | None
        Authors credited for the edition.
    description : str | None
        Synopsis or summary text.
    publisher : str | None
        Publisher of the edition.
    isbn : str | None
        International Standard Book Number.
    page_count : int
        Number of pages in the edition.
    publication_year : int | None
        Year of publication.
    publication_month : int | None
        Month of publication.
    language : str | None
        Language of the edition.
    url : str
        URL to the edition page.
    cover_url : str
        URL of the cover image.
    genres : list[str] | None
        Genres associated with the edition.
    stats : BookStats | None
        Aggregated statistics for the edition.
    """

    book_id: int = Field(..., alias="livro_id")
    edition_id: int = Field(..., alias="id")
    title: str = Field(..., alias="titulo")
    subtitle: str | None = Field("", alias="subtitulo")
    series: str | None = Field(None, alias="serie")
    volume: str | None = Field(None, alias="volume")
    authors: str | None = Field(None, alias="autor")
    description: str | None = Field("", alias="sinopse")
    publisher: str | None = Field("", alias="editora")
    isbn: str | None
    page_count: int = Field(0, alias="paginas")
    publication_year: int | None = Field(None, alias="ano")
    publication_month: int | None = Field(None, alias="mes")
    language: str | None = Field("", alias="idioma")
    url: str
    cover_url: str
    genres: list[str] | None = Field(default=None, alias="generos")

    stats: BookStats | None = Field(default=None, alias="estatisticas")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_by_name=True,
    )


class BookSearchResult(BaseModel):
    """Lightweight representation returned by the search endpoint.

    Attributes
    ----------
    edition_id : int
        Identifier of the edition.
    book_id : int
        Identifier of the work.
    title : str
        Title of the edition.
    publisher : str | None
        Publisher of the edition.
    isbn : str | None
        International Standard Book Number.
    url : str
        URL to the edition page.
    cover_url : str | None
        URL of the cover image.
    rating : float | None
        Average user rating.
    """

    edition_id: int
    book_id: int
    title: str
    publisher: str | None = None
    isbn: str | None = None
    url: str
    cover_url: str | None = None
    rating: float | None = None

    model_config = ConfigDict(from_attributes=True)


class BookTag(BaseModel):
    """Tags associated with a book edition.

    Attributes
    ----------
    edition_id : int
        Identifier of the edition.
    tags : list[str] | None
        Tags assigned to the edition.
    """

    edition_id: int
    tags: list[str] | None = None


class BookReview(BaseModel):
    """User review for a specific book edition.

    Attributes
    ----------
    review_id : int
        Identifier of the review.
    book_id : int
        Identifier of the work.
    edition_id : int | None
        Identifier of the edition, if available.
    user_id : int
        Identifier of the review author.
    rating : float
        Numeric rating given by the user.
    review_text : str
        Review content written by the user.
    reviewed_at : datetime | None
        Date and time when the review was posted.
    """

    review_id: int
    book_id: int
    edition_id: int | None
    user_id: int

    rating: float
    review_text: str
    reviewed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
