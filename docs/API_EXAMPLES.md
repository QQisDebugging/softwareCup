# API 调用样例

## 创建学习画像

```powershell
$profile = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/profiles/dialogue -ContentType 'application/json' -Body (@{
  studentName = '张同学'
  major = '软件工程'
  currentLevel = '大二，Java 基础较弱'
  learningGoal = '两周内掌握 Spring Boot 项目开发流程'
  preferences = '喜欢图解、案例驱动和短视频脚本'
  constraintsText = '每天可学习 45 分钟'
  dialogueTurns = @(
    '系统：你希望提升哪门课？',
    '学生：Java Web 和 Spring Boot。',
    '系统：你更喜欢什么形式？',
    '学生：先图解，再做项目。'
  )
} | ConvertTo-Json)
```

## 国赛增强接口样例

以下样例假设 `$course` 和 `$profile` 已按本文后续步骤创建；如果只测 Python 服务，可手动替换为固定字符串。

```powershell
$aiBase = 'http://localhost:9001'
$ragEval = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/evaluation/rag-quality" -ContentType 'application/json' -Body (@{
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  question = '为什么 Controller 不应该直接访问 Repository？'
  answer = '因为 Controller 应只负责请求响应，业务规则在 Service，数据访问在 Repository。这样更容易测试，也能降低耦合。'
  expectedAnswer = '需要说明分层职责、测试性和耦合风险。'
  contexts = @('Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。')
} | ConvertTo-Json -Depth 12)

$humanGate = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/review/human-gate" -ContentType 'application/json' -Body (@{
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  resourceTitle = 'REST API 分层讲解'
  content = 'Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。发布前需要展示引用证据。'
  rubric = @('必须有引用证据', '必须说明分层职责')
} | ConvertTo-Json -Depth 12)

$voicePackage = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/multimodal/voice-package" -ContentType 'application/json' -Body (@{
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  topic = 'REST API 分层'
  script = '第一步介绍 Controller。第二步介绍 Service。第三步介绍 Repository。'
  targetDurationMinutes = 3
} | ConvertTo-Json -Depth 12)

$ocrQuestion = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/document/ocr-question" -ContentType 'application/json' -Body (@{
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  imageName = 'rest-api-question.png'
  ocrText = '1. Spring Boot 中 Controller 的主要职责是什么？A. 数据访问 B. 请求响应 C. 物理存储 D. 编译代码'
} | ConvertTo-Json -Depth 12)

$graphRag = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/knowledge/graphrag-query" -ContentType 'application/json' -Body (@{
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  query = 'Controller 直接访问 Repository 为什么不好？'
  weaknessSignals = @('MVC 分层职责')
} | ConvertTo-Json -Depth 12)

$errorBook = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/assessment/error-book" -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  attempts = @(
    @{ questionId = 'q1'; knowledgePoint = 'MVC 分层职责'; questionType = '选择题'; score = 3; maxScore = 10; correct = $false; answerSummary = '混淆 Controller 和 Repository'; feedback = '分层职责错误' },
    @{ questionId = 'q2'; knowledgePoint = 'REST API 边界'; questionType = '简答题'; score = 6; maxScore = 10; correct = $false; answerSummary = '接口边界描述不完整'; feedback = '缺少状态码' }
  )
} | ConvertTo-Json -Depth 12)

$coverage = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/course/coverage" -ContentType 'application/json' -Body (@{
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  chapters = @('MVC 分层职责', 'REST API 边界', '异常响应')
  resourceInventory = @(
    @{ title = 'MVC 图解'; resourceType = '思维导图'; knowledgePoints = @('MVC 分层职责'); estimatedMinutes = 10 }
  )
  assessmentInventory = @(
    @{ title = 'MVC 选择题'; questionType = '选择题'; knowledgePoints = @('MVC 分层职责'); difficulty = '中' }
  )
} | ConvertTo-Json -Depth 12)

$defensePack = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/demo/defense-pack" -ContentType 'application/json' -Body (@{
  projectName = '个性化学习多智能体系统'
  implementedFeatures = @('对话式画像', 'RAG 资源生成', '防幻觉评测', '错题本', '班级分析')
  techStack = @('FastAPI', 'LangGraph', 'LangChain', 'RAG', 'Embedding')
  riskConcerns = @('讯飞 API 不可用', '评委追问防幻觉')
  apiStatus = @{ activeProvider = 'offline'; fallbackProvider = 'offline' }
} | ConvertTo-Json -Depth 12)

$runRecord = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/runs/record" -ContentType 'application/json' -Body (@{
  taskName = 'RAG 质量评测演示'
  endpoint = '/agents/evaluation/rag-quality'
  provider = 'offline'
  requestPayload = @{ question = '为什么需要引用？' }
  responsePayload = @{ overallScore = $ragEval.overallScore }
  steps = @(
    @{ order = 1; agentName = 'rag_evaluation_agent'; inputSummary = 'question+answer'; outputSummary = $ragEval.summary; durationMs = 0; status = 'success' }
  )
} | ConvertTo-Json -Depth 12)

Invoke-RestMethod "$aiBase/agents/runs/$($runRecord.runId)"
```

