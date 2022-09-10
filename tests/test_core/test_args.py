from tests.testutils.mocks import MockArgs, MockInput
from vspy.core.args import Arguments


def test_arguments_only():
    with MockArgs(
        "-d",
        "-t",
        "path",
        "-n",
        "name",
        "--author",
        "me",
        "--repository",
        "repo",
        "--keywords",
        "a,b,c,d,e",
        "--email",
        "mymail",
        "--description",
        "something",
    ):
        args = Arguments.parse()
        assert args.author == "me"
        assert args.debug
        assert args.description == "something"
        assert args.email == "mymail"
        assert args.keywords == "a b c d e"
        assert args.name == "name"
        assert args.repository == "repo"
        assert args.target == "path"


def test_arguments_skip():
    with MockArgs("-s", "-n", "name"):
        args = Arguments.parse()
        assert args.name == "name"
        assert args.target == "."


def test_arguments_invalid_name():
    with MockArgs("-s"):
        with MockInput(*("<", ">", "\\", "/", ":", '"', "|", "?", "*"), "valid_name"):
            args = Arguments.parse()
            assert args.name == "valid_name"


def test_arguments_just_prompt_missing():
    with MockArgs(
        "-d",
        "-t",
        "path",
        "-n",
        "name",
        "--author",
        "me",
        "--repository",
        "repo",
        "--email",
        "mymail",
        "--description",
        "something",
    ):
        kwords = "some keywords not comma sep"
        with MockInput(kwords):
            args = Arguments.parse()
            assert args.keywords == kwords


def test_arguments_default_and_prompt():
    with MockArgs():
        with MockInput(
            "project_name", "my_description", "my_repo", "me", "my_mail", "a b c d"
        ):
            args = Arguments.parse()
            assert args.author == "me"
            assert not args.debug
            assert args.description == "my_description"
            assert args.email == "my_mail"
            assert args.keywords == "a b c d"
            assert args.name == "project_name"
            assert args.repository == "my_repo"
            assert args.target == "."
