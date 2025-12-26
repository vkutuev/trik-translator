__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
from pathlib import Path

from translator.languages import Languages

__all__ = [
    "TranslationsManager",
]


class TranslationsManager(ABC):

    @abstractmethod
    def prepare(self, lang: Languages) -> None:
        pass

    @abstractmethod
    def get_translations(self, example_lang: Languages | None = None) -> list[Path] | list[tuple[Path, Path]]:
        pass

    @abstractmethod
    def finalize(self) -> None:
        pass
