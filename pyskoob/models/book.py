from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookStats(BaseModel):
    """Aggregated statistics about a book derived from Skoob's API."""

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
    """Detailed information about a book edition."""

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
    """Lightweight representation returned by the search endpoint."""

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
    """Tags associated with a book edition."""

    edition_id: int
    tags: list[str] | None = None


class BookReview(BaseModel):
    """User review for a specific book edition."""

    review_id: int
    book_id: int
    edition_id: int | None
    user_id: int

    rating: float
    review_text: str
    reviewed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
