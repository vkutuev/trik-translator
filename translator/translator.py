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

__all__ = [
    "Translator",
    "LlmTranslator",
    "LlmPromptsFactory",
]


class Translator(ABC):
    @abstractmethod
    def translate(self, phrases: list[Phrase], tr_lang: Languages, ex_lang: Languages | None = None) -> list[Phrase]:
        pass


class LlmPromptsFactory(ABC):
    @abstractmethod
    def get_prompt(self, tr_lang: Languages) -> str:
        pass

    @abstractmethod
    def get_prompt_ex(self, tr_lang: Languages, ex_lang: Languages) -> str:
        pass

class LlmTranslator(Translator):

    def __init__(self,
        prompts_factory: LlmPromptsFactory,
        temperature=0.15,
        max_output_tokens=4000
    ) -> None:
        self.__prompts_factory = prompts_factory
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
            prompt = self.__prompts_factory.get_prompt(tr_lang)
        else:
            prompt = self.__prompts_factory.get_prompt_ex(tr_lang, ex_lang)
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
        translated_dict = None
        try:
            translated_dict = json.loads(json_phs_tr)
        except Exception:
            # log warnin cannot parse LLM response JSON
            print("-->Cannot parse output JSON try again!!!")
            pass
        if translated_dict is None:
            return self.translate(phrases, tr_lang, ex_lang)
        return [Phrase.from_dict(tr) for tr in translated_dict if "en" in tr]
