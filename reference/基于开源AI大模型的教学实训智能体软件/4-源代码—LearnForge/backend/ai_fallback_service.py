#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI服务降级处理模块
当讯飞星火等主要服务不可用时，自动降级到百度AI服务
"""

import json
import requests
from flask import Response, jsonify
from utils import get_access_token
import time

class AIFallbackService:
    """AI服务降级处理类"""
    
    def __init__(self):
        self.baidu_base_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_speed"
    
    def get_baidu_headers(self):
        """获取百度AI请求头"""
        return {'Content-Type': 'application/json'}
    
    def get_baidu_url(self):
        """获取百度AI完整URL"""
        access_token = get_access_token()
        if not access_token:
            raise Exception("无法获取百度AI访问令牌")
        return f"{self.baidu_base_url}?access_token={access_token}"
    
    def fallback_stream_response(self, prompt, service_name="AI服务"):
        """
        降级到百度AI的流式响应
        """
        try:
            url = self.get_baidu_url()
            payload = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            headers = self.get_baidu_headers()
            
            response = requests.post(url, headers=headers, data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json().get('result', '')
                
                def generate():
                    # 先提示用户正在使用降级服务
                    yield f"[{service_name}暂时不可用，正在使用百度AI服务...]\n\n"
                    time.sleep(0.1)
                    
                    # 逐字符输出结果，模拟流式效果
                    for char in result:
                        yield char
                        time.sleep(0.02)
                
                return Response(generate(), mimetype='text/plain')
            else:
                def generate():
                    yield f"抱歉，AI服务暂时不可用，请稍后再试。(错误码: {response.status_code})"
                
                return Response(generate(), mimetype='text/plain')
                
        except Exception as e:
            print(f"降级服务也失败: {str(e)}")
            
            def generate():
                yield "抱歉，所有AI服务暂时不可用，请稍后再试。"
            
            return Response(generate(), mimetype='text/plain')
    
    def fallback_json_response(self, prompt, service_name="AI服务"):
        """
        降级到百度AI的JSON响应
        """
        try:
            url = self.get_baidu_url()
            payload = json.dumps({
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            })
            headers = self.get_baidu_headers()
            
            response = requests.post(url, headers=headers, data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json().get('result', '')
                return jsonify({
                    "result": f"[{service_name}暂时不可用，以下是备用AI服务的回答]\n\n{result}",
                    "fallback": True,
                    "original_service": service_name
                }), 200
            else:
                return jsonify({
                    "error": f"{service_name}和备用服务都不可用",
                    "details": response.text,
                    "fallback": True
                }), 500
                
        except Exception as e:
            print(f"降级服务失败: {str(e)}")
            return jsonify({
                "error": "所有AI服务暂时不可用",
                "details": str(e),
                "fallback": True
            }), 500

# 创建全局实例
ai_fallback = AIFallbackService()

def spark_ask_with_fallback(query):
    """讯飞星火对话 - 带降级功能"""
    prompt = f"你现在扮演一个资深代码专家，接下来请用富有教育意味的口吻和用户对话。使用markdown格式输出。\n\n用户问题：{query}"
    return ai_fallback.fallback_stream_response(prompt, "讯飞星火")

def spark_ques_analyse_with_fallback(ques, mycode):
    """讯飞星火题目分析 - 带降级功能"""
    prompt = f"""
    题目内容如下：
    {ques}
    
    为了解答这个问题，我编写了以下代码：
    {mycode}
    
    对于解决这个问题，请判断我的代码对不对，如果不对，请给出详细的解决方案，如果大致符合题目的要求，则判定题目通过，你可以夸奖一下我。
    """
    return ai_fallback.fallback_stream_response(prompt, "讯飞星火题目分析")

def spark_generate_problem_with_fallback(demand):
    """讯飞星火问题生成 - 带降级功能"""
    prompt = f"根据这个要求：{demand}，设计一个场景化的编程题，需要有具体的情境，要求，只需要生成题目即可。"
    return ai_fallback.fallback_stream_response(prompt, "讯飞星火问题生成")

def spark_sql_generate_with_fallback(table_struct, question):
    """讯飞星火SQL生成 - 带降级功能"""
    prompt = f"你是一个sql专家，请简明扼要的回答我提出的sql问题。数据库表如下: {table_struct} 请依据上述数据表字段，字段类型以及表之间的关系，结合问题，生成sql查询语句。 问题：{question}"
    return ai_fallback.fallback_json_response(prompt, "讯飞星火SQL生成")

def spark_generate_contest_with_fallback(info, query, contest_type, count):
    """讯飞星火竞赛生成 - 带降级功能"""
    prompt = f"""
    你是一个优秀的中文出题助手，你的任务是根据下述给定的已知信息为用户出给定题目数量的题。
    比如题目类型是选择题，题目数量是3，那么你就帮用户出3道选择题，并且每道题的都要给出正确答案，以此类推。
    确保出的题目必须与用户要求、题目类型、题目数量的相符。不要胡编乱造，不要有无关的符号。
    
    已知信息: {info}
    用户要求: {query}
    题目类型: {contest_type}
    题目数量: {count}
    
    请用中文表达，输出格式化的JSON格式。
    """
    return ai_fallback.fallback_json_response(prompt, "讯飞星火竞赛生成") 