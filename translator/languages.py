__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from enum import Enum


__all__ = [
    "Languages",
]


class Languages(Enum):
    """Enumeration of supported languages."""
    RU = "ru"
    FR = "fr"
    ES = "es"
    VI = "vi"

    def __init__(self, short: str) -> None:
        self.short = short
        match short:
            case "ru": self.long = "Russian"
            case "fr": self.long = "French"
            case "es": self.long = "Spanish"
            case "vi": self.long = "Vietnamese"
            case _: raise ValueError(f"Unknown language: '{short}'")

    def __str__(self) -> str:
        """Return the value for use in argparse help messages."""
        return self.short

    @classmethod
    def from_locale_code(cls, locale_code: str) -> "Languages":
        language_code = locale_code.split('_')[0].split('-')[0]
        return cls(language_code)
