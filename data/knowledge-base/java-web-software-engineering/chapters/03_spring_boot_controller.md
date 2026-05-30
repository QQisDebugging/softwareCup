# 第三章 Spring Boot 项目结构与 Controller

## 学习目标

- 理解 Spring Boot 应用入口和常见目录结构。
- 掌握 Controller、DTO、Validation 的基本使用。
- 能够实现简单的 REST 接口。

## 先修知识

- Java 类与方法
- HTTP 和 JSON 基础

## 核心概念

- Spring Boot
- Controller
- DTO
- Validation

## 关键知识点

- Controller 负责接收 HTTP 请求并返回响应。
- DTO 用于表达接口输入输出，避免实体对象直接暴露给前端。
- Validation 用于在入口层校验请求参数。
- Service 层承载业务逻辑，Controller 不应堆积复杂业务。

## 示例场景

实现 `GET /api/health` 和 `POST /api/courses`，让学生理解从请求到响应的基本链路。

## 常见错误

- Controller 中直接写数据库操作。
- 请求参数缺少校验。
- 返回实体对象导致接口契约不稳定。

## 实操任务

- 实现健康检查接口。
- 实现课程创建接口的 Controller 和请求 DTO。

## 适合的学生画像

- 初学者适合从健康检查接口开始。
- 工程实践型学生适合做分层重构练习。

## 推荐资源类型

- Controller 示例代码
- 分层结构图
- 参数校验练习

## 测评建议

- 检查学生是否能解释 Controller、DTO、Service 的职责边界。
