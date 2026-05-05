# Resource Agent

Python AI 主程，供 Spring Boot 后端通过 HTTP 调用。当前实现覆盖赛题要求中的多智能体协同、RAG、Embedding、文档解析、个性化资源生成、防幻觉检查和流式输出。

## 能力范围

- `LangGraph` 编排：画像分析 Agent、RAG 检索 Agent、资源规划 Agent、资源生成 Agent、安全审查 Agent。
- `LangChain` 文档对象与切分：课程 JSON、Markdown、TXT、CSV、PDF、DOCX 可解析为知识库片段。
- 本地 Embedding：默认使用确定性哈希向量，离线可跑；后续可替换为云端 Embedding。
- RAG：自动加载 `data/courses/java-web-software-engineering.json` 和 `reference/题目说明.txt`，也支持运行时导入资料。
- 请求级资料：`knowledgeBasePaths` 和 `documentTexts` 会在生成前进入检索，适合把用户上传资料直接用于本次生成。
- 幂等导入：同一文档重复导入会替换旧 chunk，避免向量库越跑越重复。
- 资源生成：一次生成讲解文档、Mermaid 思维导图、练习题、拓展阅读、实操案例、视频/动画脚本。
- 智能辅导：基于 RAG 的课程答疑，输出引用、追问、学习动作和画像信号。
- 自适应测评：生成题库、自动批改、诊断薄弱点，并返回画像更新建议。
- 学习路径规划：基于画像、薄弱点、测评结果和 RAG 资料生成动态学习路线。
- 知识图谱：抽取课程知识点、先修/包含/易错关系，并高亮画像薄弱点。
- 防幻觉审计：检查生成内容的引用覆盖、未支撑断言和风险表达。
- 教师课程诊断：分析课程资料覆盖率、缺失资源类型和测评蓝图。
- 代码实操练习：生成工程实操题，基于静态规则批改代码并返回画像更新建议。
- 多模态分镜：生成 PPT 大纲、视频分镜、旁白和画面提示词。
- 先修诊断：进入新知识点前识别先修缺口，生成入口诊断题、补救动作和画像更新建议。
- 资源策展：把 RAG 证据、候选资源和学生薄弱点重排成可执行资源包，输出覆盖图和学习顺序。
- 学习档案报告：汇总资源完成、测评、答疑、代码练习和复盘证据，生成教师可读成长报告。
- 智能体追踪：记录任务链路步骤、质量门禁、引用证据和降级事件，用于答辩和防黑盒展示。
- 对话式画像抽取：从自然语言对话、学习记录和测评摘要抽取不少于 8 个画像维度。
- 学习事件分析：分析资源使用、答疑、测评、代码练习和复盘行为，输出风险信号和下一步 Agent 调用。
- 测评题目分析：按知识点统计掌握度、高错题和误区聚类，生成教师补救计划。
- 项目级代码审查：审查多文件项目代码，输出风险等级、文件指标、分层缺陷、测试缺口、安全提示、质量门禁和重构任务。
- 班级学习分析：面向教师端输出班级趋势、学生风险画像、掌握度、参与度、干预分组、资源缺口和干预优先级。
- 演示脚本规划：自动生成 7 分钟演示路径、时间轴 Markdown、场景话术、风险预案、备用方案和成功指标。
- 防幻觉与安全：输出资料来源、质量检查、敏感内容过滤和空检索降级提示。
- Provider：默认 `offline`，可通过环境变量切换到 `xfyun_spark`，失败时自动降级。

## 启动

