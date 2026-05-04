# Resource Agent

资源生成智能体服务，供 Spring Boot 后端通过 HTTP 调用。

```powershell
cd agents/resource-agent
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

当前默认是 `mock` 生成器，用来先跑通后端任务链路。比赛版本应在这里接入科大讯飞星火 API，并保留同样的 `/agents/resource-generation` 契约，避免后端反复改接口。
