__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from pathlib import Path
from typing import Iterable

from lxml import etree

from translator.languages import Languages
from translator.phrases import Phrase, PhraseTranslationStatus, PhrasesManager


class TrikStudioPhrasesManager(PhrasesManager):

    def __init__(self, file: Path, ptype: PhraseTranslationStatus = PhraseTranslationStatus.UNFINISHED) -> None:
        self.__file = file
        try:
            self.__tree: etree.ElementTree[etree.Element[str]] = etree.parse(file)
            self.__lang: Languages = TrikStudioPhrasesManager.__detect_lang(self.__tree.getroot())
            self.__ptype = ptype
        except etree.ParseError as e:
            raise etree.ParseError(f"File {file} cannot be parsed") from e

    @staticmethod
    def __detect_lang(ts: etree.Element) -> Languages:
        if ts.tag != "TS":
            raise SyntaxError("Qt TS root tag must be <TS>")
        locale_code = ts.attrib.get("language", None)
        if locale_code is None:
            raise SyntaxError("<TS> tag in Qt TS file doesn't contain 'language' attribute")
        return Languages.from_locale_code(locale_code)

    @staticmethod
    def __parse_translation(translation: etree.Element) -> tuple[PhraseTranslationStatus, str]:
        trtype = PhraseTranslationStatus(translation.attrib.get("type", ""))
        translated = translation.text if translation.text else ""
        return trtype, translated

    def read_phrases(self) -> list[Phrase]:
        root = self.__tree.getroot()
        file_messages: list[Phrase] = []
        for context in root.findall("context"):
            for message in context.findall("message"):
                source = message.find("source")
                if source is None:
                    raise SyntaxError("<message> tag doesn't contain <source> tag")
                original = source.text
                if not original:
                    raise SyntaxError("<message> contains no text ()")
                translation = message.find("translation")
                if translation is None:
                    raise SyntaxError("<message> tag doesn't contain <translation> tag")
                trtype, translated = TrikStudioPhrasesManager.__parse_translation(translation)
                if trtype == self.__ptype:
                    file_messages.append(Phrase(original, {self.__lang: translated}))
        return file_messages

    def write_phrases(self, phrases: Iterable[Phrase]) -> Iterable[Phrase]:
        written: set[str] = set()
        translations: dict[str, str] = {p.original: p.translations.get(self.__lang, "") for p in phrases}
        phrases: dict[str, Phrase] = {p.original: p for p in phrases}
        root = self.__tree.getroot()
        for context in root.findall("context"):
            for message in context.findall("message"):
                source = message.find("source")
                if source is None:
                    raise SyntaxError("<message> tag doesn't contain <source> tag")
                original = source.text
                if not original:
                    raise SyntaxError("<message> contains no text ()")
                translation = message.find("translation")
                if translation is None:
                    raise SyntaxError("<message> tag doesn't contain <translation> tag")
                trtype, _ = TrikStudioPhrasesManager.__parse_translation(translation)
                if trtype == self.__ptype and translations.get(original, ""):
                    if not trtype.FINISHED:
                        translation.attrib.pop("type")
                    translation.text = translations[original]
                    written.add(original)

        self.__tree.write(self.__file, encoding="utf-8", xml_declaration=True)
        return {phrases[pk] for pk in set(phrases.keys()).difference(written)}
