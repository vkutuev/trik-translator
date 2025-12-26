__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
import json
from pathlib import Path

from translator.languages import Languages
from translator.messages import Message, MessagesManager, MessageType
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
    def build_mm(self, path: Path) -> MessagesManager:
        pass


class TranslatorPipeline:

    def __init__(
        self,
        tr_factory: TranslatorFactory,
        tr_path: Path,
    ) -> None:
        self.__tr_factory = tr_factory
        self.__tr_manager = tr_factory.build_tm(tr_path)

    def __process_without_ex(self, tr_files: list[Path]) -> None:
        for file in tr_files:
            ms_manager = self.__tr_factory.build_mm(file)
            messages = ms_manager.read_messages()
            messages = [m.to_dict() for m in messages]
            json_ms = json.dumps(messages, ensure_ascii=False)
            print(type(json_ms))
            # Pass to translator
            json_ms_tr = json_ms

            messages_tr = [Message.from_dict(tr) for tr in json.loads(json_ms)]
            ms_manager.write_messages(messages_tr)

    def __process_with_ex(self, ex_lang: Languages, tr_ex_files: list[tuple[Path, Path]]) -> None:
        for tr_file, ex_file in tr_ex_files:
            print(tr_file, ex_file)
            tr_mm = self.__tr_factory.build_mm(tr_file)
            ex_mm = self.__tr_factory.build_mm(ex_file)
            tr_ms_dict = {message.message: message for message in tr_mm.read_messages()}
            print(tr_ms_dict)
            ex_ms = ex_mm.read_messages(MessageType.FINISHED)
            print(ex_ms)
            for message in ex_ms:
                ms = tr_ms_dict.get(message.message, None)
                if ms:
                    ms.translations[ex_lang] = message.translations[ex_lang]
            messages = [m.to_dict([ex_lang]) for m in tr_ms_dict.values()]
            json_ms = json.dumps(messages, ensure_ascii=False)
            print(json_ms)
            # Pass to translator
            json_ms_tr = json_ms

            messages_tr = [Message.from_dict(tr) for tr in json.loads(json_ms)]
            tr_mm.write_messages(messages_tr)

    def run(self, tr_lang: Languages, ex_lang: Languages | None) -> None:
        self.__tr_manager.prepare(tr_lang)
        if ex_lang is None:
            tr_files = self.__tr_manager.translations_without_ex()
            self.__process_without_ex(tr_files)
        else:
            tr_ex_files = self.__tr_manager.translations_with_ex(ex_lang)
            self.__process_with_ex(ex_lang, tr_ex_files)
        self.__tr_manager.finalize()
