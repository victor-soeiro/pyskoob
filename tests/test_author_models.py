import pytest

from pyskoob.models.author import (
    AuthorBook,
    AuthorProfile,
    AuthorStats,
    AuthorVideo,
)


def test_author_profile_defaults():
    profile = AuthorProfile(name="A")
    assert profile.links == {}
    assert profile.tags == []
    assert profile.gender_percentages == {}
    assert profile.books == [] and profile.videos == []
    assert isinstance(profile.stats, AuthorStats)


@pytest.mark.parametrize(
    "model,expected",
    [
        (AuthorBook(), {"url": None, "title": None, "img_url": None}),
        (AuthorVideo(), {"url": None, "thumbnail_url": None, "title": None}),
    ],
)
def test_author_models_defaults(model, expected):
    assert model.model_dump() == expected
