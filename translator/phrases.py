__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from translator.languages import Languages

__all__ = [
    "Phrase",
    "PraseTranslationStatus",
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


class PraseTranslationStatus(Enum):
    FINISHED = ""
    UNFINISHED = "unfinished"
    VANISHED = "vanished"
    OBSOLETE = "obsolete"


class PhrasesManager(ABC):

    @abstractmethod
    def read_phrases(self, ptype: PraseTranslationStatus = PraseTranslationStatus.UNFINISHED) -> list[Phrase]:
        pass

    @abstractmethod
    def write_phrases(self, phrases: list[Phrase]) -> None:
        pass
