# Python AI 主程实现说明

## 对应赛题要求

本分支把 `agents/resource-agent` 从 mock 服务升级为 Python AI 主程，负责 LangGraph/LangChain、RAG、Embedding、文档解析和个性化学习资源生成。

- 对话画像输入：沿用 Java 后端传入的 `studentProfileSummary`，作为画像分析 Agent 的输入。
- 多智能体协同：`ResourceGenerationWorkflow` 中串联画像分析、RAG 检索、资源规划、资源生成、安全审查、结果装配。
- 资源生成类型：讲解文档、知识点思维导图、练习题、拓展阅读、实操案例、多模态视频/动画脚本。
- 智能辅导：`TutoringAgent` 提供 RAG 课程答疑，输出引用依据、追问问题、学习动作和画像更新信号。
- 自适应测评：`AssessmentAgent` 生成选择、判断、简答、代码纠错题，批改后输出薄弱点和画像更新建议。
- 学习路径规划：`PathPlannerAgent` 根据画像、薄弱点、最近得分和 RAG 资料生成动态学习路线。
- 知识图谱：`KnowledgeGraphAgent` 从课程资料中抽取知识点、关系和薄弱点高亮。
- 防幻觉审计：`ContentAuditAgent` 检查引用覆盖、未支撑断言、风险表达和修订建议。
- 教师诊断：`CourseDiagnosisAgent` 诊断课程覆盖率、缺失资源和测评蓝图。
- 代码实操：`CodePracticeAgent` 生成代码纠错/分层改造题，并进行静态规则批改。
- 多模态脚本：`StoryboardAgent` 生成 PPT 大纲、视频分镜、旁白和素材提示词。
- 先修诊断：`PrerequisiteDiagnosisAgent` 在新课开始前输出准备度、先修缺口、入口诊断题和补救资源动作。
- 资源策展：`ResourceCurationAgent` 将课程资料、候选资源、薄弱点和时间预算重排为个性化资源包。
- 学习档案：`PortfolioReportAgent` 汇总资源、测评、答疑、代码练习和复盘证据，形成教师可读报告。
- 链路追踪：`AgentTraceAgent` 输出智能体步骤、质量门禁、引用编号、降级事件和复现说明，不暴露模型隐藏推理。
- 画像抽取：`ProfileInferenceAgent` 从自然语言对话、学习记录和测评摘要抽取知识基础、认知风格、学习目标等 8 个画像维度。
- 学习分析：`LearningEventAnalysisAgent` 分析学习事件、资源使用、答疑、测评和实操记录，给出风险信号和下一步 Agent 调用。
- 题目分析：`AssessmentItemAnalysisAgent` 汇总测评作答，输出知识点掌握度、高错题、误区聚类和补救计划。
- 项目审查：`ProjectReviewAgent` 审查多文件项目代码，输出文件指标、风险等级、分层缺陷、测试缺口、安全提示、质量门禁和重构任务。
- 班级分析：`ClassAnalyticsAgent` 汇总学生快照，输出班级趋势、学生风险画像、班级掌握度、参与度、干预分组和资源缺口。
- 演示规划：`DemoScenarioPlannerAgent` 根据时间限制和可用端点生成演示时间轴、场景话术、风险预案、备用方案和成功指标。
- 国赛增强：`competition_enhancements.py` 增加 RAG 质量评测、Agent run 回放、人审门禁、讯飞 TTS 语音包、OCR 题目解析、GraphRAG 查询、错题本、课程覆盖率和答辩材料包。
- 个性化路径：生成结果中包含按画像层级调整的学习步骤、资源推送建议和画像更新建议。
- 防幻觉：输出 RAG 资料来源、质量检查和空检索降级提示。
- 响应体验：保留普通 JSON 接口，并新增 Markdown 流式接口。

## 技术结构

