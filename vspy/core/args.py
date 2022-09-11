import argparse
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Dict, List, Optional, Union

ArgMap = Dict[str, Union[str, bool]]


class ArgType(IntEnum):
    """Data type of argument."""

    BOOL = 0
    STR = 1


@dataclass
class ArgInfo:
    """Meta data for arguments."""

    arg_type: ArgType
    arg_prompt_message: Optional[str] = None
    arg_invalid_message: Optional[str] = None
    arg_validaiton: Callable[[str], bool] = lambda _str: True


def _validate_project_name(name: str) -> bool:
    bad = {"<", ">", "\\", "/", ":", '"', "|", "?", "*"}
    return bool(name) and not set(name).intersection(bad)


class Arguments:
    """Command line argument handler."""

    _REQUIRED_ARGUMENTS = {
        "name": ArgInfo(
            ArgType.STR,
            "Enter project name",
            "Name contains invalid characters",
            _validate_project_name,
        ),
    }

    _OPTIONAL_ARGUMENTS = {
        "debug": ArgInfo(ArgType.BOOL),
        "skip": ArgInfo(ArgType.BOOL),
        "target": ArgInfo(ArgType.STR),
        "description": ArgInfo(ArgType.STR, "Enter project description"),
        "repository": ArgInfo(ArgType.STR, "Enter repository"),
        "author": ArgInfo(ArgType.STR, "Enter author"),
        "email": ArgInfo(ArgType.STR, "Enter email"),
        "keywords": ArgInfo(ArgType.STR, "Enter keywords"),
    }

    @classmethod
    def parse(cls, sys_args: Optional[List[str]] = None) -> "Arguments":
        """Parse command line arguments into a data class."""
        parser = Arguments._get_parser()
        args: ArgMap = vars(parser.parse_args(args=sys_args))
        keywords = args.get("keywords", "")
        if keywords:
            assert isinstance(keywords, str)
            args["keywords"] = " ".join(keywords.split(","))
        return cls(args)

    def __init__(self, args: ArgMap) -> None:
        self._str_args: Dict[str, str] = {}
        self._bool_args: Dict[str, bool] = {}
        self._populate(args)
        self._prompt_remaining()

    @property
    def debug(self) -> bool:
        """Run in debug mode."""
        return self._bool_args["debug"]

    @property
    def target(self) -> str:
        """Target path."""
        return self._str_args["target"]

    @property
    def name(self) -> str:
        """Name of the project."""
        return self._str_args["name"]

    @property
    def description(self) -> str:
        """Project description."""
        return self._str_args.get("description", "")

    @property
    def repository(self) -> str:
        """Project repository."""
        return self._str_args.get("repository", "")

    @property
    def author(self) -> str:
        """Project author."""
        return self._str_args.get("author", "")

    @property
    def email(self) -> str:
        """Project email."""
        return self._str_args.get("email", "")

    @property
    def keywords(self) -> str:
        """Project keywords."""
        return self._str_args.get("keywords", "")

    @property
    def _skip(self) -> bool:
        return self._bool_args["skip"]

    def _add(self, key: str, val: Union[str, bool]) -> None:
        if isinstance(val, str):
            self._str_args[key] = val
        else:
            self._bool_args[key] = val

    def _is_set_and_valid(
        self,
        arg_key: str,
        arg_type: ArgType,
        arg_validation: Optional[Callable[[str], bool]],
    ) -> bool:
        if arg_type == ArgType.BOOL:
            return arg_key in self._bool_args
        return arg_key in self._str_args and (
            arg_validation is None or arg_validation(self._str_args[arg_key])
        )

    def _populate(self, args: ArgMap) -> None:
        for key, val in args.items():
            self._add(key, val)

    def _prompt_remaining(self) -> None:
        self._prompt_group(Arguments._REQUIRED_ARGUMENTS)
        if not self._skip:
            print("Remaining fields can be empty")
            self._prompt_group(Arguments._OPTIONAL_ARGUMENTS)

    def _prompt_group(self, group: Dict[str, ArgInfo]) -> None:
        for arg, arg_info in group.items():
            if not self._is_set_and_valid(
                arg, arg_info.arg_type, arg_info.arg_validaiton
            ):
                while True:
                    val = Arguments._prompt(arg_info.arg_prompt_message)
                    if arg_info.arg_validaiton(val):
                        self._add(arg, val)
                        break
                    print(arg_info.arg_invalid_message)

    @staticmethod
    def _prompt(msg: Optional[str]) -> str:
        """Promt message and read input."""
        print(f"{msg}:", end=" ", flush=True)
        return input().strip()

    @staticmethod
    def _get_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Process some integers.")
        parser.add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="store_true",
            default=False,
            help="Run in debug mode in debug mode.",
        )
        parser.add_argument(
            "-s",
            "--skip",
            dest="skip",
            default=False,
            action="store_true",
            help="Skip all optional prompts.",
        )
        parser.add_argument(
            "-t",
            "--target",
            dest="target",
            default=".",
            type=str,
            help="The target directory to generate project in.",
        )
        parser.add_argument(
            "-n",
            "--name",
            dest="name",
            type=str,
            help="The name of the project.",
        )
        parser.add_argument(
            "--author",
            dest="author",
            type=str,
            help="The author of the project.",
        )
        parser.add_argument(
            "--repository",
            dest="repository",
            type=str,
            help="The repository of the project.",
        )
        parser.add_argument(
            "--keywords",
            dest="keywords",
            type=str,
            help="Comma separated list of keywords describing the project.",
        )
        parser.add_argument(
            "--email",
            dest="email",
            type=str,
            help="The email for the project.",
        )
        parser.add_argument(
            "--description",
            dest="description",
            type=str,
            help="The description for the project.",
        )
        return parser
