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

    """
    Abstract base class for managing your program resources.
    The program may contain several files with translations.
    This class allows you to obtain files with translations of phrases for selected languages.

    This class defines the interface for preparing, retrieving, and finalizing
    translation resources.
    """

    @abstractmethod
    def prepare(self, lang: Languages) -> None:
        """
        Prepares the resources for a given language.
        :param lang: The language for which resources are being prepared.
        """
        pass

    @abstractmethod
    def translations_without_ex(self) -> list[Path]:
        """
        :return: A list of paths to translation files if no examples are used.
        """
        pass

    @abstractmethod
    def translations_with_ex(self, ex_lang: Languages) -> list[tuple[Path, Path]]:
        """
        :return: A list of tuples, where each tuple contains two paths:
        the path to a translation file and the path to its corresponding
        file containing example translations for a given language.
        """
        pass

    @abstractmethod
    def finalize(self) -> None:
        """
        Finalizes the resource management, performing any necessary cleanup.
        """
        pass
