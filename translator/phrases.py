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
    """
    Represents a single phrase with its original text and translations into various languages.

    :ivar original: The original text of the phrase, typically in English.
    :ivar translations: A dictionary mapping `Languages` enums to their translated string.
    """
    original: str
    translations: dict[Languages, str]

    def __hash__(self) -> int:
        return hash(self.original)

    def to_dict(self, translation_langs: list[Languages] | None = None) -> dict[str, str]:
        """
        Converts the Phrase object into a dictionary format suitable for serialization,
        including the original and specified translations.

        The original phrase is always included under the key "en".
        If `translation_langs` is provided, only translations for those languages are included.
        Otherwise, all available translations are included.

        :param translation_langs: An optional list of `Languages` enums to include in the output.
                                  If None, all available translations are included.
        :return: A dictionary where keys are language short codes (e.g., "en", "ru")
                 and values are the corresponding phrase strings.
        """
        phrase: dict[str, str] = {"en": self.original}
        if translation_langs is not None:
            for lang in translation_langs:
                phrase[lang.short] = self.translations.get(lang, "")
        return phrase

    @classmethod
    def from_dict(cls, translations: dict[str, str]) -> "Phrase":
        """
        Creates a Phrase object from a dictionary representation.

        The dictionary must contain an "en" key for the original phrase.
        Other keys are expected to be language short codes (e.g., "ru", "de")
        mapping to their translated strings.

        :param translations: A dictionary containing the original phrase and its translations.
                             Must include an "en" key.
        :raises KeyError: If the "en" key (original phrase) is missing from the input dictionary.
        :return: A new `Phrase` instance populated with the provided data.
        """
        original = translations.get("en", None)
        if not original:
            raise KeyError("Translations must contain original ('en') phrase")
        phrase_translations = {}
        for lang, phrase in translations.items():
            if lang == "en":
                continue
            phrase_translations[Languages(lang)] = phrase
        return cls(original, phrase_translations)


class PhraseTranslationStatus(Enum):
    """
    Represents the translation status of a phrase, as used by Qt Linguist.

    :cvar FINISHED: The translation is complete and up-to-date.
    :cvar UNFINISHED: The translation is incomplete or needs review.
    :cvar VANISHED: The original phrase no longer exists in the source.
    :cvar OBSOLETE: The original phrase has changed, and the translation is outdated.
    """
    FINISHED = ""
    UNFINISHED = "unfinished"
    VANISHED = "vanished"
    OBSOLETE = "obsolete"


class PhrasesManager(ABC):
    """
    Abstract base class for managing phrases from a one source.

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
