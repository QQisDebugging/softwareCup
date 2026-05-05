import re

from learning_agent.config import AgentSettings
from learning_agent.embeddings import HashingEmbeddingModel
from learning_agent.resource_templates import compact
from learning_agent.safety import ContentSafetyReview
from learning_agent.schemas import (
    ContentAuditRequest,
    ContentAuditResponse,
    KnowledgeMatch,
    RiskyClaim,
    UnsupportedClaim,
)
from learning_agent.vector_store import InMemoryVectorStore


class ContentAuditAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store
        self.embedding_model = HashingEmbeddingModel(settings.embedding_dimensions)
        self.safety = ContentSafetyReview()

    def audit(self, request: ContentAuditRequest) -> ContentAuditResponse:
        citations = request.citations or self.vector_store.search(
            query=self._query(request),
            top_k=self.settings.retrieval_top_k,
        )
        claims = self._claims(request.content)
        unsupported = self._unsupported_claims(claims, citations)
        risky = self._risky_claims(request.content)
        coverage = 1.0 if not claims else max(0.0, (len(claims) - len(unsupported)) / len(claims))
        score = max(0, min(100, round(100 * coverage - len(risky) * 12)))
        revised_content = self._revise(request.content, unsupported, risky)
        return ContentAuditResponse(
            overallScore=score,
            citationCoverage=round(coverage, 2),
            unsupportedClaims=unsupported,
            riskyClaims=risky,
            revisedContent=revised_content,
            recommendations=self._recommendations(unsupported, risky, citations),
            citations=citations,
            summary=f"审计完成：可信度 {score}/100，引用覆盖率 {coverage:.0%}，未支撑断言 {len(unsupported)} 条，风险内容 {len(risky)} 条。",
        )

    def _query(self, request: ContentAuditRequest) -> str:
        return "\n".join([request.courseTitle, request.topic, compact(request.content, 1200)])

    def _claims(self, content: str) -> list[str]:
        pieces = re.split(r"[\n。！？!?；;]+", content)
        claims = []
        for piece in pieces:
            normalized = " ".join(piece.split())
            if len(normalized) >= 14:
                claims.append(normalized)
        return claims[:20]

    def _unsupported_claims(self, claims: list[str], citations: list[KnowledgeMatch]) -> list[UnsupportedClaim]:
        if not claims:
            return []
        evidence_text = "\n".join(item.text for item in citations)
        evidence_tokens = set(self.embedding_model.tokens(evidence_text))
        unsupported: list[UnsupportedClaim] = []
        for claim in claims:
            claim_tokens = set(self.embedding_model.tokens(claim))
            overlap = len(claim_tokens & evidence_tokens)
            ratio = overlap / max(4, len(claim_tokens))
            if not citations or ratio < 0.18:
                unsupported.append(UnsupportedClaim(
                    claim=compact(claim, 180),
                    reason="当前 RAG 证据中缺少足够词汇重合或明确依据。",
                    suggestedEvidenceQuery=compact(claim, 80),
                ))
        return unsupported[:8]

    def _risky_claims(self, content: str) -> list[RiskyClaim]:
        _, issues = self.safety.sanitize(content)
        risky = [
            RiskyClaim(
                claim=issue,
                riskType="content_safety",
                mitigation="移除敏感表达或改为教师可复核的学习建议。",
            )
            for issue in issues
        ]
        seen = {f"content_safety:{item.claim}" for item in risky}
        seen_risk_types = {item.riskType for item in risky}
        for pattern, risk_type in [
            (r"100%|百分之百|绝对不会|保证", "overclaim"),
            (r"全国第一|最高水平|权威结论|唯一答案", "unverified_authority"),
            (r"真实密钥|api[_-]?secret|token", "secret_leak"),
        ]:
            if risk_type in seen_risk_types:
                continue
            for match in re.finditer(pattern, content, flags=re.IGNORECASE):
                claim = compact(content[max(0, match.start() - 40): match.end() + 60], 140)
                key = f"{risk_type}:{claim}"
                if key in seen:
                    continue
                seen.add(key)
                seen_risk_types.add(risk_type)
                risky.append(RiskyClaim(
                    claim=claim,
                    riskType=risk_type,
                    mitigation="改为带条件、带引用、可复核的表述。",
                ))
                break
        return risky[:8]

    def _revise(
        self,
        content: str,
        unsupported: list[UnsupportedClaim],
        risky: list[RiskyClaim],
    ) -> str:
        revised, _ = self.safety.sanitize(content)
        replacements = [
            (r"保证学生\s*100%\s*掌握所有知识点", "在当前资料支持下，可帮助学生逐步掌握相关知识点"),
            (r"全国第一的权威结论", "需要引用支撑的结论"),
            (r"100%|百分之百|绝对不会|保证", "在当前资料支持下"),
            (r"全国第一|最高水平|权威结论|唯一答案", "需复核结论"),
        ]
        for pattern, replacement in replacements:
            revised = re.sub(pattern, replacement, revised, flags=re.IGNORECASE)
        if unsupported:
            revised += "\n\n## 需要补充依据\n"
            revised += "\n".join(f"- {item.claim}" for item in unsupported[:5])
        if risky:
            revised += "\n\n## 风险修订提示\n"
            revised += "\n".join(f"- {item.riskType}: {item.mitigation}" for item in risky[:5])
        return revised

    def _recommendations(
        self,
        unsupported: list[UnsupportedClaim],
        risky: list[RiskyClaim],
        citations: list[KnowledgeMatch],
    ) -> list[str]:
        recommendations = []
        if not citations:
            recommendations.append("先上传课程讲义、实验文档或教材片段，再生成最终内容。")
        if unsupported:
            recommendations.append("对未支撑断言执行二次 RAG 检索，补充引用或删除该断言。")
        if risky:
            recommendations.append("把绝对化、权威化或敏感表达改成可验证、可复核表述。")
        recommendations.append("最终展示时保留引用来源、相关度和教师复核提示。")
        return recommendations
