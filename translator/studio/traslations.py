__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from pathlib import Path
import subprocess
from typing import Iterator

from translator.languages import Languages
from translator.resources import ResourcesManager

__all__ = [
    "TrikStudioTranslationsManager",
]


class TrikStudioTranslationsManager(ResourcesManager):

    def __init__(self, studio_path: Path) -> None:
        self.__studio_path = studio_path.absolute()
        self.__qrtranslations = studio_path / "qrtranslations"
        self.__lang: Languages | None = None

    def __autolupdate(self) -> None:
        print("Run qmake autolupdate")
        alupdate_dir = Path.cwd() / "trik-studio-lupdate"
        alupdate_dir.mkdir(exist_ok=True)
        log_file = alupdate_dir / "log.txt"
        with open(log_file, "w") as outfile:
            subprocess.run(
                ["qmake", "-r", "CONFIG+=autolupdate", self.__studio_path],
                cwd=alupdate_dir,
                stdout=outfile,
                stderr=subprocess.STDOUT,
            )

    def prepare(self, lang: Languages) -> None:
        # Add language
        self.__lang = lang
        tr_dir = self.__qrtranslations / self.__lang.short
        tr_dir.mkdir(exist_ok=True)
        # Run autolupdate
        self.__autolupdate()

    @staticmethod
    def __get_file_list(dir_path: Path, tr_lang: str) -> Iterator[Path]:
        files = []
        for d_root, _, d_files in dir_path.walk():
            for f in d_files:
                files.append(d_root.joinpath(f).relative_to(dir_path))
        return filter(lambda p: p.name.endswith(f"_{tr_lang}.ts"), files)

    def translations_without_ex(self) -> list[Path]:
        if self.__lang is None:
            raise RuntimeError("prepare() method must be called before get_translations()")
        tr_lang = self.__lang
        tr_dir = self.__qrtranslations / tr_lang.short
        files = TrikStudioTranslationsManager.__get_file_list(tr_dir, tr_lang.short)
        return list(map(lambda f: tr_dir / f, files))

    def translations_with_ex(self, ex_lang: Languages) -> list[tuple[Path, Path]]:
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
        # Hack to reduce diff (escape &apos; and &quot;)
        self.__autolupdate()