创建后会自动生成不少于 8 个结构化画像维度：

- `KNOWLEDGE_FOUNDATION`：知识基础
- `COGNITIVE_STYLE`：认知风格
- `LEARNING_GOAL`：学习目标
- `INTEREST_DIRECTION`：兴趣方向
- `ERROR_PRONE_POINTS`：易错点
- `TIME_CONSTRAINT`：时间约束
- `RESOURCE_PREFERENCE`：资源偏好
- `MASTERY_WEAKNESS`：掌握度/薄弱点

默认流程会先调用 Python `ProfileInferenceAgent` 做自然语言画像抽取，并在 `agent_artifacts` 中记录 `PROFILE_INFERENCE_MAIN_FLOW` 产物；如果 Python 服务不可用，后端会降级使用规则画像，接口仍可返回完整画像。

学习行为写入后还会自动维护：

- `LEARNING_BEHAVIOR_PATTERN`：学习行为模式

## 查询画像维度和演化历史

```powershell
Invoke-RestMethod http://localhost:8080/api/profiles/$($profile.profile.id)/dimensions
Invoke-RestMethod http://localhost:8080/api/profiles/$($profile.profile.id)/history
```

## 动态更新画像维度

```powershell
$updatedProfile = Invoke-RestMethod -Method Put -Uri http://localhost:8080/api/profiles/$($profile.profile.id)/dimensions -ContentType 'application/json' -Body (@{
  reason = '完成 Spring Boot Controller 练习后更新画像'
  dimensions = @(
    @{
      dimensionKey = 'MASTERY_WEAKNESS'
      value = 'Controller 和 DTO 基本理解，Service 分层仍需通过项目案例巩固'
      evidence = '练习测试得分 72 分，错题集中在 Controller 直接访问 Repository 的分层问题'
      confidenceScore = 0.82
      source = 'quiz_attempt'
    },
    @{
      dimensionKey = 'ERROR_PRONE_POINTS'
      value = '容易把 Controller、Service、Repository 的职责边界混淆'
      evidence = '答疑记录和练习错题均出现分层职责混淆'
      confidenceScore = 0.86
      source = 'tutoring_session'
    }
  )
} | ConvertTo-Json -Depth 8)
```

## 创建课程

```powershell
$courseJson = Get-Content data/courses/java-web-software-engineering.json -Raw
$course = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/courses -ContentType 'application/json' -Body (@{
  title = 'Java Web 应用开发与软件工程实践'
  department = '计算机科学与技术'
  description = '覆盖 Spring Boot、数据库、文件上传、任务管理和智能体调用。'
  creditHours = 48
  syllabusJson = $courseJson
} | ConvertTo-Json)
```

## 创建资源生成任务

