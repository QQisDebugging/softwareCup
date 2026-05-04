# Python AI 主程实现说明

## 对应赛题要求

本分支把 `agents/resource-agent` 从 mock 服务升级为 Python AI 主程，负责 LangGraph/LangChain、RAG、Embedding、文档解析和个性化学习资源生成。

- 对话画像输入：沿用 Java 后端传入的 `studentProfileSummary`，作为画像分析 Agent 的输入。
- 多智能体协同：`ResourceGenerationWorkflow` 中串联画像分析、RAG 检索、资源规划、资源生成、安全审查、结果装配。
- 资源生成类型：讲解文档、知识点思维导图、练习题、拓展阅读、实操案例、多模态视频/动画脚本。
- 智能辅导：`TutoringAgent` 提供 RAG 课程答疑，输出引用依据、追问问题、学习动作和画像更新信号。
- 自适应测评：`AssessmentAgent` 生成选择、判断、简答、代码纠错题，批改后输出薄弱点和画像更新建议。
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

## 稳定性优化

- 默认知识库和运行时知识库导入都是幂等的，同一文档再次导入会替换旧 chunk。
- `knowledgeBasePaths` 和 `documentTexts` 会在资源生成前临时进入 RAG 检索，支持把上传资料用于单次任务。
- FastAPI 使用 lifespan 加载默认知识库，避免 startup 弃用告警。
- 后端异步生成任务调整为事务提交后启动，避免异步线程提前读取未提交任务。
- Python 返回的 `title/resourceType/modality/targetLevel` 会按 Java 落库字段长度裁剪，降低大模型长标题导致任务失败的风险。

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
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```
