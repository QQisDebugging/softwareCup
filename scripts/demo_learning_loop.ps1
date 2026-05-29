param(
    [int]$PythonPort = 19001,
    [int]$BackendPort = 18080,
    [string]$JavaHome = "D:\idea\IntelliJ IDEA 2026.1\jbr"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$AgentDir = Join-Path $RepoRoot "agents\resource-agent"
$BackendDir = Join-Path $RepoRoot "backend"
$PythonExe = Join-Path $AgentDir ".venv\Scripts\python.exe"
$Mvnw = Join-Path $BackendDir "mvnw.cmd"
$ArtifactDir = Join-Path $RepoRoot "artifacts"
$PythonOut = Join-Path $env:TEMP "softwarecup-demo-python.out.log"
$PythonErr = Join-Path $env:TEMP "softwarecup-demo-python.err.log"
$BackendOut = Join-Path $env:TEMP "softwarecup-demo-backend.out.log"
$BackendErr = Join-Path $env:TEMP "softwarecup-demo-backend.err.log"

function Wait-HttpOk {
    param(
        [string]$Url,
        [string]$Name,
        [int]$Seconds
    )
    $deadline = (Get-Date).AddSeconds($Seconds)
    do {
        try {
            return Invoke-RestMethod -Method Get -Uri $Url -TimeoutSec 3
        } catch {
            Start-Sleep -Seconds 2
        }
    } while ((Get-Date) -lt $deadline)
    throw "$Name did not become ready at $Url"
}

function Stop-ProcessTree {
    param([int]$ProcessId)
    Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ProcessId } | ForEach-Object {
        Stop-ProcessTree -ProcessId $_.ProcessId
    }
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
}

