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

## 对比普通项目的提升点

- 不只生成资源，还能在学生使用后反向更新画像。
- 不只做聊天问答，还保存答疑证据、后续动作和历史事件。
- 不只做题库，还能自动批改、诊断薄弱点，并驱动下一轮资源推荐。
- 不依赖真实密钥也能完整演示，接入讯飞星火后可直接替换生成 Provider。
- 后端、Python Agent、数据库迁移、烟测脚本和接口文档都已闭合，便于评审复现。

## 推荐演示路径

1. 创建学生画像和课程。
2. 针对同一课程问题发起智能辅导，展示引用、图解和学习动作。
3. 针对薄弱主题生成自适应测评。
4. 提交答案并自动批改。
5. 展示画像维度被 `MASTERY_WEAKNESS` 和 `ERROR_PRONE_POINTS` 自动更新。
6. 查询学习事件、答疑历史和测评历史，证明闭环数据已落库。

可直接运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\demo_learning_loop.ps1
```

Python 智能体全量 smoke：

```powershell
cd agents/resource-agent
.\.venv\Scripts\python.exe scripts\smoke_full_ai_agents.py
```
