import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Protocol

import httpx

from learning_agent.config import AgentSettings


class ChatProvider(Protocol):
    name: str

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        ...


class OfflineLearningProvider:
    name = "offline"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "本地诊断生成器只保留给开发排障使用；正式资源生成任务必须使用讯飞星火。\n"
            f"诊断提示摘要：{user_prompt[:700]}"
        )


class XfyunSparkProvider:
    name = "xfyun_spark"

    def __init__(self, settings: AgentSettings) -> None:
        self.settings = settings
        self.last_cache_hit = False
        self.last_prompt_hash = ""

    @property
    def available(self) -> bool:
        return bool(self.settings.xfyun_api_password or (self.settings.xfyun_api_key and self.settings.xfyun_api_secret))

    @property
    def credential_mode(self) -> str:
        if self.settings.xfyun_api_password:
            return "APIPassword"
        if self.settings.xfyun_api_key and self.settings.xfyun_api_secret:
            return "APIKey/APISecret"
        return "not_configured"

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if not self.available:
            raise RuntimeError("XFYUN_API_PASSWORD or XFYUN_API_KEY/XFYUN_API_SECRET are not configured.")
        cache_key = self._cache_key(system_prompt, user_prompt)
        self.last_prompt_hash = cache_key
        cached = self._read_cache(cache_key)
        if cached is not None:
            self.last_cache_hit = True
            return cached
        self.last_cache_hit = False
        self._ensure_quota()
        payload = {
            "model": self.settings.xfyun_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.55,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self._authorization_token()}",
            "Content-Type": "application/json",
        }
        response = self._post_with_retry(headers, payload)
        data = response.json()
        content = self._extract_content(data)
        self._write_cache(cache_key, content)
        self._record_usage()
        return content

    def _authorization_token(self) -> str:
        if self.settings.xfyun_api_password:
            return self.settings.xfyun_api_password
        return f"{self.settings.xfyun_api_key}:{self.settings.xfyun_api_secret}"

    def _post_with_retry(self, headers: dict, payload: dict) -> httpx.Response:
        attempts = max(1, self.settings.request_retry_attempts)
        timeout = httpx.Timeout(
            connect=10.0,
            read=float(self.settings.request_timeout_seconds),
            write=30.0,
            pool=10.0,
        )
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = httpx.post(
                    self.settings.xfyun_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code < 500:
                    body = exc.response.text[:300]
                    raise RuntimeError(f"XFYUN request rejected with HTTP {status_code}: {body}") from exc
                last_error = exc
            except httpx.HTTPError as exc:
                last_error = exc
            if attempt < attempts:
                time.sleep(min(2.5, 0.6 * attempt))
        raise RuntimeError(f"XFYUN request failed after {attempts} attempts: {last_error}") from last_error

    def _extract_content(self, data: dict) -> str:
        if "choices" in data and data["choices"]:
            message = data["choices"][0].get("message", {})
            content = message.get("content")
            if content:
                return str(content)
        return json.dumps(data, ensure_ascii=False)

    def _cache_key(self, system_prompt: str, user_prompt: str) -> str:
        raw = "\n".join([
            self.settings.xfyun_endpoint,
            self.settings.xfyun_model,
            system_prompt,
            user_prompt,
        ])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _cache_root(self) -> Path:
        root = Path(self.settings.xfyun_cache_dir)
        if not root.is_absolute():
            root = self.settings.project_root / root
        return root

    def _cache_path(self, cache_key: str) -> Path:
        return self._cache_root() / f"{cache_key}.json"

    def _usage_path(self) -> Path:
        return self._cache_root() / "usage.json"

    def _today_key(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def _read_cache(self, cache_key: str) -> str | None:
        if not self.settings.xfyun_cache_enabled:
            return None
        path = self._cache_path(cache_key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            content = data.get("content")
            return str(content) if content else None
        except (OSError, json.JSONDecodeError):
            return None

    def _write_cache(self, cache_key: str, content: str) -> None:
        if not self.settings.xfyun_cache_enabled:
            return
        root = self._cache_root()
        root.mkdir(parents=True, exist_ok=True)
        payload = {
            "provider": self.name,
            "model": self.settings.xfyun_model,
            "endpoint": self.settings.xfyun_endpoint,
            "promptHash": cache_key,
            "createdAt": datetime.now().isoformat(timespec="seconds"),
            "content": content,
        }
        self._cache_path(cache_key).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_usage(self) -> dict:
        path = self._usage_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _ensure_quota(self) -> None:
        limit = self.settings.xfyun_daily_call_limit
        if limit <= 0:
            return
        usage = self._read_usage()
        today = self._today_key()
        used = int(usage.get(today, 0) or 0)
        if used >= limit:
            raise RuntimeError(
                f"XFYUN daily call limit reached: {used}/{limit}. "
                "Use cached prompts, raise XFYUN_DAILY_CALL_LIMIT only when you intentionally allow more quota, "
                "or set RESOURCE_AGENT_PROVIDER=offline for local diagnostics."
            )

    def _record_usage(self) -> None:
        limit = self.settings.xfyun_daily_call_limit
        if limit <= 0:
            return
        root = self._cache_root()
        root.mkdir(parents=True, exist_ok=True)
        usage = self._read_usage()
        today = self._today_key()
        usage[today] = int(usage.get(today, 0) or 0) + 1
        self._usage_path().write_text(json.dumps(usage, ensure_ascii=False, indent=2), encoding="utf-8")


class OpenAiCompatibleProvider:
    """OpenAI 兼容供应商：覆盖 OpenAI / DeepSeek / 通义 / 智谱 / Kimi 等，
    统一走 {base_url}/chat/completions 接口。"""

    name = "openai_compatible"

    def __init__(self, settings: AgentSettings) -> None:
        self.settings = settings

    @property
    def available(self) -> bool:
        return bool(self.settings.openai_api_key and self.settings.openai_base_url and self.settings.openai_model)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if not self.available:
            raise RuntimeError("OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL are not configured.")
        endpoint = f"{self.settings.openai_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.55,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        timeout = httpx.Timeout(
            connect=10.0,
            read=float(self.settings.request_timeout_seconds),
            write=30.0,
            pool=10.0,
        )
        attempts = max(1, self.settings.request_retry_attempts)
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = httpx.post(endpoint, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                if "choices" in data and data["choices"]:
                    content = data["choices"][0].get("message", {}).get("content")
                    if content:
                        return str(content)
                return json.dumps(data, ensure_ascii=False)
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code < 500:
                    body = exc.response.text[:300]
                    raise RuntimeError(f"OpenAI-compatible request rejected with HTTP {status_code}: {body}") from exc
                last_error = exc
            except httpx.HTTPError as exc:
                last_error = exc
            if attempt < attempts:
                time.sleep(min(2.5, 0.6 * attempt))
        raise RuntimeError(f"OpenAI-compatible request failed after {attempts} attempts: {last_error}") from last_error


class ProviderRouter:
    def __init__(self, settings: AgentSettings) -> None:
        self.settings = settings
        self.offline = OfflineLearningProvider()
        self.spark = XfyunSparkProvider(settings)
        self.openai = OpenAiCompatibleProvider(settings)
        self.last_error = ""

    @property
    def active_name(self) -> str:
        if self.settings.provider == "xfyun_spark":
            if self.spark.available:
                return self.spark.name
            return self.settings.provider
        if self.settings.provider == "openai_compatible":
            return self.openai.name
        return self.settings.provider

    def _as_xfyun_error(self) -> str:
        if self.settings.provider not in {"xfyun_spark", "openai_compatible"}:
            return f"Unsupported provider '{self.settings.provider}'."
        return (
            "XFYUN_API_PASSWORD or XFYUN_API_KEY/XFYUN_API_SECRET are not configured. "
            "Please set XFYUN credentials before running generation."
        )

    def complete(self, system_prompt: str, user_prompt: str) -> tuple[str, str, bool]:
        if self.settings.provider == "openai_compatible":
            try:
                result = self.openai.complete(system_prompt, user_prompt)
                self.last_error = ""
                return result, self.openai.name, False
            except Exception as exc:
                self.last_error = str(exc)
                raise RuntimeError(self.last_error)
        if self.settings.provider == "xfyun_spark":
            try:
                result = self.spark.complete(system_prompt, user_prompt)
                self.last_error = ""
                return result, self.spark.name, False
            except Exception as exc:
                self.last_error = str(exc)
                raise RuntimeError(self.last_error)
        raise RuntimeError(self._as_xfyun_error())

    def status(self) -> dict:
        return {
            "configuredProvider": self.settings.provider,
            "activeProvider": self.active_name,
            "xfyunConfigured": self.spark.available,
            "xfyunCredentialMode": self.spark.credential_mode,
            "xfyunModel": self.settings.xfyun_model,
            "xfyunEndpoint": self.settings.xfyun_endpoint,
            "xfyunCacheEnabled": self.settings.xfyun_cache_enabled,
            "xfyunCacheDir": str(self.spark._cache_root()),
            "xfyunDailyCallLimit": self.settings.xfyun_daily_call_limit,
            "xfyunTimeoutSeconds": self.settings.request_timeout_seconds,
            "xfyunRetryAttempts": max(1, self.settings.request_retry_attempts),
            "xfyunTodayCalls": int(self.spark._read_usage().get(self.spark._today_key(), 0) or 0),
            "xfyunLastCacheHit": self.spark.last_cache_hit,
            "xfyunLastPromptHash": self.spark.last_prompt_hash,
            "fallbackProvider": "none",
            "fallbackReady": False,
            "openaiConfigured": self.openai.available,
            "openaiBaseUrl": self.settings.openai_base_url,
            "openaiModel": self.settings.openai_model,
            "lastError": self.last_error,
        }
