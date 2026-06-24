param(
    [string]$PackageName = "智学工坊-参赛提交包"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$OutRoot = Join-Path $RepoRoot "output\competition-package\$PackageName-$Stamp"
$RuntimeRoot = Join-Path $OutRoot "1-作品安装包或可执行文件\智学工坊-runtime"
$SourceRoot = Join-Path $OutRoot "2-作品源码"
$DocsRoot = Join-Path $OutRoot "3-作品PPT演示视频文档"

New-Item -ItemType Directory -Force -Path $RuntimeRoot, $SourceRoot, $DocsRoot | Out-Null

Copy-Item -LiteralPath (Join-Path $RepoRoot "backend\target\backend-0.0.1-SNAPSHOT.jar") -Destination (New-Item -ItemType Directory -Force -Path (Join-Path $RuntimeRoot "backend")) -Force
Rename-Item -LiteralPath (Join-Path $RuntimeRoot "backend\backend-0.0.1-SNAPSHOT.jar") -NewName "backend.jar" -Force

Copy-Item -LiteralPath (Join-Path $RepoRoot "frontend\dist") -Destination (Join-Path $RuntimeRoot "frontend") -Recurse -Force

$AgentDest = Join-Path $RuntimeRoot "agent"
robocopy (Join-Path $RepoRoot "agents\resource-agent") $AgentDest /E /XD ".venv" "__pycache__" ".cache" /XF "*.log" | Out-Null
if ($LASTEXITCODE -gt 7) { throw "robocopy agent failed with code $LASTEXITCODE" }

Copy-Item -LiteralPath (Join-Path $RepoRoot "data") -Destination (Join-Path $RuntimeRoot "data") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot ".env.example") -Destination (Join-Path $RuntimeRoot ".env.example") -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "scripts\competition-runtime\serve-spa.ps1") -Destination $RuntimeRoot -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "scripts\competition-runtime\start-zhixue-workshop.ps1") -Destination $RuntimeRoot -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "scripts\competition-runtime\stop-zhixue-workshop.ps1") -Destination $RuntimeRoot -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "scripts\competition-runtime\README_运行说明.md") -Destination $RuntimeRoot -Force

$SourceStage = Join-Path $SourceRoot "智学工坊-source"
New-Item -ItemType Directory -Force -Path $SourceStage | Out-Null

$SourceDirectories = @(
    "backend\src",
    "backend\.mvn",
    "frontend\src",
    "frontend\.storybook",
    "agents\resource-agent",
    "docs",
    "scripts",
    "data"
)

foreach ($RelativeDir in $SourceDirectories) {
    $SourceDir = Join-Path $RepoRoot $RelativeDir
    if (Test-Path -LiteralPath $SourceDir) {
        $DestDir = Join-Path $SourceStage $RelativeDir
        robocopy $SourceDir $DestDir /E /XD ".venv" "__pycache__" ".cache" "node_modules" "dist" "target" "uploads" "output" /XF "*.log" "*.tmp" "*.pid" | Out-Null
        if ($LASTEXITCODE -gt 7) { throw "robocopy source dir $RelativeDir failed with code $LASTEXITCODE" }
    }
}

$SourceFiles = @(
    ".env.example",
    ".gitattributes",
    ".gitignore",
    "docker-compose.yml",
    "PRODUCT.md",
    "README.md",
    "skills-lock.json",
    "backend\pom.xml",
    "backend\mvnw",
    "backend\mvnw.cmd",
    "backend\.gitattributes",
    "backend\.gitignore",
    "frontend\package.json",
    "frontend\package-lock.json",
    "frontend\index.html",
    "frontend\vite.config.ts",
    "frontend\tsconfig.json",
    "frontend\tsconfig.app.json",
    "frontend\tsconfig.node.json",
    "frontend\env.d.ts",
    "frontend\README.md",
    "frontend\.env.development",
    "frontend\.gitignore"
)

foreach ($RelativeFile in $SourceFiles) {
    $SourceFile = Join-Path $RepoRoot $RelativeFile
    if (Test-Path -LiteralPath $SourceFile) {
        $DestFile = Join-Path $SourceStage $RelativeFile
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $DestFile) | Out-Null
        Copy-Item -LiteralPath $SourceFile -Destination $DestFile -Force
    }
}

$CompetitionDocs = Join-Path $RepoRoot "docs\competition"
Copy-Item -LiteralPath $CompetitionDocs -Destination $DocsRoot -Recurse -Force

$PresentationPdf = Join-Path $CompetitionDocs "presentation\zhixue-workshop.pdf"
if (Test-Path -LiteralPath $PresentationPdf) {
    Copy-Item -LiteralPath $PresentationPdf -Destination (Join-Path $DocsRoot "智学工坊-演示PPT-Beamer-HFUT.pdf") -Force
}

$DocEntrypoints = @()
$DocEntrypoints += [PSCustomObject]@{ Source = "演示视频脚本.md"; Destination = "智学工坊-演示视频脚本.md" }
$DocEntrypoints += [PSCustomObject]@{ Source = "软件使用说明书.md"; Destination = "智学工坊-软件使用说明书.md" }
$DocEntrypoints += [PSCustomObject]@{ Source = "项目设计与开发说明书.md"; Destination = "智学工坊-项目设计与开发说明书.md" }
$DocEntrypoints += [PSCustomObject]@{ Source = "测试说明书.md"; Destination = "智学工坊-测试说明书.md" }
$DocEntrypoints += [PSCustomObject]@{ Source = "AI_Coding工具使用说明.md"; Destination = "智学工坊-AI Coding工具使用说明.md" }
$DocEntrypoints += [PSCustomObject]@{ Source = "开源与第三方工具说明.md"; Destination = "智学工坊-开源与第三方工具说明.md" }

foreach ($Doc in $DocEntrypoints) {
    $SourcePath = Join-Path $CompetitionDocs $Doc.Source
    if (Test-Path -LiteralPath $SourcePath) {
        Copy-Item -LiteralPath $SourcePath -Destination (Join-Path $DocsRoot $Doc.Destination) -Force
    }
}

$RuntimeZip = Join-Path (Split-Path $RuntimeRoot -Parent) "智学工坊-runtime.zip"
$SourceZip = Join-Path $SourceRoot "智学工坊-source.zip"
if (Test-Path -LiteralPath $RuntimeZip) { Remove-Item -LiteralPath $RuntimeZip -Force }
if (Test-Path -LiteralPath $SourceZip) { Remove-Item -LiteralPath $SourceZip -Force }
Compress-Archive -LiteralPath $RuntimeRoot -DestinationPath $RuntimeZip -Force
Compress-Archive -LiteralPath $SourceStage -DestinationPath $SourceZip -Force

$manifest = @(
    "# 智学工坊参赛交付清单",
    "",
    "- 1-作品安装包或可执行文件：包含可执行后端 jar、前端静态文件、多智能体 Python 服务、启动/停止脚本。",
    "- 2-作品源码：包含当前项目源码快照，不包含 reference、node_modules、target、.venv 等大体积生成物。",
    "- 3-作品PPT演示视频文档：包含 Beamer-HFUT 演示文稿、系统文档、测试说明、使用说明、视频脚本。",
    "",
    "生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)
$manifest | Set-Content -LiteralPath (Join-Path $OutRoot "交付清单.md") -Encoding UTF8

Write-Host "Competition package generated at: $OutRoot"
Write-Host "Runtime zip: $RuntimeZip"
Write-Host "Source zip: $SourceZip"
