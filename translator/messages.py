__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from translator.languages import Languages

__all__ = [
    "Message",
    "MessageType",
    "MessagesManager",
]


@dataclass
class Message:
    message: str
    translations: dict[Languages, str]

    def to_dict(self, translation_langs: list[Languages] = []) -> dict[str, str]:
        message: dict[str, str] = {"en": self.message}
        for lang in translation_langs:
            message[lang.short] = self.translations.get(lang, "")
        return message

    @classmethod
    def from_dict(cls, message_translations: dict[str, str]) -> "Message":
        original = message_translations.get("en", None)
        if not original:
            raise KeyError("Translations must contain original ('en') message")
        translations = {}
        for lang, message in message_translations.items():
            if lang == "en":
                continue
            translations[Languages(lang)] = message
        return cls(original, translations)


class MessageType(Enum):
    FINISHED = ""
    UNFINISHED = "unfinished"
    VANISHED = "vanished"
    OBSOLETE = "obsolete"


class MessagesManager(ABC):
    @abstractmethod
    def read_messages(self, mtype: MessageType = MessageType.UNFINISHED) -> list[Message]:
        pass

    @abstractmethod
    def write_messages(self, messages: list[Message]) -> None:
        pass