function Repair-Utf8Mojibake {
    param($Value)

    if ($null -eq $Value) {
        return $null
    }
    if ($Value -is [string]) {
        if ($Value -notmatch "[\u00C2-\u00F4]") {
            return $Value
        }
        try {
            return [System.Text.Encoding]::UTF8.GetString(
                [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetBytes($Value)
            )
        } catch {
            return $Value
        }
    }
    if ($Value -is [System.Collections.IDictionary]) {
        $fixed = [ordered]@{}
        foreach ($key in $Value.Keys) {
            $fixed[$key] = Repair-Utf8Mojibake $Value[$key]
        }
        return $fixed
    }
    if ($Value -is [pscustomobject]) {
        $fixed = [ordered]@{}
        foreach ($property in $Value.PSObject.Properties) {
            $fixed[$property.Name] = Repair-Utf8Mojibake $property.Value
        }
        return [pscustomobject]$fixed
    }
    if ($Value -is [System.Collections.IEnumerable]) {
        return @($Value | ForEach-Object { Repair-Utf8Mojibake $_ })
    }
    return $Value
}

if (-not (Test-Path $PythonExe)) {
    throw "Python venv not found: $PythonExe. Run agents/resource-agent setup first."
}
if (-not (Test-Path $Mvnw)) {
    throw "Backend Maven wrapper not found: $Mvnw"
}

New-Item -ItemType Directory -Force $ArtifactDir | Out-Null
Remove-Item -ErrorAction SilentlyContinue $PythonOut, $PythonErr, $BackendOut, $BackendErr

$oldJavaHome = $env:JAVA_HOME
$oldSpringJson = $env:SPRING_APPLICATION_JSON
$pythonProcess = $null
$backendProcess = $null

try {
    $pythonProcess = Start-Process -FilePath $PythonExe `
        -ArgumentList @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "$PythonPort") `
        -WorkingDirectory $AgentDir `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $PythonOut `
        -RedirectStandardError $PythonErr
    Wait-HttpOk "http://127.0.0.1:$PythonPort/health" "Python agent" 30 | Out-Null

    if (Test-Path (Join-Path $JavaHome "bin\java.exe")) {
        $env:JAVA_HOME = $JavaHome
        $env:Path = "$env:JAVA_HOME\bin;$env:Path"
    }
    $env:SPRING_APPLICATION_JSON = @{
        server = @{ port = $BackendPort }
        spring = @{
            datasource = @{
                url = "jdbc:h2:mem:learningloopdemo;MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1"
            }
        }
        softwarecup = @{
            agent = @{
                "resource-base-url" = "http://127.0.0.1:$PythonPort"
            }
        }
    } | ConvertTo-Json -Depth 8 -Compress

    $backendProcess = Start-Process -FilePath $Mvnw `
        -ArgumentList @("-q", "spring-boot:run") `
        -WorkingDirectory $BackendDir `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $BackendOut `
        -RedirectStandardError $BackendErr
    Wait-HttpOk "http://127.0.0.1:$BackendPort/actuator/health" "Backend" 90 | Out-Null

    $profile = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:$BackendPort/api/profiles/dialogue" -ContentType "application/json; charset=utf-8" -Body (@{
        studentName = "Demo Student"
        major = "Computer Science"
        currentLevel = "Java basics are weak; Spring Boot beginner"
        learningGoal = "Master Spring Boot Controller, Service, Repository layering and REST API practice"
        preferences = "Prefers diagrams, short steps, and project cases"
        constraintsText = "45 minutes per day; focus on fundamentals and error-prone points"
        dialogueTurns = @(
            "I know basic Java syntax, but often mix Controller and Service responsibilities.",
            "I want to learn REST API and layering through project cases."
        )
        dimensions = @()
    } | ConvertTo-Json -Depth 8)

    $syllabus = @{
        weeks = @(
            @{ week = 1; topic = "Spring Boot project structure" },
            @{ week = 2; topic = "REST API and layered design" }
        )
    } | ConvertTo-Json -Depth 8 -Compress
    $course = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:$BackendPort/api/courses" -ContentType "application/json; charset=utf-8" -Body (@{
        title = "Java Web Application Development and Software Engineering Practice"
        department = "Computer Science"
        description = "Covers Spring Boot, REST API, database, async tasks, and learning profile loop."
        creditHours = 48
        syllabusJson = $syllabus
    } | ConvertTo-Json -Depth 8)

    $inlineDoc = "Controller handles request and response. Service handles business rules. Repository handles data access."
    $tutoring = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:$BackendPort/api/learning/tutoring" -ContentType "application/json; charset=utf-8" -Body (@{
        studentProfileId = $profile.profile.id
        courseId = $course.id
        question = "Why should a Controller avoid complex business logic?"
        modality = "text+diagram"
        documentTexts = @($inlineDoc)
    } | ConvertTo-Json -Depth 8)

    $assessment = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:$BackendPort/api/learning/assessments/generate" -ContentType "application/json; charset=utf-8" -Body (@{
        studentProfileId = $profile.profile.id
        courseId = $course.id
        topic = "Spring Boot Controller and REST API"
        difficulty = "adaptive"
        count = 4
        documentTexts = @($inlineDoc)
    } | ConvertTo-Json -Depth 8)

    $grade = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:$BackendPort/api/learning/assessments/grade" -ContentType "application/json; charset=utf-8" -Body (@{
        studentProfileId = $profile.profile.id
        courseId = $course.id
        topic = "Spring Boot Controller and REST API"
        questions = $assessment.questions
        answers = @(
            @{ questionId = $assessment.questions[0].id; answer = $assessment.questions[0].answer },
            @{ questionId = $assessment.questions[1].id; answer = "False" },
            @{ questionId = $assessment.questions[2].id; answer = "Controller handles requests and responses. Service handles business rules. Repository handles data access. A common mistake is putting business logic inside Controller." },
            @{ questionId = $assessment.questions[3].id; answer = "Controller -> Service -> Repository -> DB" }
        )
    } | ConvertTo-Json -Depth 30)

    $events = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:$BackendPort/api/learning/events?studentProfileId=$($profile.profile.id)"
    $sessions = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:$BackendPort/api/learning/tutoring?studentProfileId=$($profile.profile.id)"
    $attempts = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:$BackendPort/api/learning/attempts?studentProfileId=$($profile.profile.id)"

    $summary = [ordered]@{
        profileId = $profile.profile.id
        courseId = $course.id
        tutoringAnswerLength = $tutoring.answer.Length
        tutoringCitationCount = $tutoring.citations.Count
        generatedQuestions = $assessment.questions.Count
        gradeScore = $grade.score
        gradeMaxScore = $grade.maxScore
        profileUpdateCount = $grade.profileDimensionUpdates.Count
        eventCount = $events.Count
        tutoringHistoryCount = $sessions.Count
        attemptHistoryCount = $attempts.Count
    }
    $result = [ordered]@{
        summary = $summary
        tutoring = $tutoring
        assessmentTitle = $assessment.title
        gradeFeedback = $grade.feedback
        updatedProfileDimensions = $grade.updatedProfile.dimensions
        events = $events
    }
    $resultPath = Join-Path $ArtifactDir "demo-learning-loop-result.json"
    Repair-Utf8Mojibake $result | ConvertTo-Json -Depth 30 | Set-Content -Encoding UTF8 $resultPath

    $summary | ConvertTo-Json -Depth 8
    Write-Host "Demo artifact: $resultPath"
} catch {
    Write-Host "Demo failed: $($_.Exception.Message)"
    if (Test-Path $BackendErr) {
        Write-Host "Backend stderr tail:"
        Get-Content $BackendErr -Tail 40
    }
    if (Test-Path $PythonErr) {
        Write-Host "Python stderr tail:"
        Get-Content $PythonErr -Tail 30
    }
    throw
} finally {
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-ProcessTree -ProcessId $backendProcess.Id
    }
    if ($pythonProcess -and -not $pythonProcess.HasExited) {
        Stop-ProcessTree -ProcessId $pythonProcess.Id
    }
    if ($oldJavaHome -ne $null) {
        $env:JAVA_HOME = $oldJavaHome
    }
    if ($oldSpringJson -ne $null) {
        $env:SPRING_APPLICATION_JSON = $oldSpringJson
    } else {
        Remove-Item Env:SPRING_APPLICATION_JSON -ErrorAction SilentlyContinue
    }
}
