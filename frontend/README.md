# SoftwareCup Frontend

Vue3 + Vite + TypeScript 前端主程，用于展示软件杯 A3 个性化学习多智能体系统。

## 启动

```powershell
cd D:\competiton\software\softwareCup\frontend
npm.cmd install
npm.cmd run dev -- --port 5173
```

构建与类型检查：

```powershell
npm.cmd run typecheck
npm.cmd run build
```

访问地址：

```text
http://127.0.0.1:5173/
```

## 环境变量

`.env.development`：

```text
VITE_API_BASE_URL=http://localhost:8080/api
```

前端通过 Java 后端访问 AI 能力。Python Agent 不由前端直接作为主链路调用。

## 依赖服务

Python Agent：

```powershell
cd D:\competiton\software\softwareCup\agents\resource-agent
.\.venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

Spring Boot 后端：

```powershell
cd D:\competiton\software\softwareCup\backend
.\mvnw.cmd spring-boot:run
```

前端：

```powershell
cd D:\competiton\software\softwareCup\frontend
npm.cmd run dev -- --port 5173
```

## 页面功能

- 演示总览：系统状态、任务概览、演示准备清单。
- 学生画像：对话式画像创建、维度展示、雷达图、JSON/Markdown 下载。
- 课程资源：课程创建、课程资源列表、资源 Markdown 预览与下载。
- 资源生成：选择画像、课程和资源类型，创建异步生成任务。
- 任务详情：任务进度、9 步智能体流程、SSE 事件、防幻觉审核、模型调用、资源正文下载。
- 学习闭环：智能答疑、测评生成、自动批改、学习效果图表、学习报告下载。
- 智能体工具箱：通过 Java 后端代理调用增强 Agent，支持编辑 JSON、响应展示和下载。
- 教师分析：课程诊断、班级学情分析、图表与 JSON 下载。
- 评委模式：赛题完成度、证据指标、推荐演示流、答辩报告导出。

## 推荐演示顺序

1. 学生画像
2. 课程创建
3. 资源生成
4. 任务详情
5. 学习闭环
6. 智能体工具箱
7. 教师分析
8. 评委模式

## 常见错误

- `npm ENOENT`：当前目录没有 `package.json`。先执行 `cd D:\competiton\software\softwareCup\frontend`。
- 后端连接失败：确认 `VITE_API_BASE_URL=http://localhost:8080/api`，并启动 Spring Boot 后端。
- Python Agent 未启动：资源生成、画像推断、学习闭环等 AI 能力需要 `http://localhost:9001/health` 可访问。
- 端口占用：如果 `5173` 被占用，执行 `npm.cmd run dev -- --port 5174`，或关闭旧的 Vite 进程。
- PowerShell 禁止 `npm.ps1`：使用 `npm.cmd`，不要直接输入 `npm`。
