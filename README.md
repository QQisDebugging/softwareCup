# 基于大模型的个性化资源生成与学习多智能体系统

软件杯项目仓库。当前后端主线聚焦 Spring Boot、数据库、接口、文件上传、任务管理和 Python 智能体调用。

## 当前结构

- `backend/`：Spring Boot 后端，默认 H2 本地库，可切换 PostgreSQL。
- `agents/resource-agent/`：Python FastAPI 资源生成智能体，先用 mock 跑通链路。
- `data/courses/`：至少一门完整高校课程的自构造测试数据。
- `docs/`：比赛文档、AI Coding 使用说明和后端接口说明。

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
- `POST /api/courses`
- `GET /api/courses`
- `GET /api/courses/{courseId}/resources`
- `POST /api/tasks/resource-generation`
- `GET /api/tasks`
- `POST /api/uploads`

## 讯飞工具接入说明

比赛要求选用科大讯飞相关工具。当前仓库先保留 `agents/resource-agent` 的统一 HTTP 契约，后续把 mock 生成器替换为讯飞星火大模型调用即可，不需要改 Spring Boot 任务管理链路。真实密钥通过本地 `.env` 或系统环境变量注入，不提交到仓库。
