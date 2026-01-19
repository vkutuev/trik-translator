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
    """
    Abstract base class for a translator.
    Defines the interface for translating a list of phrases.
    """
    @abstractmethod
    def translate(self, phrases: list[Phrase], tr_lang: Languages, ex_lang: Languages | None = None) -> list[Phrase]:
        pass


class LlmPromptsFactory(ABC):
    """
    Abstract base class for a factory that provides prompts for the LLM translator.
    """

    @abstractmethod
    def get_prompt(self, tr_lang: Languages) -> str:
        """
        Returns a prompt string for the LLM translator when no example language is provided.

        :param tr_lang: The target language for translation.
        :return: A string representing the prompt for the LLM.
        """
        pass

    @abstractmethod
    def get_prompt_ex(self, tr_lang: Languages, ex_lang: Languages) -> str:
        """
        Returns a prompt string for the LLM translator when an example language is provided.

        :param tr_lang: The target language for translation.
        :param ex_lang: The example language to be used in the prompt.
        :return: A string representing the prompt for the LLM.
        """
        pass

class LlmTranslator(Translator):
    """
    A translator implementation that uses a Large Language Model (LLM) for translation.

    This class interacts with an OpenAI-compatible LLM to translate lists of phrases
    from a source language to a target language, optionally using an example language.
    It handles splitting large inputs and retrying translation on parsing errors.
    """

    def __init__(self,
        prompts_factory: LlmPromptsFactory,
        temperature=0.15,
        max_output_tokens=4000
    ) -> None:
        """
        Initializes the LlmTranslator.

        :param prompts_factory: An instance of LlmPromptsFactory to get prompts for the LLM.
        :type prompts_factory: LlmPromptsFactory
        :param temperature: The sampling temperature to use for the LLM, defaults to 0.15.
        :type temperature: float
        :param max_output_tokens: The maximum number of tokens to generate in the LLM's output, defaults to 4000.
        :type max_output_tokens: int
        :raises RuntimeError: If the OPENAI_MODEL environment variable is not set.
        """
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
        """
        Internal method to send a JSON string of phrases to the LLM for translation.

        It constructs the appropriate prompt using the prompts factory and sends the request
        to the configured OpenAI-compatible LLM.

        :param phrases_json: A JSON string representing the list of phrases to translate.
        :param tr_lang: The target language for translation.
        :param ex_lang: An optional example language to guide the translation.
        :return: A JSON string containing the translated phrases.
        """
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
        """
        Translates a list of phrases using the LLM.

        :param phrases: A list of Phrases to be translated.
        :param tr_lang: The target language for translation.
        :param ex_lang: An optional example language to guide the translation.
        :return: A list of translated Phrases.
        """
        if not phrases:
            return []

        json_phs = json.dumps([p.to_dict() for p in phrases], ensure_ascii=False)
        # If the input JSON string of phrases exceeds a certain length, it recursively
        # splits the input into smaller chunks to avoid exceeding the LLM's output limits.
        # It also includes a retry mechanism if the LLM's response cannot be parsed as JSON.
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
