"""Enumerations mapping Skoob UI labels and API constants."""

from enum import IntEnum, StrEnum


class BookShelf(StrEnum):
    """Shelf categories available on the website.

    Attributes
    ----------
    COMIC : str
        Shelf containing comics.
    BOOK : str
        Shelf containing standard books.
    MAGAZINE : str
        Shelf containing magazines.
    """

    COMIC = "comic"
    BOOK = "book"
    MAGAZINE = "magazine"


class BookLabel(IntEnum):
    """Numeric labels used by the API when tagging books.

    Attributes
    ----------
    FAVORITE : int
        Marked as favorite.
    WISHLIST : int
        Added to wishlist.
    OWNED : int
        Owned by the user.
    TRADABLE : int
        Available for trade.
    LOANED : int
        Loaned to someone else.
    """

    FAVORITE = 8
    WISHLIST = 9
    OWNED = 6
    TRADABLE = 10
    LOANED = 11


class BookSearch(StrEnum):
    """Search modes accepted by the book search endpoint.

    Attributes
    ----------
    ALL : str
        Search across all fields.
    ISBN : str
        Search by ISBN.
    AUTHOR : str
        Search by author name.
    PUBLISHER : str
        Search by publisher.
    TITLE : str
        Search by book title.
    TAGS : str
        Search by tags.
    """

    ALL = "geral"
    ISBN = "isbn"
    AUTHOR = "autor"
    PUBLISHER = "editora"
    TITLE = "titulo"
    TAGS = "tags"


class BookStatus(IntEnum):
    """Status codes for a user's relationship with a book.

    Attributes
    ----------
    READ : int
        User has read the book.
    CURRENTLY_READING : int
        User is reading the book.
    WANT_TO_READ : int
        User wants to read the book.
    REREADING : int
        User is rereading the book.
    ABANDONED : int
        User abandoned the book.
    """

    READ = 1
    CURRENTLY_READING = 2
    WANT_TO_READ = 3
    REREADING = 4
    ABANDONED = 5


class BookUserStatus(StrEnum):
    """URL slugs representing shelves in user listings.

    Attributes
    ----------
    READ : str
        Users who have read the book.
    CURRENTLY_READING : str
        Users who are currently reading.
    WANT_TO_READ : str
        Users who want to read.
    REREADING : str
        Users rereading the book.
    ABANDONED : str
        Users who abandoned the book.
    FAVORITED : str
        Users who favorited the book.
    TRADABLE : str
        Users willing to trade.
    WISHLISTED : str
        Users who wishlisted the book.
    RATED : str
        Users who rated the book.
    """

    READ = "leram"
    CURRENTLY_READING = "lendo"
    WANT_TO_READ = "vaoler"
    REREADING = "relendo"
    ABANDONED = "abandonaram"
    FAVORITED = "favoritos"
    TRADABLE = "trocam"
    WISHLISTED = "desejam"
    RATED = "avaliaram"


class BookcaseOption(IntEnum):
    """Filter options for a user's virtual bookcase.

    Attributes
    ----------
    ALL : int
        All books.
    READ : int
        Books marked as read.
    CURRENTLY_READING : int
        Currently reading books.
    WANT_TO_READ : int
        Books the user wants to read.
    REREADING : int
        Books being reread.
    ABANDONED : int
        Books abandoned by the user.
    FAVORITE : int
        Favorite books.
    WISHLIST : int
        Books in the wishlist.
    RATED : int
        Books rated by the user.
    REVIEWED : int
        Books reviewed by the user.
    OWNED : int
        Books owned by the user.
    TRADABLE : int
        Books available for trade.
    LOANED : int
        Books loaned out.
    READING_GOAL : int
        Books in the reading goal.
    EBOOK : int
        E-book editions.
    AUDIOBOOK : int
        Audiobook editions.
    """

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
    """Types of relationship between users.

    Attributes
    ----------
    FRIENDS : str
        Mutually confirmed friends.
    FOLLOWING : str
        Users this user follows.
    FOLLOWERS : str
        Users following this user.
    """

    FRIENDS = "amigos"
    FOLLOWING = "seguidos"
    FOLLOWERS = "seguidores"


class UserGender(StrEnum):
    """Gender codes returned by the API.

    Attributes
    ----------
    MALE : str
        Male gender.
    FEMALE : str
        Female gender.
    """

    MALE = "M"
    FEMALE = "F"


class BrazilianState(StrEnum):
    """Brazilian state abbreviations used in user profiles.

    Attributes
    ----------
    ACRE : str
        Acre.
    ALAGOAS : str
        Alagoas.
    AMAPA : str
        Amapá.
    AMAZONAS : str
        Amazonas.
    BAHIA : str
        Bahia.
    CEARA : str
        Ceará.
    DISTRITO_FEDERAL : str
        Distrito Federal.
    ESPIRITO_SANTO : str
        Espírito Santo.
    GOIAS : str
        Goiás.
    MARANHAO : str
        Maranhão.
    MATO_GROSSO : str
        Mato Grosso.
    MATO_GROSSO_DO_SUL : str
        Mato Grosso do Sul.
    MINAS_GERAIS : str
        Minas Gerais.
    PARA : str
        Pará.
    PARAIBA : str
        Paraíba.
    PARANA : str
        Paraná.
    PERNAMBUCO : str
        Pernambuco.
    PIAUI : str
        Piauí.
    RIO_DE_JANEIRO : str
        Rio de Janeiro.
    RIO_GRANDE_DO_NORTE : str
        Rio Grande do Norte.
    RIO_GRANDE_DO_SUL : str
        Rio Grande do Sul.
    RONDONIA : str
        Rondônia.
    RORAIMA : str
        Roraima.
    SANTA_CATARINA : str
        Santa Catarina.
    SAO_PAULO : str
        São Paulo.
    SERGIPE : str
        Sergipe.
    TOCANTINS : str
        Tocantins.
    """

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
