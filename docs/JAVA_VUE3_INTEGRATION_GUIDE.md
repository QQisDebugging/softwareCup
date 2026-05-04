# Java 后端与 Vue3 前端对接任务

本文件只描述其他同学需要接入的内容。Python 智能体侧已经提供对应 HTTP 接口、结构化响应和 smoke 脚本。

## Java 后端同学

统一通过现有 `softwarecup.agent.resource-base-url` 调用 Python 服务，沿用 `ResourceAgentClient` 风格新增方法。所有结果建议落库，便于演示历史和答辩追溯。

### 需要新增的 Agent 调用

- `POST /agents/path/plan`
  - 后端建议接口：`POST /api/learning/path-plans`
  - 建议表：`learning_path_plans`
  - 需要保存：路径阶段、推荐资源、复习节点、Mermaid 路线图、引用、画像更新建议。

- `POST /agents/knowledge/graph`
  - 后端建议接口：`POST /api/learning/knowledge-graphs`
  - 建议表：`knowledge_graph_snapshots`
  - 需要保存：nodes、edges、weakPointHighlights、Mermaid 图、引用。

- `POST /agents/safety/audit`
  - 后端建议接口：`POST /api/learning/content-audits`
  - 建议表：`content_audits`
  - 需要保存：overallScore、citationCoverage、unsupportedClaims、riskyClaims、revisedContent。

- `POST /agents/course/diagnose`
  - 后端建议接口：`POST /api/teaching/course-diagnostics`
  - 建议表：`course_diagnostics`
  - 需要保存：coverageScore、missingKnowledgePoints、missingResourceTypes、assessmentBlueprint、recommendedTasks。

- `POST /agents/code/practice/generate`
  - 后端建议接口：`POST /api/learning/code-practice/generate`
  - 建议表：`code_practice_exercises`
  - 需要保存：题目、starterCode、referenceSolution、rubric、testCases、引用。

- `POST /agents/code/practice/grade`
  - 后端建议接口：`POST /api/learning/code-practice/grade`
  - 建议表：`code_practice_attempts`
  - 需要保存：submissionCode、score、defects、correctedCode、nextActions、画像更新建议。

- `POST /agents/multimodal/storyboard`
  - 后端建议接口：`POST /api/learning/storyboards`
  - 建议表：`multimodal_storyboards`
  - 需要保存：pptOutline、videoStoryboard、narrationScript、assetPrompts、interactionQuestions、引用。

- `POST /agents/prerequisite/diagnose`
  - 后端建议接口：`POST /api/learning/prerequisites/diagnose`
  - 建议表：`prerequisite_diagnoses`
  - 需要保存：readinessScore、readinessLevel、prerequisites、diagnosticQuestions、recommendedWarmups、引用、画像更新建议。

- `POST /agents/resources/curate`
  - 后端建议接口：`POST /api/learning/resource-bundles/curate`
  - 建议表：`resource_bundles`
  - 需要保存：curatedResources、coverageMap、usagePlan、citations、profileDimensionUpdates。

- `POST /agents/report/portfolio`
  - 后端建议接口：`POST /api/learning/portfolio-reports`
  - 建议表：`portfolio_reports`
  - 需要保存：evidenceItems、masteryRadar、riskFlags、nextMilestones、teacherCommentsDraft、引用。

- `POST /agents/trace/explain`
  - 后端建议接口：`POST /api/learning/agent-traces`
  - 建议表：`agent_trace_logs`
  - 需要保存：traceId、traceSteps、qualityGates、fallbackEvents、reproducibilityNotes。

### 后端实现约束

- DTO 字段保持 camelCase，直接对齐 Python Pydantic 字段。
- 复杂结构先按 JSON text 落库，避免短期内引入 JSONB 兼容问题。
- 涉及 `profileDimensionUpdates` 的响应，复用现有 `ProfileService.updateDimensions` 写回画像。
- GET 历史接口都按 `studentProfileId` 或 `courseId` 查询最近 30 条即可。
- 所有 POST 接口失败时返回 `ProblemDetail`，保留 Python Agent 错误摘要。
- 建议为每次 AI 任务生成统一 `traceId`，后端把业务结果和 `/agents/trace/explain` 的追踪结果关联，便于教师端展示证据链和演示视频复现。

