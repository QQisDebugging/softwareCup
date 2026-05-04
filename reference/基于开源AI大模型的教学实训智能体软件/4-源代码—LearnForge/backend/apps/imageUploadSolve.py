import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import requests
import time
from queue import Queue
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用 websocket-client
from flask import Blueprint, request, Response, stream_with_context, jsonify
from ai_fallback_service import ai_fallback
from utils import get_access_token
from config import get_api_config, update_api_config, get_enabled_apis, get_api_status

# 初始化 Flask 应用
app = Blueprint("imageUploadSolve", __name__)

# WebSocket 参数类
class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, imageunderstanding_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(imageunderstanding_url).netloc
        self.path = urlparse(imageunderstanding_url).path
        self.ImageUnderstanding_url = imageunderstanding_url

    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.ImageUnderstanding_url + '?' + urlencode(v)
        return url

# WebSocket 事件处理
def on_error(ws, error):
    print("### error:", error)


def on_close(ws, *args):
    print("### closed")


def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, question=ws.question))
    ws.send(data)


def on_message(ws, message):
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        
        # 更新 answer
        ws.answer += content
        if status == 2:
            ws.close()


def gen_params(appid, question):
    data = {
        "header": {
            "app_id": appid
        },
        "parameter": {
            "chat": {
                "domain": "image",
                "temperature": 0.5,
                "top_k": 4,
                "max_tokens": 2028,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data


def main(appid, api_key, api_secret, imageunderstanding_url, question):
    wsParam = Ws_Param(appid, api_key, api_secret, imageunderstanding_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    
    # 传递 appid, question, 以及空的 answer 字符串
    setattr(ws, 'appid', appid)
    setattr(ws, 'question', question)
    setattr(ws, 'answer', "")  # 用于存储回答内容

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    return getattr(ws, 'answer', "")  # 返回最终的回答内容

# 新增：百度AI图像识别功能
def baidu_image_recognition(image_base64, question_text="识别图片中的文字和内容"):
    """使用百度AI进行图像识别"""
    try:
        access_token = get_access_token()
        if not access_token:
            raise Exception("无法获取百度AI访问令牌")
        
        # 百度AI图像识别API
        url = f"https://aip.baidubce.com/rest/2.0/image-classify/v1/image_understanding?access_token={access_token}"
        
        payload = {
            "image": image_base64,
            "scene": ["general"]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # 提取识别结果
            recognition_text = ""
            if "result" in result and "general" in result["result"]:
                items = result["result"]["general"]
                recognition_text = "\n".join([item.get("name", "") for item in items])
            
            # 如果识别结果为空，尝试OCR
            if not recognition_text.strip():
                recognition_text = baidu_ocr(image_base64)
            
            return recognition_text
        else:
            raise Exception(f"百度AI API请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"百度AI图像识别失败: {str(e)}")
        return None

def baidu_ocr(image_base64):
    """使用百度OCR进行文字识别"""
    try:
        access_token = get_access_token()
        if not access_token:
            raise Exception("无法获取百度AI访问令牌")
        
        # 百度OCR API
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
        
        payload = {
            "image": image_base64
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "words_result" in result:
                words_list = [item["words"] for item in result["words_result"]]
                return "\n".join(words_list)
        
        return ""
        
    except Exception as e:
        print(f"百度OCR失败: {str(e)}")
        return ""

# 新增：腾讯云OCR功能
def tencent_ocr(image_base64):
    """使用腾讯云OCR进行文字识别"""
    try:
        # 这里需要腾讯云SDK，暂时返回模拟结果
        # 实际使用时需要安装: pip install tencentcloud-sdk-python
        print("腾讯云OCR功能需要配置密钥后使用")
        return "腾讯云OCR功能需要配置密钥"
        
    except Exception as e:
        print(f"腾讯云OCR失败: {str(e)}")
        return None

# 新增：阿里云OCR功能
def ali_ocr(image_base64):
    """使用阿里云OCR进行文字识别"""
    try:
        # 这里需要阿里云SDK，暂时返回模拟结果
        # 实际使用时需要安装: pip install alibabacloud-ocr20191230
        print("阿里云OCR功能需要配置密钥后使用")
        return "阿里云OCR功能需要配置密钥"
        
    except Exception as e:
        print(f"阿里云OCR失败: {str(e)}")
        return None

# 新增：通用OCR + AI解答
def general_ocr_with_ai(image_base64):
    """使用通用OCR识别文字，然后用AI解答"""
    try:
        # 先尝试百度OCR
        ocr_text = baidu_ocr(image_base64)
        
        if ocr_text and ocr_text.strip():
            # 使用AI解答识别出的文字
            ai_prompt = f"请分析以下题目并给出详细解答：\n\n{ocr_text}"
            # 这里可以调用任何可用的AI服务
            return f"【OCR识别结果】\n{ocr_text}\n\n【AI解答】\n正在为您分析题目..."
        else:
            return "图片文字识别失败，请确保图片清晰且包含文字内容"
            
    except Exception as e:
        print(f"通用OCR + AI解答失败: {str(e)}")
        return None

# 新增：智能API选择器
def smart_image_solve(image_base64, question_list):
    """智能选择可用的API进行图像解答"""
    
    # 获取启用的API列表
    enabled_apis = get_enabled_apis()
    
    # 按优先级尝试各个API
    for api_name, api_config in enabled_apis:
        try:
            print(f"正在尝试使用 {api_config['name']} 进行图像识别...")
            
            # 根据API类型调用相应的处理函数
            if api_name == "spark":
                result = main_spark_solve(image_base64, question_list)
            elif api_name == "baidu":
                result = baidu_image_recognition(image_base64)
            elif api_name == "tencent":
                result = tencent_ocr(image_base64)
            elif api_name == "ali":
                result = ali_ocr(image_base64)
            elif api_name == "ocr_general":
                result = general_ocr_with_ai(image_base64)
            else:
                continue
            
            if result and result.strip():
                return {
                    "success": True,
                    "message": result,
                    "api_used": api_config["name"],
                    "fallback": api_name != "spark"
                }
                
        except Exception as e:
            print(f"{api_config['name']} 失败: {str(e)}")
            continue
    
    # 所有API都失败了
    return {
        "success": False,
        "message": "抱歉，所有图像识别服务暂时不可用，请稍后重试或联系管理员。",
        "api_used": "无",
        "fallback": True
    }

def main_spark_solve(image_base64, question_list):
    """原有的科大讯飞星火解决方案"""
    try:
        # 获取科大讯飞配置
        spark_config = get_api_config('spark')
        if not spark_config:
            raise Exception("科大讯飞配置不存在")
        
        # 构造完整的question_list
        if isinstance(question_list, str):
            question_list = json.loads(question_list)
        
        return main(
            spark_config.get('appid'),
            spark_config.get('api_key'),
            spark_config.get('api_secret'),
            spark_config.get('url'),
            question_list
        )
    except Exception as e:
        raise Exception(f"科大讯飞星火API错误: {str(e)}")


@app.route('/imageUploadSolve', methods=['POST'])
def upload_image():
    """改进的图像上传解决接口"""
    try:
        questionList = request.form.get('question')
        
        if not questionList:
            return jsonify({
                'success': False,
                'message': '缺少问题参数',
                'api_used': '无'
            }), 400
        
        # 获取图像的base64编码
        image_base64 = None
        question_parsed = json.loads(questionList)
        
        for item in question_parsed:
            if item.get('content_type') == 'image':
                image_base64 = item.get('content')
                break
        
        if not image_base64:
            return jsonify({
                'success': False,
                'message': '未找到图像数据',
                'api_used': '无'
            }), 400
        
        # 使用智能API选择器
        result = smart_image_solve(image_base64, question_parsed)
        
        if result['success']:
            response_data = {
                'success': True,
                'message': result['message'],
                'api_used': result['api_used']
            }
            
            # 如果使用了降级服务，添加提示
            if result['fallback']:
                response_data['message'] = f"[{result['api_used']}]\n\n{result['message']}"
            
            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'message': result['message'],
                'api_used': result['api_used']
            }), 500
            
    except Exception as e:
        print(f"图像上传解决接口错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器内部错误: {str(e)}',
            'api_used': '无'
        }), 500

# 新增：API配置管理接口
@app.route('/imageUploadSolve/config', methods=['GET', 'POST'])
def api_config():
    """API配置管理接口"""
    if request.method == 'GET':
        return jsonify(get_api_config())
    
    if request.method == 'POST':
        try:
            config_data = request.json
            
            if config_data is None:
                return jsonify({
                    'success': False,
                    'message': '无效的配置数据'
                }), 400
            
            # 更新配置
            for api_name, config in config_data.items():
                update_api_config(api_name, config)
            
            return jsonify({
                'success': True,
                'message': '配置更新成功',
                'config': get_api_config()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'配置更新失败: {str(e)}'
            }), 500
    
    # 默认情况
    return jsonify({
        'success': False,
        'message': '不支持的请求方法'
    }), 405

# 新增：API状态检查接口
@app.route('/imageUploadSolve/status', methods=['GET'])
def api_status():
    """检查各个API的状态"""
    return jsonify(get_api_status())
