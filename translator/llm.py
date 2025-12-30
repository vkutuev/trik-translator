__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from translator.languages import Languages
from translator.phrases import Phrase
from translator.prompts import get_prompt_without_example, get_prompt_with_example

__all__ = [
    "Translator",
    "LlmTranslator",
]


class Translator(ABC):
    @abstractmethod
    def translate(self, phrases: list[Phrase], tr_lang: Languages, ex_lang: Languages | None = None) -> list[Phrase]:
        pass


class LlmTranslator(Translator):

    def __init__(self, temperature=0.15, max_output_tokens=4000) -> None:
        load_dotenv()
        model = os.getenv("OPENAI_MODEL")
        if model is None:
            raise RuntimeError("Environment variable OPENAI_MODEL")
        self.__model = model
        self.__client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            project=os.getenv("OPENAI_PROJECT")
        )
        self.__temperature = temperature
        self.__max_output_tokens = max_output_tokens
        self.__without_example_prompts: dict[Languages, str] = {}
        self.__with_example_prompts: dict[tuple[Languages, Languages], str] = {}

    def __translate_json(self, phrases_json: str, tr_lang: Languages, ex_lang: Languages | None = None) -> str:
        if ex_lang is None:
            prompt = get_prompt_without_example(tr_lang)
        else:
            prompt = get_prompt_with_example(tr_lang, ex_lang)
        response = self.__client.responses.create(
            model=self.__model,
            temperature=self.__temperature,
            max_output_tokens=self.__max_output_tokens,
            instructions=prompt,
            input=phrases_json,
        )
        return response.output_text

    def translate(self, phrases: list[Phrase], tr_lang: Languages, ex_lang: Languages | None = None) -> list[Phrase]:
        if not phrases:
            return []

        json_phs = json.dumps([p.to_dict() for p in phrases], ensure_ascii=False)
        if len(json_phs.split()) > self.__max_output_tokens // 4:
            split_len = len(phrases) // 2
            return (self.translate(phrases[:split_len], tr_lang, ex_lang)
                    + self.translate(phrases[split_len:], tr_lang, ex_lang))

        json_phs_tr = self.__translate_json(json_phs, tr_lang, ex_lang)
        traslated_dict = None
        try:
            traslated_dict = json.loads(json_phs_tr)
        except Exception:
            # log warnin cannot parse LLM response JSON
            print("-->Cannot parse output JSON try again!!!")
            pass
        if traslated_dict is None:
            return self.translate(phrases, tr_lang, ex_lang)
        return [Phrase.from_dict(tr) for tr in traslated_dict if "en" in tr]
