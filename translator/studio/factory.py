__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"


from pathlib import Path

from translator.pipeline import TranslationsManagerFactory
from translator.studio.phrases import TrikStudioPhrasesManager
from translator.studio.traslations import TrikStudioTranslationsManager

__all__ = [
    "TrikStudioFactory",
]


class TrikStudioFactory(TranslationsManagerFactory):

    def build_rm(self, path: Path) -> TrikStudioTranslationsManager:
        return TrikStudioTranslationsManager(path)

    def build_pm(self, path: Path) -> TrikStudioPhrasesManager:
        return TrikStudioPhrasesManager(path)
