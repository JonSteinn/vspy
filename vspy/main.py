import signal
import sys
import types

from .info import get_info
from .project import create_project


def sigint_handler(sig: int, _frame: types.FrameType) -> None:
    """For terminating infinite task."""
    if sig == signal.SIGINT:
        print("\nCancelling.")
        sys.exit(0)


def main() -> None:
    """Starting point."""
    signal.signal(signal.SIGINT, sigint_handler)
    create_project(get_info())


if __name__ == "__main__":
    main()
