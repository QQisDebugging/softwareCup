#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import threading
import json
from concurrent.futures import ThreadPoolExecutor

def test_text_api_performance():
    """测试文本API性能"""
    print("=== 讯飞星火文本API性能测试 ===")
    
    test_queries = [
        "你好，请简单介绍一下你自己",
        "1+1等于几？",
        "请解释一下Python的特点",
        "什么是机器学习？",
        "请写一个简单的Python函数"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries):
        print(f"\n测试 {i+1}: {query}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                'http://localhost:5000/api/spark/ask',
                json={'query': query},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                response_text = response.text
                # 计算响应长度
                response_length = len(response_text)
                
                # 检查是否使用了降级服务
                using_fallback = "[讯飞星火响应超时，正在使用备用服务...]" in response_text
                
                results.append({
                    'query': query,
                    'response_time': response_time,
                    'response_length': response_length,
                    'using_fallback': using_fallback,
                    'status': 'success'
                })
                
                print(f"  ✅ 响应时间: {response_time:.2f}秒")
                print(f"  📝 响应长度: {response_length} 字符")
                print(f"  🔄 使用降级服务: {'是' if using_fallback else '否'}")
                
            else:
                results.append({
                    'query': query,
                    'response_time': response_time,
                    'status': 'failed',
                    'error': f"HTTP {response.status_code}"
                })
                print(f"  ❌ 请求失败: HTTP {response.status_code}")
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            results.append({
                'query': query,
                'response_time': response_time,
                'status': 'error',
                'error': str(e)
            })
            print(f"  ❌ 请求异常: {e}")
    
    # 统计结果
    print("\n=== 性能测试结果统计 ===")
    successful_results = [r for r in results if r['status'] == 'success']
    
    if successful_results:
        avg_response_time = sum(r['response_time'] for r in successful_results) / len(successful_results)
        avg_response_length = sum(r['response_length'] for r in successful_results) / len(successful_results)
        fallback_rate = sum(1 for r in successful_results if r['using_fallback']) / len(successful_results)
        
        print(f"✅ 成功请求数: {len(successful_results)}/{len(results)}")
        print(f"⏱️ 平均响应时间: {avg_response_time:.2f}秒")
        print(f"📝 平均响应长度: {avg_response_length:.0f} 字符")
        print(f"🔄 降级服务使用率: {fallback_rate:.1%}")
        
        # 性能建议
        if avg_response_time > 3.0:
            print("⚠️ 平均响应时间较慢，建议优化")
        elif avg_response_time < 1.5:
            print("🚀 响应时间很快，性能良好")
        else:
            print("✅ 响应时间正常")
            
        if fallback_rate > 0.5:
            print("⚠️ 降级服务使用率过高，建议检查主服务")
        elif fallback_rate == 0:
            print("🎉 主服务运行良好，无需降级")
            
    else:
        print("❌ 所有请求都失败了")
    
    return results

def test_concurrent_requests():
    """测试并发请求性能"""
    print("\n=== 并发请求性能测试 ===")
    
    def single_request(query_id):
        start_time = time.time()
        try:
            response = requests.post(
                'http://localhost:5000/api/spark/ask',
                json={'query': f'这是第{query_id}个并发请求，请简单回答'},
                headers={'Content-Type': 'application/json'},
                timeout=8
            )
            end_time = time.time()
            
            return {
                'query_id': query_id,
                'response_time': end_time - start_time,
                'status_code': response.status_code,
                'success': response.status_code == 200
            }
        except Exception as e:
            end_time = time.time()
            return {
                'query_id': query_id,
                'response_time': end_time - start_time,
                'error': str(e),
                'success': False
            }
    
    # 测试2个并发请求（避免QPS限制）
    concurrent_count = 2
    print(f"发送 {concurrent_count} 个并发请求...")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
        futures = [executor.submit(single_request, i+1) for i in range(concurrent_count)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 分析结果
    successful_results = [r for r in results if r['success']]
    avg_response_time = sum(r['response_time'] for r in successful_results) / len(successful_results) if successful_results else 0
    
    print(f"✅ 成功请求数: {len(successful_results)}/{concurrent_count}")
    print(f"⏱️ 总耗时: {total_time:.2f}秒")
    print(f"📊 平均响应时间: {avg_response_time:.2f}秒")
    print(f"🔄 吞吐量: {len(successful_results)/total_time:.1f} 请求/秒")
    
    if len(successful_results) == concurrent_count:
        print("🎉 所有并发请求都成功了")
    else:
        print("⚠️ 有部分并发请求失败")
    
    return results

def performance_recommendations():
    """给出性能优化建议"""
    print("\n=== 性能优化建议 ===")
    
    print("1. 🔧 已应用的优化:")
    print("   - 减少超时时间从10秒到5秒")
    print("   - 优化队列轮询频率到0.05秒")
    print("   - 添加连接状态检查机制")
    print("   - 修复WebSocket消息字段名问题")
    
    print("\n2. 🚀 进一步优化建议:")
    print("   - 考虑使用连接池复用WebSocket连接")
    print("   - 实现智能降级策略")
    print("   - 添加响应缓存机制")
    print("   - 优化队列处理算法")
    
    print("\n3. 📊 监控指标:")
    print("   - 平均响应时间 < 2秒")
    print("   - 降级服务使用率 < 20%")
    print("   - 并发处理能力 > 10 请求/秒")
    print("   - 错误率 < 5%")

if __name__ == "__main__":
    try:
        # 测试文本API性能
        text_results = test_text_api_performance()
        
        # 测试并发请求性能
        concurrent_results = test_concurrent_requests()
        
        # 给出优化建议
        performance_recommendations()
        
        print("\n🎯 性能测试完成！")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}") 