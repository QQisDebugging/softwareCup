import os
from dataclasses import dataclass, field
from pathlib import Path

from learning_agent.schemas import ProviderName


def _split_paths(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


@dataclass(frozen=True)
class AgentSettings:
    project_root: Path
    provider: ProviderName = "offline"
    embedding_dimensions: int = 384
    retrieval_top_k: int = 6
    seed_knowledge_paths: list[str] = field(default_factory=list)
    xfyun_api_key: str = ""
    xfyun_api_secret: str = ""
    xfyun_model: str = "generalv3.5"
    xfyun_endpoint: str = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    request_timeout_seconds: int = 25

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
            or "offline"
        ).strip().lower()
        if provider not in {"offline", "xfyun_spark"}:
            provider = "offline"
        return cls(
            project_root=project_root,
            provider=provider,  # type: ignore[arg-type]
            embedding_dimensions=int(os.getenv("RESOURCE_AGENT_EMBEDDING_DIM", "384")),
            retrieval_top_k=int(os.getenv("RESOURCE_AGENT_RETRIEVAL_TOP_K", "6")),
            seed_knowledge_paths=_split_paths(os.getenv("RESOURCE_AGENT_SEED_PATHS")) or default_seed_paths,
            xfyun_api_key=os.getenv("XFYUN_API_KEY", ""),
            xfyun_api_secret=os.getenv("XFYUN_API_SECRET", ""),
            xfyun_model=os.getenv("XFYUN_MODEL", "generalv3.5"),
            xfyun_endpoint=os.getenv("XFYUN_ENDPOINT", "https://spark-api-open.xf-yun.com/v1/chat/completions"),
            request_timeout_seconds=int(os.getenv("RESOURCE_AGENT_TIMEOUT_SECONDS", "25")),
        )

