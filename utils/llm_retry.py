# 提供结构化 LLM JSON 输出的统一重试能力。

from typing import Any

from langchain_core.exceptions import OutputParserException


DEFAULT_MAX_ATTEMPTS = 3


def invoke_json_with_retry(
    chain,
    inputs: dict[str, Any],
    max_attempts: int = DEFAULT_MAX_ATTEMPTS
) -> dict[str, Any]:

    last_error: Exception | None = None

    for attempt in range(
        1,
        max_attempts + 1
    ):
        try:
            result = chain.invoke(inputs)

            if not isinstance(
                result,
                dict
            ):
                raise ValueError(
                    "Structured LLM output must "
                    "be a JSON object."
                )

            return result

        except (
            OutputParserException,
            ValueError
        ) as error:

            last_error = error

            if attempt == max_attempts:
                raise

    raise RuntimeError(
        "Structured LLM generation failed."
    ) from last_error