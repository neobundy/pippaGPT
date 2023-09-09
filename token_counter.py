from pathlib import Path
import tiktoken
import settings
import os
import helper_module
from dotenv import load_dotenv

import characters


def token_counter(text="", is_file=False):
    load_dotenv()
    text = Path(text).read_text(encoding="utf-8") if is_file else text
    encoding = tiktoken.encoding_for_model(settings.DEFAULT_GPT_MODEL)
    return len(encoding.encode(text))


if __name__ == "__main__":
    helper_module.log(os.path.basename(__file__), "test")
    print("Custom Instructions")
    ci_tokens = token_counter(characters.CUSTOM_INSTRUCTIONS)
    print(f"Tokens: {ci_tokens}\n")
    print(f"Total Tokens: {ci_tokens}")
