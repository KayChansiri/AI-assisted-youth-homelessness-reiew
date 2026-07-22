"""
List available OpenAI models.

This optional script helps users see which model names are available
to their OpenAI account.

Do not paste API keys directly into this file.
"""

import os
from openai import OpenAI


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Set it as an environment variable first."
        )

    client = OpenAI(api_key=api_key)
    models_response = client.models.list()

    print("Available models:\n")

    for model in models_response.data:
        print(model.id)


if __name__ == "__main__":
    main()
