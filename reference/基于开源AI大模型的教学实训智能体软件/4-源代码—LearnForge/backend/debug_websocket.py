#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import threading
import json
import websocket
import base64
import hmac
import hashlib
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time
from config import get_api_config

def debug_websocket_connection():
    """调试WebSocket连接问题"""
    print("=== WebSocket连接调试 ===")
    
    # 获取配置
    spark_config = get_api_config('spark_text')
    print(f"配置检查: {spark_config}")
    
    if not spark_config:
        print("❌ 无法获取配置")
        return
    
    # 创建WebSocket连接URL
    appid = spark_config.get('appid')
    api_key = spark_config.get('api_key')
    api_secret = spark_config.get('api_secret')
    spark_url = spark_config.get('websocket_url')
    
    print(f"AppID: {appid}")
    print(f"API Key: {api_key}")
    print(f"WebSocket URL: {spark_url}")
    
    # 生成认证URL
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    
    parsed_url = urlparse(spark_url)
    host = parsed_url.hostname
    path = parsed_url.path
    
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'), hashlib.sha256).digest()
    signature_sha_str = base64.b64encode(signature_sha).decode('utf-8')
    
    authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_str}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    params = {
        'authorization': authorization,
        'date': date,
        'host': host
    }
    
    final_url = f"{spark_url}?{urlencode(params)}"
    print(f"最终URL: {final_url[:100]}...")
    
    # 测试连接
    connection_successful = False
    messages_received = []
    
    def on_open(ws):
        print("✅ WebSocket连接打开")
        nonlocal connection_successful
        connection_successful = True
        
        # 发送测试消息
        test_message = {
            "header": {
                "app_id": appid,
                "uid": "debug_test"
            },
            "parameter": {
                "chat": {
                    "domain": spark_config.get('domain'),
                    "temperature": 0.8,
                    "max_tokens": 1024,
                    "top_k": 5,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": "这是一个连接测试，请回答OK"}
                    ]
                }
            }
        }
        
        print(f"发送测试消息: {json.dumps(test_message, ensure_ascii=False)}")
        ws.send(json.dumps(test_message))
    
    def on_message(ws, message):
        print(f"收到消息: {message}")
        try:
            data = json.loads(message)
            messages_received.append(data)
            
            # 检查错误
            if data.get('header', {}).get('code') != 0:
                print(f"❌ 错误代码: {data['header']['code']}")
                print(f"❌ 错误信息: {data['header'].get('message', '未知错误')}")
                ws.close()
                return
            
            # 检查状态
            status = data.get('header', {}).get('status', 0)
            if status == 2:
                print("✅ 对话结束")
                ws.close()
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
    
    def on_error(ws, error):
        print(f"❌ WebSocket错误: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print(f"🔒 WebSocket关闭: {close_status_code} - {close_msg}")
    
    # 创建WebSocket连接
    ws = websocket.WebSocketApp(
        final_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # 启动连接
    print("正在连接WebSocket...")
    ws.run_forever(sslopt={"cert_reqs": __import__('ssl').CERT_NONE})
    
    # 结果分析
    print("\n=== 连接结果分析 ===")
    print(f"连接成功: {connection_successful}")
    print(f"收到消息数: {len(messages_received)}")
    
    if messages_received:
        print("收到的消息:")
        for i, msg in enumerate(messages_received):
            print(f"  消息 {i+1}: {json.dumps(msg, ensure_ascii=False, indent=2)}")
    else:
        print("没有收到任何消息")
    
    return connection_successful, messages_received

def test_api_endpoint():
    """测试API端点响应"""
    print("\n=== API端点测试 ===")
    
    test_data = {
        "query": "这是一个快速测试，请回答OK"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:5000/api/spark/ask',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        end_time = time.time()
        
        print(f"响应时间: {end_time - start_time:.2f}秒")
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)} 字符")
        
        if response.status_code == 200:
            response_text = response.text
            print(f"响应内容前200字符: {response_text[:200]}...")
            
            # 检查是否使用降级服务
            using_fallback = "[讯飞星火响应超时，正在使用备用服务...]" in response_text
            print(f"使用降级服务: {using_fallback}")
            
            return not using_fallback
        else:
            print(f"❌ 请求失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    print("开始WebSocket连接调试...")
    
    # 1. 测试直接WebSocket连接
    ws_success, messages = debug_websocket_connection()
    
    # 2. 测试API端点
    api_success = test_api_endpoint()
    
    # 3. 总结
    print("\n=== 调试总结 ===")
    print(f"WebSocket直连成功: {ws_success}")
    print(f"API端点正常: {api_success}")
    
    if ws_success and not api_success:
        print("🔍 WebSocket连接正常，但API端点有问题")
    elif not ws_success and api_success:
        print("🔍 API端点正常，但WebSocket连接有问题")
    elif ws_success and api_success:
        print("🎉 所有测试都通过了")
    else:
        print("❌ 所有测试都失败了") 