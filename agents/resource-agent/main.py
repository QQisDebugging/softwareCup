from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field


class Provider(str, Enum):
    MOCK = "mock"
    XFYUN_SPARK = "xfyun_spark"


class ResourceAgentRequest(BaseModel):
    taskId: str
    studentProfileId: str
    courseId: str
    studentProfileSummary: str
    courseTitle: str
    topic: str
    resourceType: str
    modality: str
    prompt: str


class ResourceAgentResponse(BaseModel):
    title: str
    resourceType: str
    modality: str
    targetLevel: str
    estimatedMinutes: int = Field(ge=1)
    content: str
    summary: str


app = FastAPI(title="Software Cup Resource Agent", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {
        "service": "resource-agent",
        "status": "UP",
        "provider": Provider.MOCK,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/agents/resource-generation", response_model=ResourceAgentResponse)
def generate_resource(request: ResourceAgentRequest) -> ResourceAgentResponse:
    return ResourceAgentResponse(
        title=f"{request.topic} - 个性化{request.resourceType}",
        resourceType=request.resourceType,
        modality=request.modality,
        targetLevel="根据学习画像自适应",
        estimatedMinutes=18,
        content=build_mock_content(request),
        summary=f"已围绕 {request.topic} 生成 {request.modality} 形式的学习资源。",
    )


def build_mock_content(request: ResourceAgentRequest) -> str:
    return f"""# {request.topic}

课程：{request.courseTitle}
资源形式：{request.resourceType} / {request.modality}

## 学习画像依据
{request.studentProfileSummary}

## 学习目标
1. 解释 {request.topic} 的核心概念。
2. 能够把概念应用到高校课程项目中的真实任务。
3. 形成可检验的练习输出，便于后续学习效果评估智能体追踪。

## 个性化讲解
{request.prompt}

## 图解脚本
- 画布左侧：学生当前知识点掌握状态。
- 画布中间：{request.topic} 的关键概念和先修关系。
- 画布右侧：推荐练习、测试题和补救资源。

## 练习任务
完成一个 20 分钟小任务：用自己的话总结 {request.topic}，并提交一个能体现理解程度的例子。

## 评估点
- 概念准确性。
- 例子与课程场景的贴合度。
- 是否暴露出需要智能辅导继续补救的薄弱点。
"""
