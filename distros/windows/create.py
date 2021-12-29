""""""

# Standard library modules.
import sys
import json
import glob
import shutil
import subprocess
import tempfile
import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Third party modules.
from py2win.embed import EmbedPython
import requests
import packaging.version
import pkg_resources

# Local modules.

# Globals and constants variables.


class _WindowsDistribution:
    def _get_version(self):
        return "0.0.0"

    def _create_embed(self, requirements):
        version = self._get_version()
        embed = EmbedPython("pymontecarlo", version)

        embed.add_script(
            "pymontecarlo_gui.__main__", "main", "pymontecarlo", console=False
        )

        return embed

    def create(self, dist_dir):
        dist_dir = Path(dist_dir)
        dist_dir.mkdir(parents=True, exist_ok=True)

        requirements = [
            "pymontecarlo",
            "pymontecarlo-gui",
            "pymontecarlo-casino2",
            "pymontecarlo-penepma",
            "pypenelopetools",
        ]
        embed = self._create_embed(requirements)

        logger.info("create distribution")
        embed.run(dist_dir, clean=True, zip_dist=True)


class PyPIWindowsDistribution(_WindowsDistribution):

    URL_PATTERN = "https://pypi.python.org/pypi/{package}/json"

    def _get_version(self):
        """
        Return version of package on pypi.python.org using json.
        https://stackoverflow.com/questions/28774852/pypi-api-how-to-get-stable-package-version
        """
        package = "pymontecarlo-gui"
        req = requests.get(self.URL_PATTERN.format(package=package))
        version = packaging.version.parse("0")
        if req.status_code == requests.codes.ok:  # @UndefinedVariable
            j = json.loads(req.text.encode(req.encoding))
            if "releases" in j:
                releases = j["releases"]
                for release in releases:
                    ver = packaging.version.parse(release)
                    if not ver.is_prerelease:
                        version = max(version, ver)
        return version

    def _create_embed(self, requirements):
        embed = super()._create_embed(requirements)

        for requirement in requirements:
            logger.info(f"adding requirement {requirement}")
            embed.add_requirement(requirement)

        return embed


class DebugWindowsDistribution(_WindowsDistribution):
    def __init__(self):
        super().__init__()
        self.tempdir = None

    def _find_local_project_directory(self, requirement):
        try:
            dist = pkg_resources.get_distribution(requirement)
        except pkg_resources.DistributionNotFound:
            logger.info(f"Distribution not found for {requirement}")
            projectdir = Path.cwd().joinpath(requirement)
        else:
            projectdir = Path(dist.location)

        setup_filepath = projectdir.joinpath("setup.py")
        if not setup_filepath.exists():
            raise ValueError(f"Cannot find setup.py in project {projectdir}")

        return projectdir

    def _get_version(self):
        projectdir = self._find_local_project_directory("pymontecarlo-gui")

        args = [sys.executable, "setup.py", "--version"]
        out = subprocess.run(args, cwd=projectdir, check=True, stdout=subprocess.PIPE)

        return out.stdout.decode("ascii").strip()

    def _create_embed(self, requirements):
        embed = super()._create_embed(requirements)

        # Create temporary folder to save wheels
        self.tempdir = Path(tempfile.mkdtemp())

        # Run bdist_wheel
        logger.info("running bdist_wheel on requirements")
        for requirement in requirements:
            projectdir = self._find_local_project_directory(requirement)
            logger.debug(f'found "{projectdir}" for "{requirement}"')

            args = [sys.executable, "setup.py", "bdist_wheel", "-d", str(self.tempdir)]
            logger.debug(f"running {' '.join(args)}")
            subprocess.run(args, cwd=projectdir, check=True)

        logger.info(f"created wheels: {', '.join(map(str, self.tempdir.iterdir()))}")

        # Add wheel
        logger.info("adding wheel")
        for filepath in self.tempdir.glob("*.whl"):
            embed.add_wheel(filepath)

        return embed

    def create(self, dist_dir):
        try:
            super().create(dist_dir)
        finally:
            if self.tempdir:
                shutil.rmtree(self.tempdir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="Create windows distribution of pymontecarlo"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--debug", action="store_true", help="Using local projects")
    group.add_argument("--pypi", action="store_true", help="Using PyPI")

    dist_dir = Path(__file__).parent.joinpath("dist").resolve()
    parser.add_argument(
        "-d",
        "--dist",
        type=Path,
        default=dist_dir,
        help=f"Destination directory (default: {dist_dir})",
    )

    args = parser.parse_args()

    if args.debug:
        distro = DebugWindowsDistribution()
    elif args.pypi:
        distro = PyPIWindowsDistribution()

    dist_dir = args.dist

    distro.create(dist_dir)


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
