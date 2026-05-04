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
  studentProfileId = $profile.id
  courseId = $course.id
  topic = 'Spring Boot Controller 与 REST API'
  resourceType = '微课讲义'
  modality = '文本+图解脚本'
  prompt = '面向 Java 基础较弱的大二学生，用项目案例讲解 Controller、DTO 和 Service 分层。'
} | ConvertTo-Json)

Invoke-RestMethod http://localhost:8080/api/tasks/$($task.id)
Invoke-RestMethod http://localhost:8080/api/courses/$($course.id)/resources
```
