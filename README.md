# 基于大模型的个性化资源生成与学习多智能体系统

软件杯项目仓库。当前后端主线聚焦 Spring Boot、数据库、接口、文件上传、任务管理和 Python 智能体调用。

## 当前结构

- `backend/`：Spring Boot 后端，默认 H2 本地库，可切换 PostgreSQL。
- `agents/resource-agent/`：Python FastAPI AI 主程，包含 LangGraph/LangChain、RAG、Embedding、文档解析和多智能体资源生成。
- `data/courses/`：至少一门完整高校课程的自构造测试数据。
- `docs/`：比赛文档、后端接口说明和协作说明。

## 本地启动

启动 Python 资源生成智能体：

```powershell
cd agents/resource-agent
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

启动后端：

```powershell
cd backend
.\\mvnw.cmd spring-boot:run
```

健康检查：

```powershell
curl.exe http://localhost:8080/api/health
curl.exe http://localhost:9001/health
```

如需 PostgreSQL：

```powershell
docker compose up -d postgres
cd backend
.\\mvnw.cmd spring-boot:run -Dspring-boot.run.profiles=postgres
```

## 后端第一阶段 API

- `GET /api/health`
- `POST /api/profiles/dialogue`
- `GET /api/profiles`
- `GET /api/profiles/{profileId}/detail`
- `GET /api/profiles/{profileId}/dimensions`
- `PUT /api/profiles/{profileId}/dimensions`
- `GET /api/profiles/{profileId}/history`
- `POST /api/courses`
- `GET /api/courses`
- `GET /api/courses/{courseId}/resources`
- `POST /api/tasks/resource-generation`
- `GET /api/tasks`
- `POST /api/uploads`

## Python AI 主程

`agents/resource-agent` 已保留 Spring Boot 调用契约，并实现离线可运行的 RAG 资源生成链路。运行时可通过 `knowledgeBasePaths` / `documentTexts` 把上传资料纳入单次生成。详见 `docs/AI_AGENT_IMPLEMENTATION.md`。

## 讯飞工具接入说明

比赛要求选用科大讯飞相关工具。当前 Python 主程支持通过 `RESOURCE_AGENT_PROVIDER=xfyun_spark` 接入讯飞星火；未配置密钥或调用失败时会自动降级到本地生成器，保证演示链路不中断。真实密钥通过本地 `.env` 或系统环境变量注入，不提交到仓库。
