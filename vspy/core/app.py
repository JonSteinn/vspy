from vspy.core.args import Arguments
from vspy.core.project import Project
from vspy.core.utils import clean_dir


class App:
    """The runnable unit of the package."""

    def __init__(self, args: Arguments) -> None:
        """Initialize the application."""
        self._project = Project(args)
        self._target = args.target

    async def start(self) -> None:
        """Start the application."""
        await self._project.set_versions()
        await self._project.create_project()

    def cleanup(self) -> None:
        """Remove any created files."""
        clean_dir(self._target)
