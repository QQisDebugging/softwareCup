# 智学工坊运行说明

## 环境要求

- Windows 10/11 或兼容 PowerShell 的环境。
- JDK 21：可通过系统 `PATH` 找到 `java.exe`，或设置 `JAVA_HOME`。
- Python 3.11+：用于启动多智能体资源生成服务。
- 讯飞星火密钥：正式评审必须配置，不能使用本地兜底作为最终效果。

## 密钥配置

复制 `.env.example` 为 `.env`，填写以下任一组配置：

```powershell
XFYUN_API_PASSWORD=你的APIPassword
```

或：

```powershell
XFYUN_API_KEY=你的APIKey
XFYUN_API_SECRET=你的APISecret
```

可选限额配置：

```powershell
XFYUN_DAILY_CALL_LIMIT=20
XFYUN_CACHE_ENABLED=true
```

## 启动

在本目录打开 PowerShell：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\start-zhixue-workshop.ps1
```

启动后访问：

```text
http://localhost:5173/
```

默认账号：

- 学生：`zhang.student` / `student@2026`
- 教师：`li.teacher` / `teacher@2026`

## 停止

```powershell
.\stop-zhixue-workshop.ps1
```

## 服务端口

- 前端：`http://localhost:5173/`
- 后端：`http://localhost:8080/api/health`
- 多智能体服务：`http://localhost:9001/health`

## 常见问题

- 如果提示找不到 Java，请安装 JDK 21 或设置 `JAVA_HOME`。
- 如果首次启动智能体较慢，是因为 Python 虚拟环境正在安装依赖。
- 如果资源生成报讯飞密钥错误，请检查 `.env` 中的密钥是否填写完整。
