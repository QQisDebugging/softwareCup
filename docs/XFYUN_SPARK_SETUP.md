# 讯飞星火 API 接入与验收说明

本项目正式展示、答辩录屏和线上评测必须使用科大讯飞星火 API。页面不要展示“本地兜底/替代模型”等状态；技术验收以服务状态接口和智能体真实调用结果为准。

官方 HTTP 文档给出的星火语言模型调用地址是：

- Chat Completions: `https://spark-api-open.xf-yun.com/v1/chat/completions`
- OpenAI 兼容 `base_url`: `https://spark-api-open.xf-yun.com/v1/`
- OpenAI 兼容鉴权字段：控制台获取的 `APIPassword`

官方可定制化 API 还支持垂类场景、RAG、联网搜索和知识问答；其中知识库能力包含创建知识库、上传文件并在内容中传入 `file_id` 进行问答。后续做课程知识库增强时，应优先沿用同一讯飞应用的星火知识库/文件提取能力。

## 需要申请或确认的内容

1. 讯飞开放平台账号，并完成平台要求的认证。
2. 在控制台创建应用，开通星火大模型 API。
3. 优先获取 `APIPassword`，用于 OpenAI 兼容 HTTP 调用。
4. 如果控制台只给旧版凭据，则获取 `APPID`、`APIKey`、`APISecret`。
5. 如果要做 OCR 题目解析、语音合成、语音评测、知识库问答等加分能力，继续在同一应用或对应服务页开通 OCR/TTS/语音评测/星火知识库权限。

题目说明文件只写明命题单位为科大讯飞，并提供了 QQ 群 `1072584310`；没有明确写“比赛统一发放 API key”。需要在比赛群或官方答疑里确认是否提供额度、是否限制模型版本、是否要求使用指定应用。若比赛提供统一 key，以比赛 key 为最高优先级。

## 本地配置

在 PowerShell 里配置环境变量后重启 Python 智能体服务：

```powershell
$env:SOFTWARECUP_AGENT_PROVIDER='xfyun_spark'
$env:RESOURCE_AGENT_PROVIDER='xfyun_spark'
$env:XFYUN_APP_ID='你的 AppID'
$env:XFYUN_API_PASSWORD='你的 APIPassword'
$env:XFYUN_MODEL='generalv3.5'
$env:XFYUN_ENDPOINT='https://spark-api-open.xf-yun.com/v1/chat/completions'
$env:XFYUN_CACHE_ENABLED='true'
$env:XFYUN_DAILY_CALL_LIMIT='20'
```

如果只有旧版 `APIKey/APISecret`：

```powershell
$env:SOFTWARECUP_AGENT_PROVIDER='xfyun_spark'
$env:RESOURCE_AGENT_PROVIDER='xfyun_spark'
$env:XFYUN_APP_ID='你的 AppID'
$env:XFYUN_API_KEY='你的 APIKey'
$env:XFYUN_API_SECRET='你的 APISecret'
$env:XFYUN_MODEL='generalv3.5'
```

## 额度保护

当前 Python 智能体会对完全相同的模型、接口、system prompt 和 user prompt 做本地缓存，默认目录为：

```text
D:\softwareCup\.cache\xfyun-spark
```

默认每日最多真实调用 20 次讯飞接口，命中缓存不计入调用次数。需要调整时只改本地环境变量：

```powershell
$env:XFYUN_CACHE_ENABLED='true'
$env:XFYUN_CACHE_DIR='.cache/xfyun-spark'
$env:XFYUN_DAILY_CALL_LIMIT='20'
```

比赛调试时建议保持缓存开启；只有在你确认要消耗额度重新生成时，再修改 prompt 或清理对应缓存文件。

然后启动或重启 Python 智能体服务：

```powershell
cd D:\softwareCup\agents\resource-agent
.\.venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 9001 --reload
```

## 验证

```powershell
curl.exe http://localhost:9001/agents/providers/status
curl.exe http://localhost:8080/api/agents/providers/status
```

正式接入成功时应看到：

- `configuredProvider`: `xfyun_spark`
- `activeProvider`: `xfyun_spark`
- `xfyunConfigured`: `true`
- `xfyunCredentialMode`: `APIPassword` 或 `APIKey/APISecret`
- `xfyunModel`: 当前模型名
- `xfyunCacheEnabled`: `true`
- `xfyunTodayCalls`: 当日本机真实调用次数
- `xfyunDailyCallLimit`: 当日本机调用上限
- `lastError`: 空字符串或无错误

当前机器如果没有配置密钥，状态接口会出现：

- `xfyunConfigured`: `false`
- `xfyunCredentialMode`: `not_configured`
- `lastError`: `XFYUN_API_PASSWORD or XFYUN_API_KEY/XFYUN_API_SECRET are not configured.`

这只说明本机还没有密钥，不能作为正式展示状态。你申请到字段后按变量名配置到本机环境，或者只告诉我变量已经配好，我会直接重启服务并验证。

## 需要你申请后提供的字段

优先给这一组：

```text
XFYUN_APP_ID
XFYUN_API_PASSWORD
XFYUN_MODEL
```

如果控制台没有 `APIPassword`，给这一组：

```text
XFYUN_APP_ID
XFYUN_API_KEY
XFYUN_API_SECRET
XFYUN_MODEL
```

真实密钥不要写进 Git，不要发公开截图，不要发到群里；只在本机环境变量或本地未提交的 `.env` 中配置。
