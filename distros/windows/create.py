""""""

# Standard library modules.
import os
import sys
import json
import glob
import shutil
import subprocess
import tempfile
import argparse
import logging

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
        requirements = [
            "pymontecarlo",
            "pymontecarlo-gui",
            "pymontecarlo-casino2",
            "pymontecarlo-penepma",
            "pypenelopetools",
        ]
        embed = self._create_embed(requirements)

        logger.info("create distribution")
        os.makedirs(dist_dir, exist_ok=True)
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
            logger.info("adding requirement {}".format(requirement))
            embed.add_requirement(requirement)

        return embed


class DebugWindowsDistribution(_WindowsDistribution):
    def __init__(self):
        super().__init__()
        self.tempdir = None

    def _find_local_project_directory(self, requirement):
        dist = pkg_resources.get_distribution(requirement)

        projectdir = dist.location
        setup_filepath = os.path.join(projectdir, "setup.py")
        if not os.path.exists(setup_filepath):
            raise ValueError("Cannot find setup.py in project {}".format(projectdir))

        return projectdir

    def _get_version(self):
        projectdir = self._find_local_project_directory("pymontecarlo-gui")

        args = [sys.executable, "setup.py", "--version"]
        out = subprocess.run(args, cwd=projectdir, check=True, stdout=subprocess.PIPE)

        return out.stdout.decode("ascii").strip()

    def _create_embed(self, requirements):
        embed = super()._create_embed(requirements)

        # Create temporary folder to save wheels
        self.tempdir = tempfile.mkdtemp()

        # Run bdist_wheel
        logger.info("running bdist_wheel on requirements")
        for requirement in requirements:
            projectdir = self._find_local_project_directory(requirement)
            logger.debug('found "{0}" for "{1}"'.format(projectdir, requirement))

            args = [sys.executable, "setup.py", "bdist_wheel", "-d", self.tempdir]
            logger.debug("running {}".format(" ".join(args)))
            subprocess.run(args, cwd=projectdir, check=True)

        # Add wheel
        logger.info("adding wheel")
        for filepath in glob.glob(os.path.join(self.tempdir, "*.whl")):
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

    basedir = os.path.dirname(__file__)
    dist_dir = os.path.join(basedir, "dist")
    parser.add_argument(
        "-d",
        "--dist",
        default=dist_dir,
        help="Destination directory (default: {})".format(dist_dir),
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