## Vue3 前端同学

前端先做能演示闭环的学生端和教师端页面，不需要一次性做复杂后台。

### 学生端页面

- 学习路径页
  - 调用 `/api/learning/path-plans`
  - 展示阶段时间线、推荐资源卡片、复习节点、Mermaid 路线图。

- 知识图谱页
  - 调用 `/api/learning/knowledge-graphs`
  - 渲染 nodes/edges 或 Mermaid 图。
  - 薄弱点节点用红色高亮。

- 防幻觉审计面板
  - 调用 `/api/learning/content-audits`
  - 展示可信度评分、引用覆盖率、未支撑断言、风险表达和修订版内容。

- 代码实操页
  - 调用 `/api/learning/code-practice/generate` 获取题目。
  - 用代码编辑框提交 `submissionCode`。
  - 调用 `/api/learning/code-practice/grade` 展示得分、缺陷、修正代码和下一步动作。

- 多模态资源页
  - 调用 `/api/learning/storyboards`
  - 展示 PPT 大纲、视频分镜、旁白、素材提示词。

- 先修诊断页
  - 调用 `/api/learning/prerequisites/diagnose`
  - 展示准备度仪表、先修知识列表、入口诊断题和补救资源按钮。

- 个性化资源包页
  - 调用 `/api/learning/resource-bundles/curate`
  - 按 `usagePlan` 展示学习顺序，按 `coverageMap` 展示知识点覆盖和待补齐项。

- 学习档案页
  - 调用 `/api/learning/portfolio-reports`
  - 展示证据时间线、掌握度雷达、风险提示、下一阶段里程碑和教师评语草稿。

- 智能体追踪抽屉
  - 调用 `/api/learning/agent-traces`
  - 以时间线展示 `traceSteps`，以状态卡展示 `qualityGates`、降级事件和复现说明。

### 教师端页面

- 课程诊断页
  - 调用 `/api/teaching/course-diagnostics`
  - 展示覆盖率、缺失知识点、缺失资源类型、测评蓝图、建设任务。

- 课程建设任务页
  - 从诊断结果生成待办卡片。
  - 支持一键进入资源生成、测评生成或多模态脚本生成。

### 前端交互要求

- 所有 AI 调用都要有 loading、失败提示、重新生成按钮。
- Mermaid 内容先用 Markdown/Mermaid 渲染；如果来不及做图谱组件，直接渲染 Mermaid 即可。
- 代码区建议用普通 textarea 起步，后续再换 Monaco Editor。
- 引用 `citations` 必须可展开，展示 title、source、score、text 摘要。
- 演示视频中优先展示：路径规划、知识图谱、防幻觉审计、代码批改、课程诊断。
- 新增推荐演示顺序：先修诊断 -> 资源策展 -> 资源生成/答疑 -> 测评批改 -> 学习档案 -> 智能体追踪，能完整体现“诊断、生成、学习、评估、优化、可解释”的闭环。

## Python 同学已提供的验证命令

```powershell
cd agents/resource-agent
.\.venv\Scripts\python.exe scripts\smoke_full_ai_agents.py
```

单功能 smoke：

```powershell
.\.venv\Scripts\python.exe scripts\smoke_path_planner.py
.\.venv\Scripts\python.exe scripts\smoke_knowledge_graph.py
.\.venv\Scripts\python.exe scripts\smoke_content_audit.py
.\.venv\Scripts\python.exe scripts\smoke_course_diagnosis.py
.\.venv\Scripts\python.exe scripts\smoke_code_practice.py
.\.venv\Scripts\python.exe scripts\smoke_storyboard.py
.\.venv\Scripts\python.exe scripts\smoke_prerequisite.py
.\.venv\Scripts\python.exe scripts\smoke_resource_curation.py
.\.venv\Scripts\python.exe scripts\smoke_portfolio_report.py
.\.venv\Scripts\python.exe scripts\smoke_agent_trace.py
```
