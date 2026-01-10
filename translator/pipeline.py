__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
from pathlib import Path

from translator.languages import Languages
from translator.translator import Translator
from translator.phrases import PhrasesManager
from translator.resources import ResourcesManager

__all__ = [
    "TranslatorFactory",
    "TranslatorPipeline",
]


class TranslatorFactory(ABC):

    @abstractmethod
    def build_rm(self, path: Path) -> ResourcesManager:
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
        self.__rs_manager = tr_factory.build_rm(tr_path)
        self.__translator = translator
        self.__all_written = False

    def __process_without_ex(self, tr_lang: Languages, tr_files: list[Path]) -> None:
        self.__all_written = True
        for file in tr_files:
            print(f"Generate translations for {file}")
            ph_manager = self.__tr_factory.build_pm(file)
            print(f"->Read phrases from {file}")
            phrases = list(ph_manager.read_phrases())
            if len(phrases) == 0:
                continue
            print(f"->Pass to translator {len(phrases)} phrases")
            phrases_tr = self.__translator.translate(phrases, tr_lang)
            cannot_write = list(ph_manager.write_phrases(phrases_tr))
            if len(cannot_write) > 0:
                self.__all_written = False
                print("->Cannot write translations for phrases:")
                print("\n---->".join({p.original for p in cannot_write}))

    def __process_with_ex(self, tr_lang: Languages, ex_lang: Languages, tr_ex_files: list[tuple[Path, Path]]) -> None:
        self.__all_written = True
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
            phrases_tr = self.__translator.translate(phrases, tr_lang)
            cannot_write = list(tr_pm.write_phrases(phrases_tr))
            if len(cannot_write) > 0:
                self.__all_written = False
                print("->Cannot write translations for phrases:")
                print("\n---->".join({p.original for p in cannot_write}))


    def run(self, tr_lang: Languages, ex_lang: Languages | None = None) -> None:
        self.__rs_manager.prepare(tr_lang)
        try:
            if ex_lang is None:
                tr_files = self.__rs_manager.translations_without_ex()
                self.__process_without_ex(tr_lang, tr_files)
            else:
                tr_ex_files = self.__rs_manager.translations_with_ex(ex_lang)
                self.__process_with_ex(tr_lang, ex_lang, tr_ex_files)
        finally:
            self.__rs_manager.finalize()
            if self.__all_written:
                print("->Cannot write some translations! Try to run program again!!!")
