from enum import Enum


__all__ = [
    "Languages",
]


class Languages(Enum):
    """Enumeration of supported languages."""
    RU = ("ru", "Russian")
    FR = ("fr", "French")
    ES = ("es", "Spanish")
    VI = ("vi", "Vietnamese")

    def __init__(self, short: str, long: str) -> None:
        self.short = short
        self.long = long

    def __str__(self) -> str:
        """Return the value for use in argparse help messages."""
        return self.short
