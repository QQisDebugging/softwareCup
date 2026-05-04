# 国赛级核心能力说明

本分支围绕 A3 赛题的核心评分点，把系统从“资源生成工具”升级为“可持续学习闭环智能体系统”。实现重点不是堆页面，而是让画像、知识库、生成、辅导、测评和画像更新形成可验证的数据链路。

## 已实现能力

1. 多智能体资源生成
   - Python 主程使用 `ResourceGenerationWorkflow` 串联画像分析、RAG 检索、资源规划、资源生成、安全审查和结果装配。
   - 后端通过异步任务状态机调用 Python 主程，支持任务创建、运行、失败记录和资源落库。

2. RAG 知识库与文档解析
   - 支持 JSON、TXT、Markdown、CSV、PDF、DOCX 解析。
   - 支持默认课程知识库和请求级 `knowledgeBasePaths` / `documentTexts` 动态导入。
   - 向量库导入幂等，重复资料不会无限堆积 chunk。

3. 智能辅导 Agent
   - `POST /agents/tutoring` 提供基于 RAG 的课程答疑。
   - 输出答案、引用依据、追问问题、学习动作、画像信号和 Mermaid 图解。
   - Java 后端 `POST /api/learning/tutoring` 已接入并保存答疑历史。

4. 自适应测评 Agent
   - `POST /agents/assessment/generate` 生成选择题、判断题、简答题和代码纠错题。
   - `POST /agents/assessment/grade` 自动批改，输出逐题反馈、薄弱点、后续资源类型和画像更新建议。
   - Java 后端 `POST /api/learning/assessments/grade` 会把测评结果写入 `quiz_attempts`，并自动更新画像维度。

5. 学习闭环事件库
   - `learning_events` 记录辅导完成、测评生成、测评批改等关键学习事件。
   - `tutoring_sessions` 保存答疑内容、引用、行动建议和画像信号。
   - `quiz_attempts` 保存题目、答案、批改结果和掌握度。

6. 防幻觉与可解释输出
   - 资源生成、辅导、测评均返回检索引用或依据片段。
   - 空检索和模型失败时会降级到离线模板，避免演示链路中断。
   - 画像更新保留 evidence、source 和 confidenceScore，便于答辩说明依据。

7. 功能广度增强 Agent
   - `PathPlannerAgent` 生成个性化学习路径和资源推荐。
   - `KnowledgeGraphAgent` 生成课程知识图谱并高亮薄弱点。
   - `ContentAuditAgent` 输出可信度、引用覆盖率、未支撑断言和修订内容。
   - `CourseDiagnosisAgent` 为教师诊断课程覆盖率、缺失资源和测评蓝图。
   - `CodePracticeAgent` 生成代码实操题并按静态规则批改。
   - `StoryboardAgent` 生成 PPT 大纲、视频分镜、旁白和素材提示词。

8. 国赛展示增强 Agent
   - `PrerequisiteDiagnosisAgent` 做新课入口诊断，输出先修准备度、诊断题、补救动作和画像更新。
   - `ResourceCurationAgent` 将 RAG 证据、候选资源、薄弱点和时间预算重排成个性化资源包。
   - `PortfolioReportAgent` 汇总资源完成、测评、答疑、代码实操和复盘证据，生成教师可读学习档案。
   - `AgentTraceAgent` 记录智能体步骤、质量门禁、引用证据、降级事件和复现说明，支撑可解释答辩。
   - `ProfileInferenceAgent` 从对话和学习记录抽取 8 个画像维度，支撑“对话式学习画像自主构建”。
   - `LearningEventAnalysisAgent` 分析学习事件、掌握趋势和风险信号，驱动下一轮资源或测评。
   - `AssessmentItemAnalysisAgent` 进行题目质量与误区聚类分析，给教师端提供补救教学计划。

## 对比普通项目的提升点

- 不只生成资源，还能在学生使用后反向更新画像。
- 不只做聊天问答，还保存答疑证据、后续动作和历史事件。
- 不只做题库，还能自动批改、诊断薄弱点，并驱动下一轮资源推荐。
- 不只展示结果，还能展示画像抽取、先修诊断、资源策展、学习分析、学习档案和智能体追踪，证明系统有完整学习闭环和可解释链路。
- 不依赖真实密钥也能完整演示，接入讯飞星火后可直接替换生成 Provider。
- 后端、Python Agent、数据库迁移、烟测脚本和接口文档都已闭合，便于评审复现。

## 推荐演示路径

1. 创建学生画像和课程。
2. 运行对话式画像抽取，展示 8 个画像维度、证据和置信度。
3. 运行先修诊断，展示准备度、诊断题和补救建议。
4. 运行资源策展，展示按画像重排后的资源包和覆盖图。
5. 针对同一课程问题发起智能辅导，展示引用、图解和学习动作。
6. 针对薄弱主题生成自适应测评并自动批改。
7. 运行学习事件分析和题目分析，展示参与度、趋势、风险、高错题和误区聚类。
8. 展示画像维度被 `MASTERY_WEAKNESS`、`ERROR_PRONE_POINTS`、`LEARNING_ENGAGEMENT` 自动更新。
9. 生成学习档案报告，展示证据时间线、掌握度雷达、风险提示和教师评语草稿。
10. 打开智能体追踪，展示步骤、质量门禁、引用证据和降级事件。

可直接运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo_learning_loop.ps1
```

Python 智能体全量 smoke：

```powershell
cd agents/resource-agent
.\.venv\Scripts\python.exe scripts\smoke_full_ai_agents.py
```
