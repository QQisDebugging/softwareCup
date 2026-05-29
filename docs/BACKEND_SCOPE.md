# Java 后端主程范围

## 当前已落地

- Spring Boot 后端工程，默认 H2 本地数据库，可通过 `postgres` profile 切换 PostgreSQL。
- Flyway 迁移脚本，覆盖画像、课程、学习资源、任务链路、智能体产物和学习闭环相关表。
- 学习画像接口：对话建档、画像详情、维度查询、维度更新和画像历史。
- 课程与学习资源接口：课程创建/查询、课程资源查询和固定资源类型查询。
- 资源生成任务状态机：`PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED`，并记录任务步骤、模型调用、审核结果和 SSE 进度事件。
- 文件上传和上传元数据记录。
- 后端调用 Python resource-agent 的 HTTP 契约，统一通过 `softwarecup.agent.resource-base-url`，环境变量使用 `SOFTWARECUP_AGENT_RESOURCE_BASE_URL`。
- Python Agent provider 口径统一为 `offline` / `xfyun_spark`，环境变量使用 `SOFTWARECUP_AGENT_PROVIDER`，旧的 `RESOURCE_AGENT_PROVIDER` 仍兼容。
- 智能辅导、测评生成、自动批改和画像更新闭环接口。
- 学习事件、答疑会话、测评尝试、知识掌握度、学习路径、资源推荐和阶段评估报告落库。
- 高级 Agent 代理接口：学习路径规划、知识图谱、防幻觉审计、课程诊断、代码实操、分镜、先修诊断、资源策展、学习档案、链路追踪、画像抽取、学习事件分析、题目分析、项目代码审查、班级学情分析和演示脚本规划。
- 初赛评委模式接口 `/api/demo/readiness-report`，可聚合核心能力证据用于答辩看板。

## 下一阶段后端任务

1. 接入真实登录和学生账号体系，补齐学生、教师、班级和权限边界。
2. 把课程 JSON 导入做成初始化脚本或后台管理接口，避免每次演示手工创建课程。
3. 继续补强学习行为采集，覆盖资源浏览、学习时长、主观反馈、错题复盘和代码练习过程。
4. 接入讯飞星火真实调用环境，记录真实 provider、model、prompt 摘要、耗时、token 或计费字段，并保留 offline 降级证据。
5. 为画像建档、资源生成、学习闭环、Agent 代理和评委模式接口补接口测试。
6. 与 Vue3 前端确认最终演示接口清单，固定请求/响应字段，减少临近提交前的对接变更。
