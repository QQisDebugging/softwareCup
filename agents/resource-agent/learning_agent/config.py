import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from learning_agent.schemas import ProviderName

# 运行时配置持久化文件：保存用户在设置页切换的供应商/模型/Key，重启后自动恢复
RUNTIME_CONFIG_FILENAME = ".agent-runtime-config.json"


class RuntimeConfigError(RuntimeError):
    """Raised when runtime model configuration cannot be persisted."""


def _split_paths(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def _runtime_config_path() -> Path:
    configured_path = os.getenv("RESOURCE_AGENT_RUNTIME_CONFIG_PATH", "").strip()
    if configured_path:
        return Path(configured_path).expanduser().resolve()
    return Path(__file__).resolve().parents[1] / RUNTIME_CONFIG_FILENAME


def runtime_config_path() -> Path:
    return _runtime_config_path()


def load_runtime_overrides() -> dict:
    path = _runtime_config_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_runtime_overrides(overrides: dict) -> None:
    path = _runtime_config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(overrides, ensure_ascii=False, indent=2)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(payload, encoding="utf-8")
        tmp_path.replace(path)
    except OSError as exc:
        raise RuntimeConfigError(f"Failed to persist runtime agent config to {path}: {exc}") from exc


@dataclass(frozen=True)
class AgentSettings:
    project_root: Path
    provider: ProviderName = "xfyun_spark"
    embedding_dimensions: int = 384
    retrieval_top_k: int = 6
    seed_knowledge_paths: list[str] = field(default_factory=list)
    xfyun_app_id: str = ""
    xfyun_api_key: str = ""
    xfyun_api_secret: str = ""
    xfyun_api_password: str = ""
    xfyun_model: str = "generalv3.5"
    xfyun_endpoint: str = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    request_timeout_seconds: int = 120
    request_retry_attempts: int = 3
    xfyun_cache_enabled: bool = True
    xfyun_cache_dir: str = ".cache/xfyun-spark"
    xfyun_daily_call_limit: int = 20
    # OpenAI 兼容供应商（DeepSeek / 通义 / 智谱 / Kimi / OpenAI 等，统一 /v1/chat/completions）
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    @classmethod
    def from_env(cls) -> "AgentSettings":
        resource_agent_dir = Path(__file__).resolve().parents[1]
        project_root = resource_agent_dir.parents[1]
        default_seed_paths = [
            "data/courses/java-web-software-engineering.json",
            "reference/题目说明.txt",
        ]
        provider = (
            os.getenv("SOFTWARECUP_AGENT_PROVIDER")
            or os.getenv("RESOURCE_AGENT_PROVIDER")
            or "xfyun_spark"
        ).strip().lower()
        if provider not in {"offline", "xfyun_spark", "openai_compatible"}:
            provider = "xfyun_spark"

        # 持久化的运行时覆盖（设置页切换后写入的本地文件）优先于环境变量默认值
        overrides = load_runtime_overrides()
        if isinstance(overrides.get("provider"), str):
            candidate = overrides["provider"].strip().lower()
            if candidate in {"offline", "xfyun_spark", "openai_compatible"}:
                provider = candidate

        def ov(key: str, fallback: str) -> str:
            value = overrides.get(key)
            return value if isinstance(value, str) and value != "" else fallback

        return cls(
            project_root=project_root,
            provider=provider,  # type: ignore[arg-type]
            embedding_dimensions=int(os.getenv("RESOURCE_AGENT_EMBEDDING_DIM", "384")),
            retrieval_top_k=int(os.getenv("RESOURCE_AGENT_RETRIEVAL_TOP_K", "6")),
            seed_knowledge_paths=_split_paths(os.getenv("RESOURCE_AGENT_SEED_PATHS")) or default_seed_paths,
            xfyun_app_id=os.getenv("XFYUN_APP_ID", ""),
            xfyun_api_key=os.getenv("XFYUN_API_KEY", ""),
            xfyun_api_secret=os.getenv("XFYUN_API_SECRET", ""),
            xfyun_api_password=ov("xfyun_api_password", os.getenv("XFYUN_API_PASSWORD", "")),
            xfyun_model=ov("xfyun_model", os.getenv("XFYUN_MODEL", "generalv3.5")),
            xfyun_endpoint=os.getenv("XFYUN_ENDPOINT", "https://spark-api-open.xf-yun.com/v1/chat/completions"),
            request_timeout_seconds=int(os.getenv("RESOURCE_AGENT_TIMEOUT_SECONDS", "120")),
            request_retry_attempts=int(os.getenv("RESOURCE_AGENT_RETRY_ATTEMPTS", "3")),
            xfyun_cache_enabled=os.getenv("XFYUN_CACHE_ENABLED", "true").strip().lower() not in {"0", "false", "no"},
            xfyun_cache_dir=os.getenv("XFYUN_CACHE_DIR", ".cache/xfyun-spark"),
            xfyun_daily_call_limit=int(os.getenv("XFYUN_DAILY_CALL_LIMIT", "20")),
            openai_api_key=ov("openai_api_key", os.getenv("OPENAI_API_KEY", "")),
            openai_base_url=ov("openai_base_url", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/"),
            openai_model=ov("openai_model", os.getenv("OPENAI_MODEL", "gpt-4o-mini")),
        )
