"""Project Info."""

import os

import tomlkit


class ProjectInfo:
    """ProjectInfo."""

    def __init__(self, main_path: str):
        self.main_path = main_path

    def get_project_name(self) -> str:
        """Get name from pyproject.toml."""
        with open(
            os.path.join(self.main_path, "pyproject.toml"),
            encoding="utf-8",
        ) as toml_file:
            data = tomlkit.parse(toml_file.read())
        return data["project"]["name"]  # type: ignore

    def get_project_version(self) -> str:
        """Get version from pyproject.toml."""
        with open(
            os.path.join(self.main_path, "pyproject.toml"),
            encoding="utf-8",
        ) as toml_file:
            data = tomlkit.parse(toml_file.read())
        return data["project"]["version"]  # type: ignore
