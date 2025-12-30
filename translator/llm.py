__author__ = "Vladimir Kutuev"
__copyright__ = "Copyright (c) 2025 Vladimir Kutuev"
__license__ = "SPDX-License-Identifier: MIT"

from abc import ABC, abstractmethod
import os

from openai.types.responses import response_format_text_json_schema_config

from dotenv import load_dotenv
from openai import OpenAI

from translator.languages import Languages
from translator.prompts import get_prompt_without_example, get_prompt_with_example

__all__ = [
    "Translator",
    "LlmTranslator",
]


class Translator(ABC):
    @abstractmethod
    def translate(self, query: str, tr_lang: Languages, ex_lang: Languages | None) -> str:
        pass


class LlmTranslator(Translator):

    def __init__(self, tempreture=0.15) -> None:
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
        self.__temperature = tempreture
        self.__without_example_prompts: dict[Languages, str] = {}
        self.__with_example_prompts: dict[tuple[Languages, Languages], str] = {}

    def translate(self, query: str, tr_lang: Languages, ex_lang: Languages | None = None) -> str:
        if ex_lang is None:
            if tr_lang in self.__without_example_prompts:
                prompt = self.__without_example_prompts[tr_lang]
            else:
                prompt = get_prompt_without_example(tr_lang)
                self.__without_example_prompts[tr_lang] = prompt
        else:
            if (tr_lang, ex_lang) in self.__with_example_prompts:
                prompt = self.__with_example_prompts[(tr_lang, ex_lang)]
            else:
                prompt = get_prompt_with_example(tr_lang, ex_lang)
                self.__with_example_prompts[(tr_lang, ex_lang)] = prompt

        response = self.__client.responses.create(
            model=self.__model,
            temperature=self.__temperature,
            max_output_tokens=4000,
            instructions=prompt,
            input=query,
        )
        return response.output_text
