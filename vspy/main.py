import asyncio

from vspy.core import App
from vspy.core.args import Arguments
from vspy.core.utils import is_empty_folder, is_windows, silence_event_loop_closed


def main() -> None:
    """Starting point."""
    args = Arguments.parse()
    if is_empty_folder(args.target):
        print("Target is either not a folder or nonempty.")
        return
    if is_windows():
        silence_event_loop_closed()
    app = App(args)
    try:
        asyncio.run(app.start())
    except KeyboardInterrupt:
        print("Cancelled")
        app.cleanup()


if __name__ == "__main__":
    main()
