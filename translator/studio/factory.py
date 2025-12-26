__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"


from pathlib import Path

from translator.pipeline import TranslatorFactory
from translator.studio.messages import TrikStudioMessageManager
from translator.studio.traslations import TrikStudioTranslationsManager

__all__ = [
    "TrikStudioFactory",
]


class TrikStudioFactory(TranslatorFactory):

    def build_tm(self, path: Path) -> TrikStudioTranslationsManager:
        return TrikStudioTranslationsManager(path)

    def build_mm(self, path: Path) -> TrikStudioMessageManager:
        return TrikStudioMessageManager(path)
