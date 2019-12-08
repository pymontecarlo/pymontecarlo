""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.util.token import Token, TokenState, TqdmToken

# Globals and constants variables.


def test_token_initalize():
    token = Token("test")

    assert token.name == "test"
    assert token.state == TokenState.NOTSTARTED
    assert token.progress == 0.0
    assert token.status == "Not started"


def test_token_update():
    token = Token("test")
    token.update(0.5, "Progress made", TokenState.RUNNING)

    assert token.state == TokenState.RUNNING
    assert token.progress == 0.5
    assert token.status == "Progress made"


def test_subtoken_initialize():
    token = Token("test")
    subtoken1 = token.create_subtoken("subtest1")
    subtoken2 = token.create_subtoken("subtest2")

    assert token.name == "test"
    assert token.state == TokenState.NOTSTARTED
    assert token.progress == 0.0
    assert token.status == "Not started"
    assert subtoken1.name == "subtest1"
    assert token.state == TokenState.NOTSTARTED
    assert subtoken1.progress == 0.0
    assert subtoken1.status == "Not started"
    assert subtoken2.name == "subtest2"
    assert token.state == TokenState.NOTSTARTED
    assert subtoken2.progress == 0.0
    assert subtoken2.status == "Not started"


def test_subtoken_update():
    token = Token("test")
    subtoken1 = token.create_subtoken("subtest1")
    subtoken2 = token.create_subtoken("subtest2")

    subtoken1.update(0.5, "progress made in subtest1")

    assert token.state == TokenState.RUNNING
    assert token.progress == 0.5
    assert token.status == "progress made in subtest1"
    assert subtoken1.state == TokenState.RUNNING
    assert subtoken1.progress == 0.5
    assert subtoken1.status == "progress made in subtest1"
    assert subtoken2.state == TokenState.NOTSTARTED
    assert subtoken2.progress == 0.0
    assert subtoken2.status == "Not started"

    subtoken2.update(0.25, "progress made in subtest2")

    assert token.state == TokenState.RUNNING
    assert token.progress == (0.5 + 0.25) / 2
    assert token.status == "progress made in subtest2"
    assert subtoken1.state == TokenState.RUNNING
    assert subtoken1.progress == 0.5
    assert subtoken1.status == "progress made in subtest1"
    assert subtoken2.state == TokenState.RUNNING
    assert subtoken2.progress == 0.25
    assert subtoken2.status == "progress made in subtest2"


def test_token_start():
    token = Token("test")
    token.start("foo")

    assert token.state == TokenState.RUNNING
    assert token.progress == 0.01
    assert token.status == "foo"


def test_token_done():
    token = Token("test")
    token.done("foo")

    assert token.state == TokenState.DONE
    assert token.progress == 1.0
    assert token.status == "foo"


def test_token_cancel():
    token = Token("test")
    token.cancel("foo")

    assert token.state == TokenState.CANCELLED
    assert token.progress == 1.0
    assert token.status == "foo"


def test_token_error():
    token = Token("test")
    token.error("foo")

    assert token.state == TokenState.ERROR
    assert token.progress == 1.0
    assert token.status == "foo"


def test_token_subtokens():
    token = Token("test")
    subtoken1 = token.create_subtoken("subtest1")
    subtoken2 = token.create_subtoken("subtest2")

    subtokens = token.get_subtokens()
    assert len(subtokens) == 2
    assert subtoken1 in subtokens
    assert subtoken2 in subtokens


def test_token_subtokens_with_category():
    token = Token("test")
    subtoken1 = token.create_subtoken("subtest1", "cat1")
    subtoken2 = token.create_subtoken("subtest2", "cat2")

    subtokens = token.get_subtokens()
    assert len(subtokens) == 2
    assert subtoken1 in subtokens
    assert subtoken2 in subtokens

    subtokens = token.get_subtokens("cat1")
    assert len(subtokens) == 1
    assert subtoken1 in subtokens

    subtokens = token.get_subtokens("cat2")
    assert len(subtokens) == 1
    assert subtoken2 in subtokens


def test_tqdm_token(capsys):
    token = TqdmToken("test")
    assert not capsys.readouterr().err

    token.start()
    assert capsys.readouterr().err.strip().startswith("test:")

    token.done()
    assert capsys.readouterr().err.strip().startswith("test: 100%")


def test_tqdm_subtoken(capsys):
    token = TqdmToken("test")
    subtoken = token.create_subtoken("subtest")

    subtoken.start()
    assert capsys.readouterr().err.strip().startswith("subtest:")

    subtoken.done()
