import pyskoob


def test_root_imports():
    assert hasattr(pyskoob, "SkoobClient")
    assert hasattr(pyskoob, "models")
    assert hasattr(pyskoob, "ParsingError")