```powershell
$task = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/tasks/resource-generation -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  topic = 'Spring Boot Controller 与 REST API'
  resourceType = '课程讲解文档'
  modality = '文本+图解脚本'
  prompt = '面向 Java 基础较弱的大二学生，用项目案例讲解 Controller、DTO 和 Service 分层。'
} | ConvertTo-Json)

Invoke-RestMethod http://localhost:8080/api/tasks/$($task.id)
Invoke-RestMethod http://localhost:8080/api/tasks/$($task.id)/steps
Invoke-RestMethod http://localhost:8080/api/tasks/$($task.id)/model-invocations
Invoke-RestMethod http://localhost:8080/api/tasks/$($task.id)/audits
Invoke-RestMethod http://localhost:8080/api/courses/$($course.id)/resources
```

`/api/tasks/{taskId}/audits` 会返回课程证据、学术准确性、内容安全和 `HUMAN_REVIEW_GATE` 四类审核记录。资源生成任务会强制调用 Python `ContentAuditAgent`；如果发现未支撑断言、绝对化承诺、密钥泄露、代写作弊或敏感违规表达，会写入 `REVIEW_REQUIRED` 并把修订稿写回资源正文。

资源类型固定覆盖 7 类，可直接给前端做筛选项：

```powershell
Invoke-RestMethod http://localhost:8080/api/resource-types
```

## 学习闭环：辅导、测评、画像自动更新

```powershell
$tutoring = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/learning/tutoring -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  question = 'Controller 为什么不应该直接写复杂业务逻辑？'
  modality = '文本+图解'
  documentTexts = @('Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。')
} | ConvertTo-Json -Depth 8)

$assessment = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/learning/assessments/generate -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  topic = 'Spring Boot Controller 与 REST API'
  difficulty = '自适应'
  count = 4
  documentTexts = @('Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。')
} | ConvertTo-Json -Depth 8)

$grade = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/learning/assessments/grade -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  topic = 'Spring Boot Controller 与 REST API'
  questions = $assessment.questions
  answers = @(
    @{ questionId = $assessment.questions[0].id; answer = $assessment.questions[0].answer },
    @{ questionId = $assessment.questions[1].id; answer = '错误' },
    @{ questionId = $assessment.questions[2].id; answer = 'Controller 负责请求响应，Service 负责业务规则。' },
    @{ questionId = $assessment.questions[3].id; answer = 'Controller -> Service -> Repository -> DB' }
  )
} | ConvertTo-Json -Depth 30)

Invoke-RestMethod http://localhost:8080/api/learning/events?studentProfileId=$($profile.profile.id)
Invoke-RestMethod http://localhost:8080/api/learning/tutoring?studentProfileId=$($profile.profile.id)
Invoke-RestMethod http://localhost:8080/api/learning/attempts?studentProfileId=$($profile.profile.id)
```

普通学习行为也会写回画像、掌握度和阶段评估：

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/learning/events -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  resourceId = $task.createdResourceId
  eventType = 'FEEDBACK'
  durationSeconds = 300
  feedbackScore = 2
  eventPayload = '{}'
} | ConvertTo-Json)
```

## 查询 Agent 产物与证据

高级 Agent 代理接口会自动保存结构化产物、引用、安全摘要、traceId 和耗时：

```powershell
$pathPlan = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/learning/path-plans -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  studentProfileSummary = $profile.profile.dialogueSummary
  courseTitle = $course.title
  topic = 'Spring Boot Controller 与 REST API'
  traceId = 'demo-trace-001'
  documentTexts = @('Controller 负责请求响应，Service 负责业务规则。')
} | ConvertTo-Json -Depth 8)

