#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API配置管理文件
用于管理各种第三方API的配置信息
"""

import os
import json
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / 'api_config.json'

# 默认API配置
DEFAULT_API_CONFIG = {
    "spark": {
        "enabled": True,
        "priority": 1,
        "name": "科大讯飞星火",
        "appid": os.getenv("XF_APP_ID", ""),
        "api_secret": os.getenv("XF_API_SECRET", ""),
        "api_key": os.getenv("XF_API_KEY", ""),
        "url": "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"
    },
    "spark_text": {
        "enabled": True,
        "priority": 1,
        "name": "科大讯飞星火文本",
        "appid": os.getenv("XF_APP_ID", ""),
        "api_secret": os.getenv("XF_API_SECRET", ""),
        "api_key": os.getenv("XF_API_KEY", ""),
        "websocket_url": "wss://spark-api.xf-yun.com/v1/x1",
        "http_url": "https://spark-api-open.xf-yun.com/v2/chat/completions",
        "domain": "x1"
    },
    "baidu": {
        "enabled": True,
        "priority": 2,
        "name": "百度AI图像识别",
        "api_key": os.getenv("BAIDU_API_KEY", ""),
        "secret_key": os.getenv("BAIDU_SECRET_KEY", ""),
        "ocr_url": "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic",
        "image_url": "https://aip.baidubce.com/rest/2.0/image-classify/v1/image_understanding"
    },
    "tencent": {
        "enabled": False,
        "priority": 3,
        "name": "腾讯云OCR",
        "secret_id": os.getenv("TENCENT_SECRET_ID", ""),
        "secret_key": os.getenv("TENCENT_SECRET_KEY", ""),
        "region": "ap-beijing",
        "url": "https://ocr.tencentcloudapi.com"
    },
    "ali": {
        "enabled": False,
        "priority": 4,
        "name": "阿里云OCR",
        "access_key_id": os.getenv("ALI_ACCESS_KEY_ID", ""),
        "access_key_secret": os.getenv("ALI_ACCESS_KEY_SECRET", ""),
        "endpoint": "https://ocr.cn-shanghai.aliyuncs.com",
        "region": "cn-shanghai"
    },
    "ocr_general": {
        "enabled": True,
        "priority": 5,
        "name": "通用OCR+AI解答",
        "description": "使用OCR识别文字后由AI解答，作为最后的备用方案"
    }
}

class APIConfigManager:
    """API配置管理器"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置，确保新增的配置项不丢失
                merged_config = DEFAULT_API_CONFIG.copy()
                for api_name, api_config in config.items():
                    if api_name in merged_config:
                        merged_config[api_name].update(api_config)
                return merged_config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return DEFAULT_API_CONFIG.copy()
        else:
            # 创建默认配置文件
            self.save_config(DEFAULT_API_CONFIG)
            return DEFAULT_API_CONFIG.copy()
    
    def save_config(self, config=None):
        """保存配置到文件"""
        try:
            config_to_save = config if config else self.config
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_config(self, api_name=None):
        """获取配置"""
        if api_name:
            return self.config.get(api_name)
        return self.config
    
    def update_config(self, api_name, updates):
        """更新配置"""
        if api_name in self.config:
            self.config[api_name].update(updates)
            return self.save_config()
        return False
    
    def get_enabled_apis(self):
        """获取启用的API列表（按优先级排序）"""
        enabled_apis = []
        for api_name, config in self.config.items():
            if config.get('enabled', False):
                enabled_apis.append((api_name, config))
        
        # 按优先级排序
        enabled_apis.sort(key=lambda x: x[1].get('priority', 999))
        return enabled_apis
    
    def is_api_configured(self, api_name):
        """检查API是否已正确配置"""
        config = self.get_config(api_name)
        if not config or not config.get('enabled', False):
            return False
        
        # 检查必要的配置项
        if api_name == 'spark':
            return all([
                config.get('appid'),
                config.get('api_secret'),
                config.get('api_key')
            ])
        elif api_name == 'spark_text':
            return all([
                config.get('appid'),
                config.get('api_secret'),
                config.get('api_key')
            ])
        elif api_name == 'baidu':
            return True  # 百度使用全局token，不需要检查
        elif api_name == 'tencent':
            return all([
                config.get('secret_id'),
                config.get('secret_key')
            ])
        elif api_name == 'ali':
            return all([
                config.get('access_key_id'),
                config.get('access_key_secret')
            ])
        elif api_name == 'ocr_general':
            return True  # 通用OCR总是可用
        
        return False
    
    def get_api_status(self):
        """获取所有API的状态"""
        status = {}
        for api_name, config in self.config.items():
            is_configured = self.is_api_configured(api_name)
            status[api_name] = {
                'name': config.get('name', api_name),
                'enabled': config.get('enabled', False),
                'priority': config.get('priority', 999),
                'configured': is_configured,
                'status': '可用' if is_configured else ('需要配置' if config.get('enabled', False) else '已禁用')
            }
        return status

# 全局配置管理器实例
config_manager = APIConfigManager()

# 便捷函数
def get_api_config(api_name=None):
    """获取API配置"""
    return config_manager.get_config(api_name)

def update_api_config(api_name, updates):
    """更新API配置"""
    return config_manager.update_config(api_name, updates)

def get_enabled_apis():
    """获取启用的API列表"""
    return config_manager.get_enabled_apis()

def get_api_status():
    """获取API状态"""
    return config_manager.get_api_status() 
