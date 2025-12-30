__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from pathlib import Path
from lxml import etree as ET

from translator.languages import Languages
from translator.phrases import Phrase, PraseTranslationStatus, PhrasesManager


class TrikStudioMessageManager(PhrasesManager):

    def __init__(self, file: Path) -> None:
        self.__file = file
        try:
            self.__tree: ET.ElementTree[ET.Element[str]] = ET.parse(file)
            self.__lang: Languages = TrikStudioMessageManager.__detect_lang(self.__tree.getroot())
        except ET.ParseError as e:
            raise ET.ParseError(f"File {file} cannot be parsed") from e

    @staticmethod
    def __detect_lang(ts: ET.Element) -> Languages:
        if ts.tag != "TS":
            raise SyntaxError("Qt TS root tag must be <TS>")
        locale_code = ts.attrib.get("language", None)
        if locale_code is None:
            raise SyntaxError("<TS> tag in Qt TS file doesn't contain 'language' attribute")
        return Languages.from_locale_code(locale_code)

    @staticmethod
    def __parse_translation(translation: ET.Element) -> tuple[PraseTranslationStatus, str]:
        trtype = PraseTranslationStatus(translation.attrib.get("type", ""))
        translated = translation.text if translation.text else ""
        return trtype, translated

    def read_messages(self, mtype: PraseTranslationStatus = PraseTranslationStatus.UNFINISHED) -> list[Phrase]:
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
                trtype, translated = TrikStudioMessageManager.__parse_translation(translation)
                if trtype == mtype:
                    file_messages.append(Phrase(original, {self.__lang: translated}))
        return file_messages

    def write_messages(self, messages: list[Phrase]) -> None:
        translations: dict[str, str] = {m.original: m.translations.get(self.__lang, "") for m in messages}
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
                trtype, _ = TrikStudioMessageManager.__parse_translation(translation)
                #if trtype == MessageType.UNFINISHED and translations.get(original, ""):
                if trtype == PraseTranslationStatus.FINISHED and translations.get(original, ""):
                    # translation.attrib.pop("type")
                    translation.text = translations[original]
        self.__tree.write(self.__file, encoding="utf-8", xml_declaration=True)