- `main.py`：FastAPI 入口，保留 `/agents/resource-generation` Java 兼容契约。
- `learning_agent/graph.py`：LangGraph 工作流；依赖缺失时自动退化为顺序执行。
- `learning_agent/documents.py`：文档解析与 LangChain 文档切分，支持 JSON/TXT/MD/CSV/PDF/DOCX。
- `learning_agent/embeddings.py`：本地哈希 Embedding，保证无密钥也能做 RAG 演示。
- `learning_agent/vector_store.py`：内存向量库与相似度检索。
- `learning_agent/llm.py`：Provider 路由，默认离线生成，可选讯飞星火。
- `learning_agent/safety.py`：内容安全和防幻觉检查。
- `learning_agent/tutoring.py`：智能辅导 Agent，支撑学生即时问答和画像信号识别。
- `learning_agent/assessment.py`：测评生成与自动批改 Agent，支撑学习效果评估闭环。
- `learning_agent/path_planner.py`：学习路径规划 Agent，支撑资源推荐和复习节点安排。
- `learning_agent/knowledge_graph.py`：课程知识图谱 Agent，支撑 Mermaid 图谱和薄弱点高亮。
- `learning_agent/content_audit.py`：内容审计 Agent，支撑防幻觉和内容安全复核。
- `learning_agent/course_diagnosis.py`：教师课程诊断 Agent，支撑课程建设建议。
- `learning_agent/code_practice.py`：代码实操 Agent，支撑代码练习生成与静态批改。
- `learning_agent/storyboard.py`：多模态分镜 Agent，支撑 PPT 和视频脚本生成。
- `learning_agent/prerequisite.py`：先修诊断 Agent，支撑入口诊断和补救学习闭环。
- `learning_agent/resource_curation.py`：资源策展 Agent，支撑资源包重排、覆盖图和学习顺序。
- `learning_agent/portfolio_report.py`：学习档案 Agent，支撑过程证据、风险提示和教师评语草稿。
- `learning_agent/agent_trace.py`：智能体追踪 Agent，支撑演示审计、质量门禁和降级可见性。
- `learning_agent/profile_infer.py`：对话式画像抽取 Agent，支撑画像自主构建和随学更新。
- `learning_agent/learning_event_analysis.py`：学习事件分析 Agent，支撑参与度、趋势、风险和下一步动作分析。
- `learning_agent/assessment_item_analysis.py`：测评题目分析 Agent，支撑教师视角的知识点诊断和误区聚类。
- `learning_agent/project_review.py`：项目级代码审查 Agent，支撑 AI 辅助编程和工程实践反馈。
- `learning_agent/class_analytics.py`：班级学习分析 Agent，支撑教师端学情看板和分层干预。
- `learning_agent/demo_planner.py`：演示规划 Agent，支撑答辩脚本、录屏顺序和风险预案。
- `learning_agent/competition_enhancements.py`：国赛增强 Agent 集合，支撑 RAG 评测、run 持久化、人审、语音包、OCR、GraphRAG、错题本、课程覆盖和答辩包。

## 稳定性优化

- 默认知识库和运行时知识库导入都是幂等的，同一文档再次导入会替换旧 chunk。
- `knowledgeBasePaths` 和 `documentTexts` 会在资源生成前临时进入 RAG 检索，支持把上传资料用于单次任务。
- FastAPI 使用 lifespan 加载默认知识库，避免 startup 弃用告警。
- 后端异步生成任务调整为事务提交后启动，避免异步线程提前读取未提交任务。
- Python 返回的 `title/resourceType/modality/targetLevel` 会按 Java 落库字段长度裁剪，降低大模型长标题导致任务失败的风险。
- `llm.py` 同时支持讯飞 `XFYUN_API_PASSWORD` 和 `XFYUN_API_KEY/XFYUN_API_SECRET` 两种凭据模式，`/agents/providers/status` 会返回当前凭据模式、fallback 状态和最近错误。
- Agent run 记录写入 `agents/resource-agent/data/agent_runs.jsonl`，该目录被 `.gitignore` 排除，适合演示回放但不会污染仓库。

## 与 Java 后端的兼容性

Java 后端仍调用：

```text
POST http://localhost:9001/agents/resource-generation
```

请求字段和返回字段没有破坏性变化。新增的知识库接口和流式接口只供 Python 服务直接调用，不影响已有 Spring Boot 任务链路。

新增后端学习闭环接口会调用 Python 主程的辅导和测评端点，并把学习过程写入数据库：

- `POST /api/learning/tutoring`：调用 `/agents/tutoring`，保存答疑会话、RAG 引用、学习动作和画像信号。
- `POST /api/learning/assessments/generate`：调用 `/agents/assessment/generate`，生成自适应测评并写入学习事件。
- `POST /api/learning/assessments/grade`：调用 `/agents/assessment/grade`，保存测评尝试，并把 `profileDimensionUpdates` 自动写回学生画像。
- `GET /api/learning/events`、`GET /api/learning/tutoring`、`GET /api/learning/attempts`：查询学生学习事件、答疑历史和测评历史。

## 可验证命令

```powershell
cd agents/resource-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
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
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```
