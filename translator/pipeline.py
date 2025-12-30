__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
import json
from pathlib import Path

from translator.languages import Languages
from translator.llm import Translator
from translator.phrases import Phrase, PhrasesManager, PhraseTranslationStatus
from translator.translations import TranslationsManager

__all__ = [
    "TranslatorFactory",
    "TranslatorPipeline",
]


class TranslatorFactory(ABC):

    @abstractmethod
    def build_tm(self, path: Path) -> TranslationsManager:
        pass

    @abstractmethod
    def build_pm(self, path: Path) -> PhrasesManager:
        pass


class TranslatorPipeline:

    def __init__(
        self,
        tr_factory: TranslatorFactory,
        tr_path: Path,
        translator: Translator,
    ) -> None:
        self.__tr_factory = tr_factory
        self.__tr_manager = tr_factory.build_tm(tr_path)
        self.__traslator = translator

    def __process_without_ex(self, tr_lang: Languages, tr_files: list[Path]) -> None:
        for file in tr_files:
            print(f"Generate translations for {file}")
            ms_manager = self.__tr_factory.build_pm(file)
            print(f"->Read phrases from {file}")
            phrases = list(ms_manager.read_phrases())
            if len(phrases) == 0:
                continue
            print(f"->Pass to translator {len(phrases)} phrases")
            phrases_tr = self.__traslator.translate(phrases, tr_lang)
            ms_manager.write_phrases(phrases_tr)

    def __process_with_ex(self, tr_lang: Languages, ex_lang: Languages, tr_ex_files: list[tuple[Path, Path]]) -> None:
        for tr_file, ex_file in tr_ex_files:
            print(f"Generate translations for {tr_file}")
            tr_pm = self.__tr_factory.build_pm(tr_file)
            ex_pm = self.__tr_factory.build_pm(ex_file)
            print(f"->Read phrases from {tr_file}")
            tr_ps_dict = {phrase.original: phrase for phrase in tr_pm.read_phrases()}
            print(f"->Read phrases from {ex_file}")
            ex_ps = ex_pm.read_phrases()
            print("->Merge phrases")
            for phrase in ex_ps:
                ps = tr_ps_dict.get(phrase.original, None)
                if ps:
                    ps.translations[ex_lang] = phrase.translations[ex_lang]

            phrases = list(tr_ps_dict.values())
            if len(phrases) == 0:
                continue
            print(f"->Pass to translator {len(phrases)} phrases")
            phrases_tr = self.__traslator.translate(phrases, tr_lang)
            cannot_write = tr_pm.write_phrases(phrases_tr)
            print("->Cannot write translations for phrases:")
            print("\n---->".join({p.original for p in cannot_write}))


    def run(self, tr_lang: Languages, ex_lang: Languages | None = None) -> None:
        self.__tr_manager.prepare(tr_lang)
        try:
            if ex_lang is None:
                tr_files = self.__tr_manager.translations_without_ex()
                self.__process_without_ex(tr_lang, tr_files)
            else:
                tr_ex_files = self.__tr_manager.translations_with_ex(ex_lang)
                self.__process_with_ex(tr_lang, ex_lang, tr_ex_files)
        finally:
            self.__tr_manager.finalize()
