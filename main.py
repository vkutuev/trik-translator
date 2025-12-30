import argparse
from pathlib import Path

from translator.languages import Languages
from translator.llm import LlmTranslator
from translator.pipeline import TranslatorPipeline
from translator.studio.factory import TrikStudioFactory


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("path", type=str, help="Path to directory with trik studio translations")
    # parser.add_argument("--with-translation", action="store_true", help="Whether add translation to output JSON")
    # args = parser.parse_args()
    # path = Path(args.path)
    studio_dir = Path("../trik-studio/")
    pipeline = TranslatorPipeline(
        TrikStudioFactory(),
        studio_dir,
        LlmTranslator(),
    )
    pipeline.run(Languages.RU)


if __name__ == "__main__":
    main()
