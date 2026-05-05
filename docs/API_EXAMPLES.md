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
  resourceType = '课程讲解文档'
  modality = '文本+图解脚本'
  prompt = '面向 Java 基础较弱的大二学生，用项目案例讲解 Controller、DTO 和 Service 分层。'
} | ConvertTo-Json)

Invoke-RestMethod http://localhost:8080/api/tasks/$($task.id)
Invoke-RestMethod http://localhost:8080/api/courses/$($course.id)/resources
```
## 多智能体任务链与学习闭环

查询智能体定义和固定资源类型：

```powershell
Invoke-RestMethod http://localhost:8080/api/agents
Invoke-RestMethod http://localhost:8080/api/resource-types
```

创建资源生成任务时，`resourceType` 建议使用固定枚举或中文名称，例如 `课程讲解文档`、`知识点思维导图`、`练习题/测验`、`拓展阅读`、`实操案例`、`视频讲解脚本/动画脚本`。

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
Invoke-RestMethod "http://localhost:8080/api/learning/paths?studentProfileId=$($profile.profile.id)"
Invoke-RestMethod "http://localhost:8080/api/learning/recommendations?studentProfileId=$($profile.profile.id)"
```

SSE 进度接口：

```powershell
curl.exe -N http://localhost:8080/api/tasks/$($task.id)/events
```

记录学习行为和测验结果：

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/learning/events -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  resourceId = $task.createdResourceId
  eventType = 'RESOURCE_VIEW'
  durationSeconds = 780
  feedbackScore = 4
  eventPayload = '完成 Controller 示例阅读'
} | ConvertTo-Json)

Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/learning/quiz-attempts -ContentType 'application/json' -Body (@{
  studentProfileId = $profile.profile.id
  courseId = $course.id
  resourceId = $task.createdResourceId
  score = 78
  maxScore = 100
  correctCount = 8
  totalCount = 10
  weakPoints = 'Controller 与 Service 职责边界'
} | ConvertTo-Json)

Invoke-RestMethod "http://localhost:8080/api/learning/mastery?studentProfileId=$($profile.profile.id)&courseId=$($course.id)"
Invoke-RestMethod "http://localhost:8080/api/learning/evaluation-reports?studentProfileId=$($profile.profile.id)&courseId=$($course.id)"
```
