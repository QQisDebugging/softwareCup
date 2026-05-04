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

创建后会自动生成不少于 8 个结构化画像维度：

- `KNOWLEDGE_FOUNDATION`：知识基础
- `COGNITIVE_STYLE`：认知风格
- `LEARNING_GOAL`：学习目标
- `INTEREST_DIRECTION`：兴趣方向
- `ERROR_PRONE_POINTS`：易错点
- `TIME_CONSTRAINT`：时间约束
- `RESOURCE_PREFERENCE`：资源偏好
- `MASTERY_WEAKNESS`：掌握度/薄弱点

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
  resourceType = '微课讲义'
  modality = '文本+图解脚本'
  prompt = '面向 Java 基础较弱的大二学生，用项目案例讲解 Controller、DTO 和 Service 分层。'
} | ConvertTo-Json)

Invoke-RestMethod http://localhost:8080/api/tasks/$($task.id)
Invoke-RestMethod http://localhost:8080/api/courses/$($course.id)/resources
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
