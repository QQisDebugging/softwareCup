# SoftwareCup Frontend

Vue3 + Vite + TypeScript 前端主程，用于比赛现场展示“个性化学习资源生成系统”的页面、接口对接、AI 结果展示、下载能力和可视化证据。

## 技术栈

- Vue3 + TypeScript + Vite
- Vue Router + Pinia
- Axios API 封装
- ECharts 可视化
- Markdown 渲染与 JSON 展示

## 环境变量

`frontend/.env.development`：

```text
VITE_API_BASE_URL=http://localhost:8080/api
```

前端主链路只调用 Java Spring Boot 后端。Python Agent 由 Java 后端代理调用，前端仅在“演示准备清单”中检测 `http://localhost:9001/health`。

## 完整启动顺序

建议打开 3 个 PowerShell 终端，并按下面顺序启动。

1. 启动 Python Agent：

```powershell
cd D:\competiton\software\softwareCup\agents\resource-agent
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

健康检查：

```text
http://localhost:9001/health
```

2. 启动 Spring Boot 后端：

```powershell
cd D:\competiton\software\softwareCup\backend
.\mvnw.cmd spring-boot:run
```

健康检查：

```text
http://localhost:8080/api/health
```

3. 启动 Vue3 前端：

```powershell
cd D:\competiton\software\softwareCup\frontend
npm.cmd install
npm.cmd run dev -- --port 5173
```

访问地址：

```text
http://127.0.0.1:5173/
```

## 验收命令

```powershell
cd D:\competiton\software\softwareCup\frontend
npm.cmd run typecheck
npm.cmd run build
```

如果 `5173` 端口被占用，可以改用：

```powershell
npm.cmd run dev -- --port 5174
```

## 页面功能

- 演示总览：后端状态、核心指标、任务概览、演示准备清单、三端启动命令复制。
- 学生画像：对话式画像创建、画像维度、历史记录、雷达图、JSON/Markdown 下载。
- 课程资源：课程列表、课程创建、课程资源查看、资源 Markdown 预览与下载。
- 资源生成：选择画像、课程、资源类型，创建异步生成任务并跳转任务详情。
- 任务详情：任务状态、进度、步骤时间线、SSE 事件、模型调用、防幻觉审核、结果下载。
- 学习闭环：智能答疑、测评生成、自动批改、学习记录、趋势图、学习报告下载。
- 智能体工具箱：后端代理接口调试台，支持示例 JSON、格式化、校验、响应展示和下载。
- 教师分析：课程诊断、班级学情、风险学生、干预分组、资源缺口和教师报告导出。
- 评委模式：赛题完成度、证据端点、推荐演示流、答辩材料 JSON/Markdown/HTML 导出。

## 已对接接口

- `GET /api/health`
- `GET /api/agents`
- `GET /api/agent-artifacts`
- `GET /api/profiles`
- `POST /api/profiles/dialogue`
- `GET /api/profiles/{profileId}`
- `GET /api/profiles/{profileId}/detail`
- `GET /api/profiles/{profileId}/dimensions`
- `GET /api/profiles/{profileId}/history`
- `POST /api/profiles/agent-infer`
- `GET /api/courses`
- `POST /api/courses`
- `GET /api/courses/{courseId}`
- `GET /api/courses/{courseId}/resources`
- `GET /api/resource-types`
- `GET /api/tasks`
- `POST /api/tasks/resource-generation`
- `GET /api/tasks/{taskId}`
- `GET /api/tasks/{taskId}/steps`
- `GET /api/tasks/{taskId}/model-invocations`
- `GET /api/tasks/{taskId}/audits`
- `GET /api/tasks/{taskId}/events`
- `POST /api/learning/tutoring`
- `POST /api/learning/assessments/generate`
- `POST /api/learning/assessments/grade`
- `GET /api/learning/events`
- `GET /api/learning/tutoring`
- `GET /api/learning/attempts`
- `GET /api/learning/mastery`
- `GET /api/learning/evaluation-reports`
- `POST /api/learning/path-plans`
- `POST /api/learning/knowledge-graphs`
- `POST /api/learning/content-audits`
- `POST /api/learning/code-practice/generate`
- `POST /api/learning/code-practice/grade`
- `POST /api/learning/storyboards`
- `POST /api/learning/prerequisites/diagnose`
- `POST /api/learning/resource-bundles/curate`
- `POST /api/learning/portfolio-reports`
- `POST /api/learning/agent-traces`
- `POST /api/learning/events/analyze`
- `POST /api/learning/assessments/item-analysis`
- `POST /api/learning/code-projects/review`
- `POST /api/teaching/course-diagnostics`
- `POST /api/teaching/class-analytics`
- `GET /api/demo/readiness-report`
- `POST /api/demo/scenario-plans`

## 推荐演示顺序

1. 演示总览：确认 Java 后端、Python Agent、前端 API 地址均正常。
2. 学生画像：创建画像，展示画像维度、证据和雷达图。
3. 课程资源：创建课程，查看课程资源列表。
4. 资源生成：选择画像与课程，创建资源生成任务。
5. 任务详情：展示多智能体步骤、实时事件、防幻觉审核和生成结果下载。
6. 学习闭环：演示智能答疑、测评生成、自动批改和学习记录图表。
7. 智能体工具箱：展示 Java 后端代理调用多个 Agent 能力。
8. 教师分析：展示班级掌握度、风险学生、干预分组和资源缺口。
9. 评委模式：导出答辩 JSON、Markdown 和可打印 HTML。

## 常见错误

- `npm ENOENT`：当前目录没有 `package.json`。先执行 `cd D:\competiton\software\softwareCup\frontend`。
- 后端连接失败：确认 `VITE_API_BASE_URL=http://localhost:8080/api`，并启动 Spring Boot 后端。
- Python Agent 未启动：资源生成、画像推断、学习闭环等 AI 能力需要后端能访问 `http://localhost:9001/health`。
- `JAVA_HOME` 未配置：安装 JDK 后设置 `JAVA_HOME`，再运行 `.\mvnw.cmd spring-boot:run`。
- Maven 一直下载：首次启动后端会下载依赖，等待完成即可；网络慢时可以多等几分钟。
- 端口占用：如果 `5173` 被占用，执行 `npm.cmd run dev -- --port 5174`。
- PowerShell 禁止 `npm.ps1`：使用 `npm.cmd`，不要直接输入 `npm`。
