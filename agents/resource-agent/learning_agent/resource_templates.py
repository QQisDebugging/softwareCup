from learning_agent.schemas import KnowledgeMatch, ResourceAgentRequest


def infer_target_level(profile_summary: str) -> str:
    text = (profile_summary or "").lower()
    if any(keyword in text for keyword in ["基础弱", "较弱", "零基础", "不熟", "weak", "beginner", "unfamiliar"]):
        return "基础补强型"
    if any(keyword in text for keyword in ["项目", "实践", "案例", "project", "practice", "case"]):
        return "实践进阶型"
    if any(keyword in text for keyword in ["考研", "竞赛", "高阶", "competition", "advanced"]):
        return "高阶拓展型"
    return "根据学习画像自适应"


def estimate_minutes(resource_type: str, modality: str, resource_count: int) -> int:
    base = 16 + resource_count * 4
    if "视频" in modality or "动画" in modality:
        base += 6
    if "实操" in resource_type or "项目" in resource_type:
        base += 8
    if "PPT" in resource_type or "课件" in resource_type:
        base += 4
    return min(max(base, 15), 90)


def build_query(request: ResourceAgentRequest) -> str:
    return "\n".join(
        [
            request.courseTitle,
            request.topic,
            request.resourceType,
            request.modality,
            request.prompt,
            request.studentProfileSummary,
        ]
    )


def citations_markdown(matches: list[KnowledgeMatch]) -> str:
    if not matches:
        return "- 暂无命中资料，建议先通过 `/knowledge/ingest` 导入课程讲义、教材或项目文档。"
    lines = []
    seen: set[str] = set()
    for index, match in enumerate(matches, start=1):
        key = f"{match.source}:{match.title}"
        if key in seen:
            continue
        seen.add(key)
        snippet = compact(match.text, 110)
        lines.append(f"- [{index}] {match.title}，来源 `{match.source}`，相关度 {match.score}：{snippet}")
    return "\n".join(lines)


def compact(text: str, limit: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "..."


def preserve_text(text: str, limit: int) -> str:
    """按长度截断，但保留模型输出的换行与 Markdown 结构（标题、列表、代码块）。

    compact() 会把所有空白折叠成单行，适合做短摘要；模型主回答必须用本函数，
    否则 Markdown 结构会被压扁，前端无法正确渲染。
    """
    normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    # 合并 3 个以上连续空行，避免过度留白
    while "\n\n\n" in normalized:
        normalized = normalized.replace("\n\n\n", "\n\n")
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "..."


def limit_text(text: str, limit: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    if limit <= 3:
        return normalized[:limit]
    return normalized[: limit - 3].rstrip() + "..."


def mermaid_map(topic: str) -> str:
    safe_topic = topic.replace('"', "")
    return f"""```mermaid
mindmap
  root(({safe_topic}))
    先修基础
      术语理解
      场景识别
    核心概念
      定义
      工作流程
      常见误区
    实操应用
      最小案例
      调试检查
      结果复盘
    评估反馈
      自测题
      错因分析
      下一步资源
```"""


def exercise_block(topic: str, target_level: str) -> str:
    return f"""1. 选择题：以下哪一项最能体现 `{topic}` 在真实项目中的作用？请说明理由。
2. 判断题：只要代码能运行，就说明 `{topic}` 的工程设计是合理的。请判断并解释。
3. 简答题：结合自己的课程项目，用 120 字说明 `{topic}` 的输入、处理过程和输出。
4. 纠错题：给出一个违反 `{topic}` 原则的伪代码片段，并写出修改方案。
5. 实践题：完成一个 30 分钟小任务，提交运行截图、关键代码和复盘说明。

难度定位：{target_level}，题目按“概念识别 -> 场景迁移 -> 实操验证”递进。"""


def project_case(topic: str, course_title: str) -> str:
    return f"""**案例名称：** 面向 `{course_title}` 的 `{topic}` 小型实训

**任务背景：** 学生需要把课堂概念落到一个可运行的小功能中。

**交付物：**
- 一份 1 页设计说明，写清目标、输入输出和关键约束。
- 一个最小可运行 demo 或伪代码流程。
- 一份自测记录，说明成功场景、失败场景和下一步改进。

**验收标准：**
- 能解释每个关键步骤为什么存在。
- 能指出至少 2 个常见错误并给出修正方式。
- 能把结果和个人学习画像中的薄弱点对应起来。"""


def video_script(topic: str, modality: str) -> str:
    if "视频" not in modality and "动画" not in modality:
        return "当前任务未要求视频/动画；可将图解脚本作为后续多模态生成输入。"
    return f"""**镜头 1（15 秒）**：用问题场景引入 `{topic}`，展示学生常见困惑。

**镜头 2（40 秒）**：动画拆解核心流程，左侧显示先修知识，右侧显示项目中的实际位置。

**镜头 3（45 秒）**：演示一个小案例，标注关键代码/步骤和易错点。

**镜头 4（20 秒）**：给出自测题和下一步学习资源，提醒学生提交反馈以更新画像。"""


def ppt_outline(topic: str, course_title: str, target_level: str) -> str:
    return f"""| 页码 | 页面主题 | 讲解要点 | 互动设计 | 素材提示 |
| --- | --- | --- | --- | --- |
| 1 | `{topic}` 学习目标 | 对齐 `{course_title}` 的课程任务，说明本节要解决的核心问题 | 让学生用一句话描述当前困惑 | 课程场景图、问题气泡 |
| 2 | 先修基础检查 | 列出 3 个必须掌握的术语和常见断点 | 1 分钟自测，标记不熟悉的术语 | 术语卡片、流程入口 |
| 3 | 核心流程拆解 | 按输入、处理、输出解释关键流程，适配 `{target_level}` 学习层级 | 让学生补全流程中的缺失步骤 | 分层结构图、箭头流程 |
| 4 | 易错点对比 | 对比正确做法与常见误区，突出判断依据 | 现场判断 2 个伪代码片段 | 红绿对照、代码片段 |
| 5 | 实操任务说明 | 明确任务背景、交付物、验收标准和复盘问题 | 学生选择自己的实践切入点 | 项目看板、验收清单 |
| 6 | 复盘与画像更新 | 汇总错题、耗时、反馈和下一步资源推送 | 提交学习反馈用于动态画像更新 | 雷达图、学习路径节点 |"""
