#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def quick_test():
    print("=== 快速性能测试 ===")
    
    test_query = "请简单回答：你好"
    
    print(f"测试查询: {test_query}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            'http://localhost:5000/api/spark/ask',
            json={'query': test_query},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"✅ 响应时间: {response_time:.2f}秒")
        print(f"📝 响应长度: {len(response.text)} 字符")
        
        # 检查是否使用了降级服务
        using_fallback = "[讯飞星火响应超时，正在使用备用服务...]" in response.text
        print(f"🔄 使用降级服务: {'是' if using_fallback else '否'}")
        
        # 显示响应内容的前100个字符
        print(f"📄 响应内容: {response.text[:100]}...")
        
        # 性能评估
        if response_time < 3.0:
            print("🚀 响应速度：很快")
        elif response_time < 8.0:
            print("✅ 响应速度：正常")
        else:
            print("⚠️ 响应速度：较慢")
            
        if not using_fallback:
            print("🎉 主服务工作正常！")
        else:
            print("❌ 仍在使用降级服务")
            
        return not using_fallback
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎯 性能优化成功！")
    else:
        print("\n❌ 仍需进一步优化") 