Invoke-RestMethod "http://localhost:8080/api/agent-artifacts?studentProfileId=$($profile.profile.id)"
```

## 初赛评委模式报告

```powershell
Invoke-RestMethod "http://localhost:8080/api/demo/readiness-report?studentProfileId=$($profile.profile.id)&courseId=$($course.id)&taskId=$($task.id)"
```

该接口会聚合画像维度、画像历史、智能体数量、资源类型数量、任务步骤、模型调用、内容审核、学习路径、资源推荐、学习行为、测评记录、掌握度、评估报告和 Agent 产物，按赛题要求输出达成状态、分数、证据接口和推荐演示顺序。适合给前端做“评委模式/答辩看板”。

## Python 智能体增强接口：先修诊断、资源策展、档案报告、链路追踪

这些接口目前由 Python 主程直接提供，Java 后端可按 `docs/JAVA_VUE3_INTEGRATION_GUIDE.md` 中的建议封装为 `/api/learning/*`。

```powershell
$aiBase = 'http://localhost:9001'

$preq = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/prerequisite/diagnose" -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  studentProfileSummary = 'Java 基础较弱，容易混淆 Controller、Service、Repository。'
  courseTitle = 'Java Web 应用开发与软件工程实践'
  targetTopic = 'Spring Boot Controller 与 REST API'
  completedTopics = @('Java 面向对象基础')
  assessmentWeaknesses = @('HTTP 请求响应', 'MVC 分层职责')
  documentTexts = @('学习 Spring Boot Controller 前，需要理解 HTTP、JSON、MVC 分层和接口调试。')
} | ConvertTo-Json -Depth 10)

$bundle = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/resources/curate" -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  studentProfileSummary = 'Java 基础较弱，喜欢图解和项目案例。'
  courseTitle = 'Java Web 应用开发与软件工程实践'
  topic = 'Spring Boot Controller 与 REST API'
  weaknesses = @('HTTP 请求响应', 'MVC 分层职责')
  timeBudgetMinutes = 120
  candidateResources = @('Controller 负责请求响应，Service 负责业务规则，Repository 负责数据访问。')
} | ConvertTo-Json -Depth 10)

$report = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/report/portfolio" -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  studentName = '张同学'
  studentProfileSummary = 'Java 基础较弱，最近开始主动复盘错题。'
  courseTitle = 'Java Web 应用开发与软件工程实践'
  topic = 'Spring Boot Controller 与 REST API'
  completedResources = @($bundle.summary)
  assessmentSummaries = @('入口测评 58/100，复测 72/100。')
  tutoringSummaries = @($tutoring.answer)
  codePracticeSummaries = @('REST API 分层改造练习批改 76分。')
  weaknesses = @('HTTP 状态码', 'MVC 分层职责')
} | ConvertTo-Json -Depth 12)

$trace = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/trace/explain" -ContentType 'application/json' -Body (@{
  taskName = '个性化资源生成'
  userIntent = '为 Java 基础较弱学生生成 REST API 分层资源'
  studentProfileId = $profile.profile.id
  courseId = $course.id
  involvedAgents = @('profile_agent', 'rag_retrieval_agent', 'resource_generator_agent', 'content_audit_agent')
  requestPayload = @{ topic = 'Spring Boot Controller 与 REST API'; weaknesses = @('MVC 分层职责') }
  responseSummary = $bundle.summary
  fallbackEvents = @('offline provider 可保证无密钥演示链路不中断。')
} | ConvertTo-Json -Depth 12)

$inferred = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/profile/infer" -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  declaredMajor = '软件工程'
  currentLevel = '大二，Java 基础较弱'
  learningGoal = '两周内掌握 Spring Boot REST API 分层开发'
  preferences = '喜欢图解、项目案例和短视频脚本'
  constraintsText = '每天可学习 45 分钟'
  dialogueTurns = @('学生：Controller、Service、Repository 分层总混。', '学生：我喜欢先看图解，再做一个能跑的小项目。')
  assessmentSummaries = @('入口测评 58/100，薄弱点是 HTTP 请求响应和 MVC 分层。')
} | ConvertTo-Json -Depth 12)

$eventAnalysis = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/learning/events/analyze" -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  studentProfileSummary = 'Java 基础较弱，喜欢图解和项目案例。'
  courseTitle = 'Java Web 应用开发与软件工程实践'
  targetTopic = 'Spring Boot Controller 与 REST API'
  learningEvents = @('完成 2 个资源卡。', '错题复盘：同一错误是 Controller 直接访问 Repository。')
  resourceUsage = @($bundle.summary)
  assessmentSummaries = @('入口测评 58/100。', '复测 72/100。')
  tutoringSummaries = @($tutoring.answer)
} | ConvertTo-Json -Depth 12)

$itemAnalysis = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/assessment/item-analysis" -ContentType 'application/json' -Body (@{
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  topic = 'Spring Boot Controller 与 REST API'
  studentProfileId = $profile.profile.id
  attempts = @(
    @{ questionId = 'q1'; knowledgePoint = 'HTTP 请求响应'; questionType = '选择题'; score = 4; maxScore = 10; correct = $false; feedback = '状态码和请求响应职责理解不稳。' },
    @{ questionId = 'q2'; knowledgePoint = 'Controller 分层职责'; questionType = '简答题'; score = 5; maxScore = 15; correct = $false; feedback = 'Controller、Service、Repository 分层职责混淆。' },
    @{ questionId = 'q3'; knowledgePoint = 'REST API 设计'; questionType = '代码纠错题'; score = 13; maxScore = 15; correct = $true; feedback = '能写出 Controller -> Service -> Repository 调用链。' }
  )
} | ConvertTo-Json -Depth 12)

$projectReview = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/code/project-review" -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  studentProfileSummary = 'Java 基础较弱，容易把 Controller、Service、Repository 职责写混。'
  courseTitle = 'Java Web 应用开发与软件工程实践'
  projectTitle = 'REST API 分层练习'
  targetTopic = 'Spring Boot Controller 与 REST API'
  files = @(
    @{ path = 'src/main/java/demo/UserController.java'; language = 'Java'; content = '@RestController class UserController { UserRepository repo; @PostMapping("/u") User save(@RequestBody User u){ return repo.save(u); } }' }
  )
} | ConvertTo-Json -Depth 12)

$classAnalytics = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/class/analytics" -ContentType 'application/json' -Body (@{
  courseId = $course.id
  courseTitle = 'Java Web 应用开发与软件工程实践'
  topic = 'Spring Boot Controller 与 REST API'
  snapshots = @(
    @{ studentProfileId = $profile.profile.id; studentName = '张同学'; profileSummary = 'Java 基础较弱'; recentScores = @(48, 55); completedResources = 1; tutoringCount = 0; codePracticeCount = 0; weaknessSignals = @('HTTP 请求响应', 'MVC 分层职责'); learningEvents = @('只完成入口讲解') },
    @{ studentProfileId = 'peer-1'; studentName = '李同学'; profileSummary = '实操不足'; recentScores = @(68, 72); completedResources = 2; tutoringCount = 1; codePracticeCount = 0; weaknessSignals = @('MVC 分层职责', 'REST API 边界'); learningEvents = @('错题复盘') }
  )
} | ConvertTo-Json -Depth 12)

$demoPlan = Invoke-RestMethod -Method Post -Uri "$aiBase/agents/demo/scenario-plan" -ContentType 'application/json' -Body (@{
  scenarioTitle = '软件杯 A3 个性化学习多智能体 7 分钟演示'
  audience = '初赛评委'
  courseTitle = 'Java Web 应用开发与软件工程实践'
  studentProfileSummary = 'Java 基础较弱，喜欢图解和项目案例。'
  timeLimitMinutes = 7
  coreEndpoints = @('/agents/profile/infer', '/agents/prerequisite/diagnose', '/agents/resources/curate', '/agents/resource-generation', '/agents/assessment/grade', '/agents/report/portfolio', '/agents/trace/explain')
  availableArtifacts = @('smoke_full_ai_agents.py 输出', 'Java/Vue3 对接文档')
  riskConcerns = @('网络不稳定时使用 offline provider')
} | ConvertTo-Json -Depth 12)
```
