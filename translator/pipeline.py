__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
import json
from pathlib import Path

from translator.languages import Languages
from translator.llm import Translator
from translator.phrases import Phrase, PhrasesManager, PraseTranslationStatus
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
    def build_mm(self, path: Path) -> PhrasesManager:
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
            ms_manager = self.__tr_factory.build_mm(file)
            print(f"->Read messages from {file}")
            messages = ms_manager.read_messages(PraseTranslationStatus.FINISHED)
            messages = [m.to_dict() for m in messages]
            if len(messages) == 0:
                continue
            json_ms = json.dumps(messages, ensure_ascii=False)
            if len(json_ms.split()) < 1300:
                # Pass to translator
                print(f"->Pass to translator {len(messages)} messages")
                json_ms_tr = self.__traslator.translate(json_ms, tr_lang)
                # Process translated messages
                try:
                    traslated = json.loads(json_ms_tr)
                except Exception:
                    print("Cannot parse JSON")
                    print(json_ms_tr)
                    raise
                messages_tr = [Phrase.from_dict(tr) for tr in traslated if "en" in tr]
                print(f"->Write messages to {file}")
                ms_manager.write_messages(messages_tr)
            else:
                msgs_split = len(messages) // 2
                ms_1 = messages[:msgs_split]
                print(f"--->Pass 1 part to translator {len(ms_1)} messages")
                json_ms = json.dumps(ms_1, ensure_ascii=False)
                json_ms_tr = self.__traslator.translate(json_ms, tr_lang)
                try:
                    traslated = json.loads(json_ms_tr)
                except Exception:
                    print("Cannot parse JSON")
                    print(json_ms_tr)
                    raise
                messages_tr = [Phrase.from_dict(tr) for tr in traslated if "en" in tr]
                print(f"->Write messages to {file}")
                ms_manager.write_messages(messages_tr)
                ms_2 = messages[msgs_split:]
                print(f"--->Pass 1 part to translator {len(ms_1)} messages")
                json_ms = json.dumps(ms_2, ensure_ascii=False)
                json_ms_tr = self.__traslator.translate(json_ms, tr_lang)
                try:
                    traslated = json.loads(json_ms_tr)
                except Exception:
                    print("Cannot parse JSON")
                    print(json_ms_tr)
                    raise
                messages_tr = [Phrase.from_dict(tr) for tr in traslated if "en" in tr]
                print(f"->Write messages to {file}")
                ms_manager.write_messages(messages_tr)

    def __process_with_ex(self, tr_lang: Languages, ex_lang: Languages, tr_ex_files: list[tuple[Path, Path]]) -> None:
        for tr_file, ex_file in tr_ex_files:
            print(f"Generate translations for {tr_file}")
            tr_mm = self.__tr_factory.build_mm(tr_file)
            ex_mm = self.__tr_factory.build_mm(ex_file)
            print(f"->Read messages from {tr_file}")
            tr_ms_dict = {message.original: message for message in tr_mm.read_messages()}
            print(f"->Read messages from {ex_file}")
            ex_ms = ex_mm.read_messages(PraseTranslationStatus.FINISHED)
            print("->Merge messages")
            for message in ex_ms:
                ms = tr_ms_dict.get(message.original, None)
                if ms:
                    ms.translations[ex_lang] = message.translations[ex_lang]
            messages = [m.to_dict([ex_lang]) for m in tr_ms_dict.values()]
            if len(messages) == 0:
                continue

            print(f"->Pass to translator {len(messages)} messages")

            json_ms = json.dumps(messages, ensure_ascii=False)
            if len(json_ms.split()) < 1300:
                json_ms_tr = self.__traslator.translate(json_ms, tr_lang, ex_lang)
                # Process translated messages
                try:
                    traslated = json.loads(json_ms_tr)
                except Exception:
                    print("Cannot parse JSON")
                    print(json_ms_tr)
                    raise
                messages_tr = [Phrase.from_dict(tr) for tr in traslated]
                print(f"->Write messages to {tr_file}")
                tr_mm.write_messages(messages_tr)
            else:
                msgs_split = len(messages) // 2
                ms_1 = messages[:msgs_split]
                print(f"--->Pass 1 part to translator {len(ms_1)} messages")
                json_ms = json.dumps(ms_1, ensure_ascii=False)
                json_ms_tr = self.__traslator.translate(json_ms, tr_lang, ex_lang)
                try:
                    traslated = json.loads(json_ms_tr)
                except Exception:
                    print("Cannot parse JSON")
                    print(json_ms_tr)
                    raise
                messages_tr = [Phrase.from_dict(tr) for tr in traslated]
                print(f"--->Write messages to {tr_file}")
                tr_mm.write_messages(messages_tr)
                ms_2 = messages[msgs_split:]
                print(f"--->Pass 2 part to translator {len(ms_2)} messages")
                json_ms = json.dumps(ms_2, ensure_ascii=False)
                json_ms_tr = self.__traslator.translate(json_ms, tr_lang, ex_lang)
                try:
                    traslated = json.loads(json_ms_tr)
                except Exception:
                    print("Cannot parse JSON")
                    print(json_ms_tr)
                    raise
                messages_tr = [Phrase.from_dict(tr) for tr in traslated]
                print(f"--->Write messages to {tr_file}")
                tr_mm.write_messages(messages_tr)

    def run(self, tr_lang: Languages, ex_lang: Languages | None = None) -> None:
        self.__tr_manager.prepare(tr_lang)
        if ex_lang is None:
            tr_files = self.__tr_manager.translations_without_ex()
            self.__process_without_ex(tr_lang, tr_files)
        else:
            tr_ex_files = self.__tr_manager.translations_with_ex(ex_lang)
            self.__process_with_ex(tr_lang, ex_lang, tr_ex_files)
        self.__tr_manager.finalize()
