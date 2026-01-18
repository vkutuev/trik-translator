import argparse
from pathlib import Path

from translator.languages import Languages
from translator.studio.prompts import TrikStudioPrompts
from translator.translator import LlmTranslator
from translator.pipeline import TranslatorPipeline
from translator.studio.factory import TrikStudioFactory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str,
                        help="Path to directory with your program, for example, the path to TRIKStudio.")
    parser.add_argument("lang_tr", type=str, choices=list(Languages),
                        help="The language into which the phrases in your program need to be translated.")
    parser.add_argument("--lang_ex", type=str, choices=list(Languages), required=False,
                        help="""The language that translations should be based on as an example.
                        This may be useful when using an LLM-based translator.""")
    args = parser.parse_args()

    pipeline = TranslatorPipeline(
        TrikStudioFactory(),
        Path(args.path),
        LlmTranslator(TrikStudioPrompts()),
    )
    pipeline.run(args.lang_tr, args.lang_ex)


if __name__ == "__main__":
    main()
