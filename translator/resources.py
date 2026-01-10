__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
from pathlib import Path

from translator.languages import Languages

__all__ = [
    "ResourcesManager",
]


class ResourcesManager(ABC):

    @abstractmethod
    def prepare(self, lang: Languages) -> None:
        pass

    @abstractmethod
    def translations_without_ex(self) -> list[Path]:
        pass

    @abstractmethod
    def translations_with_ex(self, ex_lang: Languages) -> list[tuple[Path, Path]]:
        pass

    @abstractmethod
    def finalize(self) -> None:
        pass
