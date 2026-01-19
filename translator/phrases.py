__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from translator.languages import Languages

__all__ = [
    "Phrase",
    "PhraseTranslationStatus",
    "PhrasesManager",
]


@dataclass
class Phrase:
    original: str
    translations: dict[Languages, str]

    def to_dict(self, translation_langs: list[Languages] | None = None) -> dict[str, str]:
        phrase: dict[str, str] = {"en": self.original}
        if translation_langs is not None:
            for lang in translation_langs:
                phrase[lang.short] = self.translations.get(lang, "")
        return phrase

    @classmethod
    def from_dict(cls, translations: dict[str, str]) -> "Phrase":
        original = translations.get("en", None)
        if not original:
            raise KeyError("Translations must contain original ('en') phrase")
        translations = {}
        for lang, phrase in translations.items():
            if lang == "en":
                continue
            translations[Languages(lang)] = phrase
        return cls(original, translations)


class PhraseTranslationStatus(Enum):
    FINISHED = ""
    UNFINISHED = "unfinished"
    VANISHED = "vanished"
    OBSOLETE = "obsolete"


class PhrasesManager(ABC):
    """
    Abstract base class for managing phrases.

    This class defines the interface for reading and writing phrases,
    which concrete implementations will provide.
    """

    @abstractmethod
    def read_phrases(self) -> Iterable[Phrase]:
        """
        Reads all required phrases from a source.

        :return: Read phrases.
        """
        pass

    @abstractmethod
    def write_phrases(self, phrases: Iterable[Phrase]) -> Iterable[Phrase]:
        """
        Writes phrases to a destination.

        :param phrases: Phrases to be written.
        :return: Phrases that cannot be written for further processing.
        """
        pass
