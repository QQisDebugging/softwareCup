# Python AI 主程实现说明

## 对应赛题要求

本分支把 `agents/resource-agent` 从 mock 服务升级为 Python AI 主程，负责 LangGraph/LangChain、RAG、Embedding、文档解析和个性化学习资源生成。

- 对话画像输入：沿用 Java 后端传入的 `studentProfileSummary`，作为画像分析 Agent 的输入。
- 多智能体协同：`ResourceGenerationWorkflow` 中串联画像分析、RAG 检索、资源规划、资源生成、安全审查、结果装配。
- 资源生成类型：讲解文档、知识点思维导图、练习题、拓展阅读、实操案例、多模态视频/动画脚本。
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

## 与 Java 后端的兼容性

Java 后端仍调用：

```text
POST http://localhost:9001/agents/resource-generation
```

请求字段和返回字段没有破坏性变化。新增的知识库接口和流式接口只供 Python 服务直接调用，不影响已有 Spring Boot 任务链路。

## 可验证命令

```powershell
cd agents/resource-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/smoke_test.py
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

