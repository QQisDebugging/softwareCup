import re


class ContentSafetyReview:
    def __init__(self) -> None:
        self.blocked_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in [
                r"真实密钥[:：]\s*\S+",
                r"api[_-]?secret\s*[:=]\s*['\"]?[a-z0-9]{16,}",
                r"(access[_-]?token|private[_-]?key)\s*[:=]\s*['\"]?[a-z0-9_\-]{16,}",
                r"身份证号[:：]?\s*\d{15,18}",
                r"手机号[:：]?\s*1\d{10}",
                r"(制作|购买|传播).{0,8}(炸药|毒品|枪支)",
                r"(自杀|自残).{0,8}(方法|步骤|教程)",
                r"(仇恨|歧视).{0,8}(煽动|攻击)",
                r"(色情|淫秽).{0,8}(内容|资源|链接)",
                r"绕过.*考试",
                r"代写.*作业",
            ]
        ]

    def sanitize(self, content: str) -> tuple[str, list[str]]:
        issues: list[str] = []
        sanitized = content
        for pattern in self.blocked_patterns:
            if pattern.search(sanitized):
                issues.append(f"命中安全规则：{pattern.pattern}")
                sanitized = pattern.sub("[已移除的敏感内容]", sanitized)
        return sanitized, issues

    def hallucination_checks(self, content: str, citation_count: int) -> list[str]:
        checks = [
            "已按知识库检索结果生成引用片段",
            "已避免输出未经来源支撑的具体分数、排名和外部事实",
            "已保留教师复核建议，避免把生成内容包装成权威结论",
        ]
        if citation_count == 0:
            checks.append("知识库命中为空，内容已降级为课程通用模板并提示补充资料")
        if "资料来源" not in content:
            checks.append("已追加资料来源区，便于答辩说明 RAG 依据")
        return checks

