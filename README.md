# 基于大模型的个性化资源生成与学习多智能体系统

软件杯项目仓库。当前后端主线聚焦 Spring Boot、数据库、接口、文件上传、任务管理、学习闭环和 Python 智能体调用。

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
- `POST /api/learning/tutoring`
- `POST /api/learning/assessments/generate`
- `POST /api/learning/assessments/grade`
- `GET /api/learning/events?studentProfileId=...`
- `GET /api/learning/tutoring?studentProfileId=...`
- `GET /api/learning/attempts?studentProfileId=...`

## Python AI 主程

`agents/resource-agent` 已保留 Spring Boot 调用契约，并实现离线可运行的 RAG 资源生成链路。运行时可通过 `knowledgeBasePaths` / `documentTexts` 把上传资料纳入单次生成。详见 `docs/AI_AGENT_IMPLEMENTATION.md`。

Python 智能体新增学习路径、知识图谱、防幻觉审计、教师诊断、代码实操和多模态分镜能力。Java 后端和 Vue3 前端对接任务见 `docs/JAVA_VUE3_INTEGRATION_GUIDE.md`。

## 讯飞工具接入说明

比赛要求选用科大讯飞相关工具。当前 Python 主程支持通过 `SOFTWARECUP_AGENT_PROVIDER=xfyun_spark` 接入讯飞星火；正式展示和评测应配置真实讯飞密钥运行。真实密钥通过本地 `.env` 或系统环境变量注入，不提交到仓库。申请、配置和验证步骤见 `docs/XFYUN_SPARK_SETUP.md`。
## 多智能体与学习闭环接口

当前后端已经把资源生成从单个 `resource-agent` 升级为可观测的多智能体任务链。一次资源生成任务会依次记录：画像分析、知识诊断、路径规划、文档生成、题库生成、思维导图生成、实操案例生成、PPT 课件生成和安全审核。

`POST /api/profiles/dialogue` 会优先调用 Python `ProfileInferenceAgent` 抽取 8 个画像维度，并把本次画像智能体产物写入 `agent_artifacts`；Python 服务不可用时自动降级为后端规则画像，保证演示链路不断。

资源生成完成后会强制调用 `ContentAuditAgent` 做引用覆盖、事实性断言、敏感违规表达和人工复核门禁检查。审核结果写入 `generation_audits`，风险或证据不足时会把 `revisedContent` 写回资源正文，并产生 `HUMAN_REVIEW_GATE` 记录。

新增接口：

- `GET /api/agents`
- `GET /api/resource-types`
- `GET /api/tasks/{taskId}/steps`
- `GET /api/tasks/{taskId}/events`
- `GET /api/tasks/{taskId}/model-invocations`
- `GET /api/tasks/{taskId}/audits`
- `GET /api/agent-artifacts?studentProfileId=...`
- `GET /api/learning/paths?studentProfileId=...`
- `GET /api/learning/recommendations?studentProfileId=...`
- `POST /api/learning/events`
- `POST /api/learning/quiz-attempts`
- `GET /api/learning/mastery?studentProfileId=...&courseId=...`
- `GET /api/learning/evaluation-reports?studentProfileId=...&courseId=...`
- `GET /api/demo/readiness-report?studentProfileId=...&courseId=...&taskId=...`

固定资源类型覆盖 7 类：课程讲解文档、知识点思维导图、练习题/测验、拓展阅读、实操案例、视频讲解脚本/动画脚本、PPT课件/课堂讲稿。

`/api/demo/readiness-report` 是初赛评委模式接口，会把赛题基本功能、可选加分项和非功能要求映射成量化指标、达成状态、证据接口和推荐演示顺序。前端可把它做成答辩看板，PPT/视频中也可以截图展示“8 维画像、9 个智能体、7 类资源、防幻觉审核、学习闭环”这些能力的真实数据证据。
