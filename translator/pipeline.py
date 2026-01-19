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
    "TranslationsManagerFactory",
    "TranslatorPipeline",
]


class TranslationsManagerFactory(ABC):
    """
    Abstract base class for creating managers for resources and phrases.

    This factory is responsible for providing concrete implementations of
    :class:`ResourcesManager` and :class:`PhrasesManager` based on the
    specific requirements of the translation pipeline.
    """

    @abstractmethod
    def build_rm(self, path: Path) -> ResourcesManager:
        """
        Builds and returns a :class:`ResourcesManager` instance.

        :param path: The path to the resources.
        :return: An instance of :class:`ResourcesManager`.
        """
        pass

    @abstractmethod
    def build_pm(self, path: Path) -> PhrasesManager:
        """
        Builds and returns a :class:`PhrasesManager` instance.

        :param path: The path to the phrases.
        :return: An instance of :class:`PhrasesManager`.
        """
        pass


class TranslatorPipeline:
    """
    This class represents the main pipeline for translating phrases.
    It orchestrates the process of reading, translating, and writing phrases using a TranslatorFactory and a Translator.
    """

    def __init__(
        self,
        tr_factory: TranslationsManagerFactory,
        tr_path: Path,
        translator: Translator,
    ) -> None:
        self.__tr_factory = tr_factory
        self.__rs_manager = tr_factory.build_rm(tr_path)
        self.__translator = translator
        self.__all_written = False

    def __process_without_ex(self, tr_lang: Languages, tr_files: list[Path]) -> None:
        """
        Processes translation files without example translations.

        This method iterates through a list of translation files, reads phrases from each,
        translates them into the target language, and then writes the translated phrases back.
        It updates an internal flag if any translations cannot be written.

        :param tr_lang: The target language for translation.
        :param tr_files: A list of paths to the translation files to be processed.
        :return: None
        """
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
        """
        This method iterates through pairs of translation files (target and example),
        reads phrases from both, merges the existing translations into the target phrases,
        translates the merged phrases into the target language, and then writes them back.
        It updates an internal flag if any translations cannot be written.

        :param tr_lang: The target language for new translations.
        :param ex_lang: The existing language whose translations will be merged.
        :param tr_ex_files: A list of tuples, where each tuple contains
                            (path to target translation file, path to existing translation file).
        :return: None
        """

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
                print("->Cannot write translations for phrases:\n---->")
                print("\n---->".join({p.original for p in cannot_write}))

    def run(self, tr_lang: Languages, ex_lang: Languages | None = None) -> None:
        """
        Executes the translation pipeline.

        This method prepares the resources, extract phrases to translate
        (merges them with example translations if provided),
        translate them using given translator, and write the translated phrases back,
        and finally finalizes the resources.
        It also prints a warning if some translations could not be written.

        :param tr_lang: The target language for translation.
        :param ex_lang: An optional existing language to merge translations from. Defaults to None.
        """

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
            if not self.__all_written:
                print("->Cannot write some translations! Try to run program again!!!")
