import json
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
            "离线生成器已接管。本回答依据本地知识库、学习画像和资源模板生成，"
            "适合无 API Key 的比赛演示环境。\n\n"
            f"任务摘要：{user_prompt[:700]}"
        )


class XfyunSparkProvider:
    name = "xfyun_spark"

    def __init__(self, settings: AgentSettings) -> None:
        self.settings = settings

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
        response = httpx.post(
            self.settings.xfyun_endpoint,
            headers=headers,
            json=payload,
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return self._extract_content(data)

    def _authorization_token(self) -> str:
        if self.settings.xfyun_api_password:
            return self.settings.xfyun_api_password
        return f"{self.settings.xfyun_api_key}:{self.settings.xfyun_api_secret}"

    def _extract_content(self, data: dict) -> str:
        if "choices" in data and data["choices"]:
            message = data["choices"][0].get("message", {})
            content = message.get("content")
            if content:
                return str(content)
        return json.dumps(data, ensure_ascii=False)


class ProviderRouter:
    def __init__(self, settings: AgentSettings) -> None:
        self.settings = settings
        self.offline = OfflineLearningProvider()
        self.spark = XfyunSparkProvider(settings)
        self.last_error = ""

    @property
    def active_name(self) -> str:
        if self.settings.provider == "xfyun_spark" and self.spark.available:
            return self.spark.name
        return self.offline.name

    def complete(self, system_prompt: str, user_prompt: str) -> tuple[str, str, bool]:
        if self.settings.provider == "xfyun_spark":
            try:
                result = self.spark.complete(system_prompt, user_prompt)
                self.last_error = ""
                return result, self.spark.name, False
            except Exception as exc:
                self.last_error = str(exc)
                fallback_text = self.offline.complete(
                    system_prompt,
                    user_prompt + f"\n\n主模型降级原因：{exc}",
                )
                return fallback_text, self.offline.name, True
        return self.offline.complete(system_prompt, user_prompt), self.offline.name, False

    def status(self) -> dict:
        return {
            "configuredProvider": self.settings.provider,
            "activeProvider": self.active_name,
            "xfyunConfigured": self.spark.available,
            "xfyunCredentialMode": self.spark.credential_mode,
            "xfyunModel": self.settings.xfyun_model,
            "xfyunEndpoint": self.settings.xfyun_endpoint,
            "fallbackProvider": self.offline.name,
            "fallbackReady": True,
            "lastError": self.last_error,
        }
