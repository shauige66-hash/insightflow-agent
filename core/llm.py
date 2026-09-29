from langchain_openai import ChatOpenAI

from core.config import Settings, get_settings


def create_llm(settings: Settings | None = None) -> ChatOpenAI:
    if settings is None:
        settings = get_settings()
    return ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0
    )