from learning_agent.config import AgentSettings
from learning_agent.resource_templates import compact, mermaid_map
from learning_agent.schemas import (
    AssetPrompt,
    KnowledgeMatch,
    PPTSlide,
    StoryboardRequest,
    StoryboardResponse,
    StoryboardScene,
)
from learning_agent.vector_store import InMemoryVectorStore


class StoryboardAgent:
    def __init__(self, settings: AgentSettings, vector_store: InMemoryVectorStore) -> None:
        self.settings = settings
        self.vector_store = vector_store

    def create(self, request: StoryboardRequest) -> StoryboardResponse:
        citations = self.vector_store.search(self._query(request), top_k=self.settings.retrieval_top_k)
        evidence = compact(citations[0].text, 160) if citations else "当前知识库未命中强相关资料，需教师补充资料。"
        slides = self._slides(request, evidence)
        scenes = self._scenes(request, evidence)
        return StoryboardResponse(
            title=f"{request.topic} 多模态微课脚本",
            pptOutline=slides,
            videoStoryboard=scenes,
            narrationScript=self._narration(request, evidence),
            assetPrompts=self._asset_prompts(request),
            interactionQuestions=[
                f"`{request.topic}` 最容易混淆的概念是什么？",
                "请指出一个真实项目中违反分层职责的例子。",
                "完成学习后，你希望系统下一步推送哪类资源？",
            ],
            citations=citations,
            summary=f"已生成 {len(slides)} 页 PPT 大纲和 {len(scenes)} 个视频分镜，时长约 {request.targetDurationMinutes} 分钟。",
        )

    def _query(self, request: StoryboardRequest) -> str:
        return "\n".join([request.courseTitle, request.topic, request.modality, request.studentProfileSummary])

    def _slides(self, request: StoryboardRequest, evidence: str) -> list[PPTSlide]:
        return [
            PPTSlide(
                slideNo=1,
                title=f"{request.topic} 学习目标",
                bullets=["定位学习痛点", "明确项目场景", "说明本节交付物"],
                visualHint="左侧学生画像，右侧课程任务卡片。",
                speakerNote=f"开场引用资料依据：{evidence}",
            ),
            PPTSlide(
                slideNo=2,
                title="核心概念图解",
                bullets=["先修基础", "核心流程", "常见误区"],
                visualHint=mermaid_map(request.topic),
                speakerNote="用图解释概念边界，避免只背定义。",
            ),
            PPTSlide(
                slideNo=3,
                title="项目案例拆解",
                bullets=["输入输出", "关键步骤", "代码/伪代码片段"],
                visualHint="三栏布局：Controller、Service、Repository。",
                speakerNote="把抽象知识落到工程职责。",
            ),
            PPTSlide(
                slideNo=4,
                title="练习与画像更新",
                bullets=["完成自测题", "提交实操结果", "根据反馈更新画像"],
                visualHint="闭环箭头：学习 -> 练习 -> 批改 -> 画像 -> 路径重排。",
                speakerNote="强调系统不是一次性生成，而是持续优化。",
            ),
        ]

    def _scenes(self, request: StoryboardRequest, evidence: str) -> list[StoryboardScene]:
        base = max(20, round(request.targetDurationMinutes * 60 / 4))
        return [
            StoryboardScene(
                sceneNo=1,
                durationSeconds=base,
                visual="学生提出具体困惑，屏幕展示画像薄弱点。",
                narration=f"今天解决 `{request.topic}` 的核心困惑。",
                interaction="让学生选择最不懂的概念。",
            ),
            StoryboardScene(
                sceneNo=2,
                durationSeconds=base,
                visual="动画拆解概念图和调用链。",
                narration=f"资料依据：{evidence}",
                interaction="暂停提问：这一步属于哪一层？",
            ),
            StoryboardScene(
                sceneNo=3,
                durationSeconds=base,
                visual="展示最小项目案例和错误写法。",
                narration="对比错误写法和改造方案。",
                interaction="让学生指出代码问题。",
            ),
            StoryboardScene(
                sceneNo=4,
                durationSeconds=base,
                visual="展示测评、批改、画像更新和下一步路径。",
                narration="完成闭环，系统会重排下一轮资源。",
                interaction="让学生选择下一类资源。",
            ),
        ]

    def _narration(self, request: StoryboardRequest, evidence: str) -> str:
        return f"""本节微课围绕 `{request.topic}` 展开。首先根据学生画像定位薄弱点，再用课程资料解释核心概念。
关键依据是：{evidence}
随后通过一个最小项目案例展示正确做法和常见错误，最后用自适应测评完成反馈，推动画像和学习路径更新。"""

    def _asset_prompts(self, request: StoryboardRequest) -> list[AssetPrompt]:
        return [
            AssetPrompt(
                assetType="PPT封面图",
                prompt=f"高校软件工程课堂，主题是 {request.topic}，清晰、现代、学习场景",
                usage="第一页背景或封面插图",
            ),
            AssetPrompt(
                assetType="流程图",
                prompt=f"{request.topic} 的工程调用链图，强调职责边界和反馈闭环",
                usage="核心概念图解页",
            ),
            AssetPrompt(
                assetType="短视频画面",
                prompt="学生通过智能体完成学习、练习、测评、画像更新的界面录屏脚本",
                usage="演示视频分镜",
            ),
        ]
