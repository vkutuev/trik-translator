# TRIK Translator

This project provides tools for translating TRIK Studio UI files.

## Installation

### With [uv](https://github.com/astral-sh/uv)

1. Install dependencies

    ```bash
    uv sync
    ```

2. Run tool

    ```bash
    uv run main.py <args>
    ```

## Configuration

The application uses an OpenAI-compatible Large Language Model (LLM) for translation.
You need to configure the connection to the LLM by creating a `.env` 
file in the project root with the following variables:

```
OPENAI_MODEL="your-model-name"
OPENAI_API_KEY="your-api-key"
OPENAI_BASE_URL="https://your.openai.compatible.host/v1"
OPENAI_PROJECT="your-project-id" # Optional, depending on your provider
```

Replace the placeholder values with your actual LLM provider's details.

## Usage

To run the translator, execute the `main.py` script:

```bash
uv run main.py <path to program> <target language>
```

To get more information get help:

```bash
uv run main.py -h
```

## License

This project is licensed under the terms of the MIT License specified in the [LICENSE](LICENSE) file.
