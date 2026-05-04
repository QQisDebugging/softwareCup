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
$env:XFYUN_API_KEY='你的 API Key'
$env:XFYUN_API_SECRET='你的 API Secret'
$env:XFYUN_MODEL='generalv3.5'
```

未配置密钥或调用失败时，系统会使用离线模板生成器继续返回结构化学习资源，保证比赛演示链路不中断。
