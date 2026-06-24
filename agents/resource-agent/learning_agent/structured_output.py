import json
from collections.abc import Mapping
from typing import Any

from learning_agent.llm import ProviderRouter


class StructuredOutputError(RuntimeError):
    pass


def complete_json(
    provider_router: ProviderRouter,
    system_prompt: str,
    user_prompt: str,
    operation: str,
    *,
    repair_attempts: int = 1,
) -> dict[str, Any]:
    raw_text, provider, fallback_used = provider_router.complete(system_prompt, user_prompt)
    if fallback_used:
        raise StructuredOutputError(f"{operation} unexpectedly used fallback provider {provider}.")
    try:
        parsed = extract_json_object(raw_text)
    except StructuredOutputError:
        parsed = _repair_json(provider_router, raw_text, operation, repair_attempts)
    if not isinstance(parsed, Mapping):
        raise StructuredOutputError(f"{operation} returned JSON that is not an object.")
    result = dict(parsed)
    result.setdefault("_provider", provider)
    result.setdefault("_executionMode", "LLM")
    result.setdefault("_fallbackUsed", False)
    return result


def extract_json_object(text: str) -> dict[str, Any]:
    candidates = _json_candidates(text)
    last_error = ""
    for candidate in candidates:
        try:
            value = json.loads(candidate)
            if isinstance(value, dict):
                return value
            last_error = f"expected object, got {type(value).__name__}"
        except json.JSONDecodeError as exc:
            last_error = str(exc)
    raise StructuredOutputError(f"No valid JSON object found in model output: {last_error}")


def _json_candidates(text: str) -> list[str]:
    stripped = (text or "").strip()
    candidates: list[str] = []
    if stripped:
        candidates.append(stripped)
    fence_markers = ["```json", "```JSON", "```"]
    for marker in fence_markers:
        start = stripped.find(marker)
        if start == -1:
            continue
        start += len(marker)
        end = stripped.find("```", start)
        if end != -1:
            candidates.append(stripped[start:end].strip())
    balanced = _balanced_json_object(stripped)
    if balanced:
        candidates.append(balanced)
    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def _balanced_json_object(text: str) -> str:
    start = text.find("{")
    if start == -1:
        return ""
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""


def _repair_json(
    provider_router: ProviderRouter,
    raw_text: str,
    operation: str,
    repair_attempts: int,
) -> dict[str, Any]:
    repair_prompt = (
        "You repair malformed model output into strict JSON. "
        "Return one JSON object only. Do not add Markdown, comments, or explanations."
    )
    current = raw_text
    for attempt in range(max(0, repair_attempts)):
        repaired, provider, fallback_used = provider_router.complete(
            repair_prompt,
            f"Operation: {operation}\nMalformed output:\n{current}",
        )
        if fallback_used:
            raise StructuredOutputError(f"{operation} JSON repair unexpectedly used fallback provider {provider}.")
        try:
            return extract_json_object(repaired)
        except StructuredOutputError:
            current = repaired
    raise StructuredOutputError(f"{operation} did not return valid JSON after repair.")


def as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def as_int(value: Any, default: int, minimum: int = 1, maximum: int | None = None) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    number = max(minimum, number)
    if maximum is not None:
        number = min(maximum, number)
    return number


def as_float(value: Any, default: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return min(max(number, minimum), maximum)


def as_list(value: Any, default: list[Any] | None = None) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return list(default or [])
    return [value]
