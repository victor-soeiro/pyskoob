"""Enumerations mapping Skoob UI labels and API constants."""

from enum import IntEnum, StrEnum


class BookShelf(StrEnum):
    """Shelf categories available on the website."""
    COMIC = 'comic'
    BOOK = 'book'
    MAGAZINE = 'magazine'


class BookLabel(IntEnum):
    """Numeric labels used by the API when tagging books."""
    FAVORITE = 8
    WISHLIST = 9
    OWNED = 6
    TRADABLE = 10
    LOANED = 11


class BookSearch(StrEnum):
    """Search modes accepted by the book search endpoint."""
    ALL = 'geral'
    ISBN = 'isbn'
    AUTHOR = 'autor'
    PUBLISHER = 'editora'
    TITLE = 'titulo'
    TAGS = 'tags'


class BookStatus(IntEnum):
    """Status codes for a user's relationship with a book."""
    READ = 1
    CURRENTLY_READING = 2
    WANT_TO_READ = 3
    REREADING = 4
    ABANDONED = 5


class BookUserStatus(StrEnum):
    """URL slugs representing shelves in user listings."""
    READ = 'leram'
    CURRENTLY_READING = 'lendo'
    WANT_TO_READ = 'vaoler'
    REREADING = 'relendo'
    ABANDONED = 'abandonaram'
    FAVORITED = 'favoritos'
    TRADABLE = 'trocam'
    WISHLISTED = 'desejam'
    RATED = 'avaliaram'


class BookcaseOption(IntEnum):
    """Filter options for a user's virtual bookcase."""
    ALL = 0
    READ = 1
    CURRENTLY_READING = 2
    WANT_TO_READ = 3
    REREADING = 4
    ABANDONED = 5
    FAVORITE = 8
    WISHLIST = 9
    RATED = 13
    REVIEWED = 14
    OWNED = 6
    TRADABLE = 10
    LOANED = 11
    READING_GOAL = 12
    EBOOK = 7
    AUDIOBOOK = 15


class UsersRelation(StrEnum):
    """Types of relationship between users."""
    FRIENDS = 'amigos'
    FOLLOWING = 'seguidos'
    FOLLOWERS = 'seguidores'


class UserGender(StrEnum):
    """Gender codes returned by the API."""
    MALE = 'M'
    FEMALE = 'F'


class BrazilianState(StrEnum):
    """Brazilian state abbreviations used in user profiles."""
    ACRE = "AC"
    ALAGOAS = "AL"
    AMAPA = "AP"
    AMAZONAS = "AM"
    BAHIA = "BA"
    CEARA = "CE"
    DISTRITO_FEDERAL = "DF"
    ESPIRITO_SANTO = "ES"
    GOIAS = "GO"
    MARANHAO = "MA"
    MATO_GROSSO = "MT"
    MATO_GROSSO_DO_SUL = "MS"
    MINAS_GERAIS = "MG"
    PARA = "PA"
    PARAIBA = "PB"
    PARANA = "PR"
    PERNAMBUCO = "PE"
    PIAUI = "PI"
    RIO_DE_JANEIRO = "RJ"
    RIO_GRANDE_DO_NORTE = "RN"
    RIO_GRANDE_DO_SUL = "RS"
    RONDONIA = "RO"
    RORAIMA = "RR"
    SANTA_CATARINA = "SC"
    SAO_PAULO = "SP"
    SERGIPE = "SE"
    TOCANTINS = "TO"
