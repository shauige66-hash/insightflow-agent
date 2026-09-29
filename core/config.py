import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_model: str


def get_settings() -> Settings:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com"
    )
    model = os.getenv("DEEPSEEK_MODEL")

    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is missing")

    if not model:
        raise ValueError("DEEPSEEK_MODEL is missing")

    return Settings(
        deepseek_api_key=api_key,
        deepseek_base_url=base_url,
        deepseek_model=model
    )