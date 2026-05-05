import hashlib
import re

from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact
from learning_agent.schemas import (
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    KnowledgeGraphRequest,
    KnowledgeGraphResponse,
    KnowledgeMatch,
)
from learning_agent.vector_store import InMemoryVectorStore


class KnowledgeGraphAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def build(self, request: KnowledgeGraphRequest) -> KnowledgeGraphResponse:
        citations = self.vector_store.search(self._query(request), top_k=max(8, self.settings.retrieval_top_k))
        concepts = self._concepts(request, citations)
        weak_points = set(request.weaknessSignals)
        nodes = [
            KnowledgeGraphNode(
                id=self._node_id(concept),
                label=concept,
                type=self._node_type(index),
                importance=round(max(0.35, 0.95 - index * 0.07), 2),
                evidence=self._evidence(concept, citations),
                weakPoint=concept in weak_points or any(concept in item or item in concept for item in weak_points),
            )
            for index, concept in enumerate(concepts)
        ]
        edges = self._edges(nodes)
        return KnowledgeGraphResponse(
            graphTitle=f"{request.topic} 课程知识图谱",
            courseId=request.courseId,
            topic=request.topic,
            nodes=nodes,
            edges=edges,
            weakPointHighlights=[node.label for node in nodes if node.weakPoint],
            mermaidDiagram=self._mermaid(nodes, edges),
            citations=citations,
            summary=f"已抽取 {len(nodes)} 个知识点和 {len(edges)} 条关系，用于课程结构展示和薄弱点定位。",
        )

    def _query(self, request: KnowledgeGraphRequest) -> str:
        return "\n".join([request.courseTitle, request.topic, " ".join(request.weaknessSignals)])

    def _concepts(self, request: KnowledgeGraphRequest, citations: list[KnowledgeMatch]) -> list[str]:
        candidates: list[str] = [request.topic]
        candidates.extend(request.weaknessSignals)
        text = "\n".join(item.text for item in citations)
        for pattern in [
            r"weeks\.topic:\s*([^\n]+)",
            r"topic:\s*([^\n]+)",
            r"([A-Za-z][A-Za-z0-9 ]{2,40})",
            r"([\u4e00-\u9fa5A-Za-z0-9]{2,18}(?:职责|边界|设计|建模|迁移|测评|图谱|资源|接口|实践))",
        ]:
            for match in re.findall(pattern, text):
                concept = " ".join(str(match).split()).strip("：:;；,.，。")
                if 2 <= len(concept) <= 48:
                    candidates.append(concept)
        defaults = ["先修基础", "核心概念", "常见误区", "实操案例", "自适应测评", "画像更新"]
        candidates.extend(defaults)
        return list(dict.fromkeys(candidates))[:12]

    def _node_type(self, index: int) -> str:
        if index == 0:
            return "root"
        if index <= 3:
            return "core"
        if index <= 7:
            return "support"
        return "assessment"

    def _edges(self, nodes: list[KnowledgeGraphNode]) -> list[KnowledgeGraphEdge]:
        if not nodes:
            return []
        root = nodes[0]
        edges: list[KnowledgeGraphEdge] = []
        for index, node in enumerate(nodes[1:], start=1):
            relation = "先修" if index <= 2 else "包含" if index <= 7 else "评估"
            edges.append(KnowledgeGraphEdge(
                source=root.id if index <= 4 else nodes[index - 1].id,
                target=node.id,
                relation=relation,
                evidence=compact(node.evidence, 80),
            ))
        for left, right in zip(nodes[1:4], nodes[4:7], strict=False):
            edges.append(KnowledgeGraphEdge(
                source=left.id,
                target=right.id,
                relation="易错关联",
                evidence="由薄弱点和课程资料共同推断，供教师复核。",
            ))
        return edges[:16]

    def _evidence(self, concept: str, citations: list[KnowledgeMatch]) -> str:
        for item in citations:
            if concept in item.text or concept.lower() in item.text.lower():
                return compact(item.text, 160)
        if citations:
            return compact(citations[0].text, 160)
        return "当前知识库未命中强相关资料，节点来自主题和默认课程结构。"

    def _mermaid(self, nodes: list[KnowledgeGraphNode], edges: list[KnowledgeGraphEdge]) -> str:
        lines = ["```mermaid", "flowchart TD"]
        for node in nodes:
            label = self._safe(node.label)
            shape = f"(({label}))" if node.type == "root" else f"[{label}]"
            lines.append(f"  {node.id}{shape}")
        for edge in edges:
            lines.append(f"  {edge.source} -- {self._safe(edge.relation)} --> {edge.target}")
        weak_ids = [node.id for node in nodes if node.weakPoint]
        if weak_ids:
            lines.append("  classDef weak fill:#ffe4e6,stroke:#e11d48,color:#111827")
            lines.append(f"  class {','.join(weak_ids)} weak")
        lines.append("```")
        return "\n".join(lines)

    def _node_id(self, label: str) -> str:
        digest = hashlib.sha1(label.encode("utf-8")).hexdigest()[:10]
        return f"n_{digest}"

    def _safe(self, text: str) -> str:
        return text.replace('"', "").replace("[", "(").replace("]", ")")[:48]
