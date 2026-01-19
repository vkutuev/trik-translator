__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

import sys
from pathlib import Path
import subprocess
from typing import Iterator

from translator.languages import Languages
from translator.resources import ResourcesManager

__all__ = [
    "TrikStudioTranslationsManager",
]


class TrikStudioTranslationsManager(ResourcesManager):
    """
    Manages TRIK Studio translation files (TS-files).

    This class allows generating new translation files or fixing XML escaping
    sequences for TRIK Studio using the local qmake feature named autolupdate.
    It also provides methods to retrieve translation files for a selected language.
    """

    def __init__(self, studio_path: Path) -> None:
        self.__studio_path = studio_path.absolute()
        self.__qrtranslations = studio_path / "qrtranslations"
        self.__lang: Languages | None = None

    def __autolupdate(self) -> None:
        """
        Runs qmake with the 'autolupdate' configuration to generate or update translation files.
        """
        print("Run qmake autolupdate")
        alupdate_dir = Path.cwd() / "trik-studio-lupdate"
        alupdate_dir.mkdir(exist_ok=True)
        log_file = alupdate_dir / "log.txt"
        qmake = "qmake"
        if sys.platform.lower().startswith("win"):
            qmake = qmake + ".exe"
        with open(log_file, "w") as outfile:
            subprocess.run(
                [qmake, "-r", "CONFIG+=autolupdate", self.__studio_path],
                cwd=alupdate_dir,
                stdout=outfile,
                stderr=subprocess.STDOUT,
            )

    def prepare(self, lang: Languages) -> None:
        """
        Prepares the manager for a specific language.
        This involves setting the target language and running autolupdate.

        :param lang: The `Languages` enum member representing the target language.
        """
        # Add language
        self.__lang = lang
        tr_dir = self.__qrtranslations / self.__lang.short
        tr_dir.mkdir(exist_ok=True)
        # Run autolupdate
        self.__autolupdate()

    @staticmethod
    def __get_file_list(dir_path: Path, tr_lang: str) -> Iterator[Path]:
        """
        Helper method to get a list of translation files in a given directory.

        :param dir_path: The path to the directory to search.
        :param tr_lang: The short code of the translation language (e.g., "en", "ru").
        :return: An iterator of `Path` objects representing the translation files.
        """
        files = []
        for d_root, _, d_files in dir_path.walk():
            for f in d_files:
                files.append(d_root.joinpath(f).relative_to(dir_path))
        return filter(lambda p: p.name.endswith(f"_{tr_lang}.ts"), files)

    def translations_without_ex(self) -> list[Path]:
        """
        Retrieves a list of translation files for the prepared language.

        :raises RuntimeError: If `prepare()` has not been called.
        :return: A list of `Path` objects to the translation files.
        """
        if self.__lang is None:
            raise RuntimeError("prepare() method must be called before get_translations()")
        tr_lang = self.__lang
        tr_dir = self.__qrtranslations / tr_lang.short
        files = TrikStudioTranslationsManager.__get_file_list(tr_dir, tr_lang.short)
        return list(map(lambda f: tr_dir / f, files))

    def translations_with_ex(self, ex_lang: Languages) -> list[tuple[Path, Path]]:
        """
        Retrieves a list of translation files for the prepared language,
        paired with their corresponding files in an example language.

        :param ex_lang: The `Languages` enum member representing the example language.
        :raises RuntimeError: If `prepare()` has not been called.
        :return: A list of tuples, where each tuple contains `(target_lang_path, example_lang_path)`.
        """
        if self.__lang is None:
            raise RuntimeError("prepare() method must be called before get_translations()")
        tr_lang = self.__lang
        tr_dir = self.__qrtranslations / tr_lang.short
        ex_dir = self.__qrtranslations / ex_lang.short
        files = map(
            lambda p: str(p).removesuffix(f"_{tr_lang.short}.ts"),
            TrikStudioTranslationsManager.__get_file_list(tr_dir, tr_lang.short)
        )
        files = list(map(lambda f: (tr_dir / (f + f"_{tr_lang}.ts"), ex_dir / (f + f"_{ex_lang}.ts")), files))
        return files

    def finalize(self) -> None:
        """
        Finalizes the translation process, typically by running autolupdate again.
        """
        # Hack to reduce diff (escape &apos; and &quot;)
        self.__autolupdate()