```powershell
cd agents/resource-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

健康检查：

```powershell
curl.exe http://localhost:9001/health
```

## 烟测

```powershell
cd agents/resource-agent
.\.venv\Scripts\Activate.ps1
python scripts/smoke_test.py
python scripts/smoke_tutoring.py
python scripts/smoke_assessment.py
python scripts/smoke_path_planner.py
python scripts/smoke_knowledge_graph.py
python scripts/smoke_content_audit.py
python scripts/smoke_course_diagnosis.py
python scripts/smoke_code_practice.py
python scripts/smoke_storyboard.py
python scripts/smoke_prerequisite.py
python scripts/smoke_resource_curation.py
python scripts/smoke_portfolio_report.py
python scripts/smoke_agent_trace.py
python scripts/smoke_profile_infer.py
python scripts/smoke_learning_event_analysis.py
python scripts/smoke_assessment_item_analysis.py
python scripts/smoke_project_review.py
python scripts/smoke_class_analytics.py
python scripts/smoke_demo_planner.py
python scripts/smoke_competition_enhancements.py
python scripts/smoke_full_ai_agents.py
```

## 接口

后端兼容接口：

- `POST /agents/resource-generation`
- `POST /agents/resource-generation/stream`
- `POST /agents/tutoring`
- `POST /agents/assessment/generate`
- `POST /agents/assessment/grade`
- `POST /agents/path/plan`
- `POST /agents/knowledge/graph`
- `POST /agents/safety/audit`
- `POST /agents/course/diagnose`
- `POST /agents/code/practice/generate`
- `POST /agents/code/practice/grade`
- `POST /agents/multimodal/storyboard`
- `POST /agents/prerequisite/diagnose`
- `POST /agents/resources/curate`
- `POST /agents/report/portfolio`
- `POST /agents/trace/explain`
- `POST /agents/profile/infer`
- `POST /agents/learning/events/analyze`
- `POST /agents/assessment/item-analysis`
- `POST /agents/code/project-review`
- `POST /agents/class/analytics`
- `POST /agents/demo/scenario-plan`
- `POST /agents/evaluation/rag-quality`
- `POST /agents/runs/record`
- `GET /agents/runs/recent`
- `GET /agents/runs/{runId}`
- `POST /agents/review/human-gate`
- `POST /agents/multimodal/voice-package`
- `POST /agents/document/ocr-question`
- `POST /agents/knowledge/graphrag-query`
- `POST /agents/assessment/error-book`
- `POST /agents/course/coverage`
- `POST /agents/demo/defense-pack`

知识库接口：

- `POST /knowledge/ingest`
- `POST /knowledge/search`
- `POST /agents/knowledge/search`

导入资料示例：

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:9001/knowledge/ingest -ContentType 'application/json' -Body (@{
  paths = @('data/courses/java-web-software-engineering.json', 'reference/题目说明.txt')
} | ConvertTo-Json)
```

## 讯飞星火配置

真实密钥只放环境变量，不提交到仓库。

```powershell
$env:RESOURCE_AGENT_PROVIDER='xfyun_spark'
$env:XFYUN_APP_ID='你的 AppID'
$env:XFYUN_API_PASSWORD='你的 APIPassword'
$env:XFYUN_API_KEY='你的 API Key'
$env:XFYUN_API_SECRET='你的 API Secret'
$env:XFYUN_MODEL='generalv3.5'
```

HTTP 调用优先使用 `XFYUN_API_PASSWORD`；如果只拿到旧版 `APIKey/APISecret`，也可以继续配置 `XFYUN_API_KEY` 和 `XFYUN_API_SECRET`。未配置密钥或调用失败时，系统会使用离线模板生成器继续返回结构化学习资源，保证比赛演示链路不中断。`GET /agents/providers/status` 会返回当前凭据模式、模型、fallback 状态和最近错误。

## 国赛增强能力

- RAG 质量评测：`/agents/evaluation/rag-quality` 输出 faithfulness、answerRelevancy、contextPrecision、contextRecall、groundedness 和 citationCoverage。
- Agent 运行记录：`/agents/runs/record` 写入本地 JSONL，`/agents/runs/{runId}` 支持答辩回放。
- 教师人审门禁：`/agents/review/human-gate` 输出 autoApproved、needsTeacherReview、riskReasons、publishChecklist。
- 多模态语音包：`/agents/multimodal/voice-package` 输出旁白分段、SRT 字幕和讯飞 TTS 对接配置。
- OCR 题目解析：`/agents/document/ocr-question` 把 OCR 文本解析为题目、知识点、解题步骤和后续 Agent 调用。
- GraphRAG 查询：`/agents/knowledge/graphrag-query` 输出扩展概念、检索路径、local citations 和 global summary。
- 错题本：`/agents/assessment/error-book` 聚类错题、生成间隔复习计划和画像更新。
- 课程覆盖率：`/agents/course/coverage` 检查章节资源类型、测评题型、缺口和建设计划。
- 答辩包：`/agents/demo/defense-pack` 生成开场稿、评分点矩阵、Q&A、API 清单、开源说明和风险应答。
