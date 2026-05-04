# 讯飞接口流式返回模块
import json
import threading
import uuid
import websocket
from queue import Queue
from urllib.parse import urlparse, urlencode
import hmac
import hashlib
import base64
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import ssl
import queue
# 用于存储每个请求队列的字典
doc_connection_queues = {}

class Document_Q_And_A:
    def __init__(self, APPId, APISecret, TimeStamp, OriginUrl):
        self.appId = APPId
        self.apiSecret = APISecret
        self.timeStamp = TimeStamp
        self.originUrl = OriginUrl

    def get_origin_signature(self):
        m2 = hashlib.md5()
        data = bytes(self.appId + self.timeStamp, encoding="utf-8")
        m2.update(data)
        checkSum = m2.hexdigest()
        return checkSum

    def get_signature(self):
        signature_origin = self.get_origin_signature()
        signature = hmac.new(self.apiSecret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha1).digest()
        signature = base64.b64encode(signature).decode(encoding='utf-8')
        return signature

    def get_header(self):
        signature = self.get_signature()
        header = {
            "Content-Type": "application/json",
            "appId": self.appId,
            "timestamp": self.timeStamp,
            "signature": signature
        }
        return header

    def get_url(self):
        signature = self.get_signature()
        return self.originUrl + "?" + f'appId={self.appId}&timestamp={self.timeStamp}&signature={signature}'

    def get_body(self, message, file_ids):
        data = {
            "chatExtends": {
                "wikiPromptTpl": "请将以下内容作为已知信息：\n<wikicontent>\n请根据以上内容回答用户的问题。\n问题:<wikiquestion>\n回答:",
                "wikiFilterScore": 0.83,
                "temperature": 0.5
            },
            "fileIds": file_ids,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
        return data

def on_error_doc(ws, error):
    print("### error:", error)

def on_close_doc(ws, close_status_code, close_msg):
    connection_id = ws.get_id()
    if connection_id in doc_connection_queues:
        del doc_connection_queues[connection_id]
    print("### closed ###")

def on_open_doc(ws):
    data = json.dumps(ws.question)
    ws.send(data)

def on_message_doc(ws, message):
    data = json.loads(message)
    code = data['code']
    connection_id = ws.get_id()
    queue = doc_connection_queues.get(connection_id)
    if not queue:
        return

    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        content = data["content"]
        print(content)
        queue.put(content)  # 将消息放入队列中
        if data["status"] == 2:
            ws.close()

def start_websocket_connection_doc(params, question):
    connection_id = str(uuid.uuid4())  # 生成一个唯一标识符
    doc_param = Document_Q_And_A(params['appid'], params['api_secret'], params['cur_time'], params['origin_url'])
    ws_url = doc_param.get_url()
    queue = Queue()
    doc_connection_queues[connection_id] = queue
    
    ws = websocket.WebSocketApp(ws_url,
                                on_message=lambda ws, msg: on_message_doc(ws, msg),
                                on_error=on_error_doc,
                                on_close=on_close_doc,
                                on_open=on_open_doc)
    ws.question = question
    ws.get_id = lambda: connection_id
    threading.Thread(target=lambda: ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})).start()
    
    return queue

# # 消息队列
# message_queue = Queue()

class Ws_Param:
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        v = {"authorization": authorization, "date": date, "host": self.host}
        url = f"{self.Spark_url}?{urlencode(v)}"
        return url


text = []
def getText(role,content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

# def on_message(ws, message):
#     data = json.loads(message)
#     if data['header']['code'] != 0:
#         print(f'请求错误: {data["header"]["code"]}, {data}')
#         ws.close()
#     else:
#         content = data["payload"]["choices"]["text"][0]["content"]
#         message_queue.put(content)
#         if data["payload"]["choices"]["status"] == 2:
#             ws.close()

def on_error(ws, error):
    print("Error:", error)

# def on_close(ws, close_status_code, close_msg):
#     print("WebSocket closed")

def on_open(ws):
    data = json.dumps(ws.question)
    ws.send(data)

# def start_websocket_connection(params, question):
#     ws_param = Ws_Param(params['appid'], params['api_key'], params['api_secret'], params['spark_url'])
#     ws_url = ws_param.create_url()
#     ws = websocket.WebSocketApp(ws_url,
#                                 on_message=on_message,
#                                 on_error=on_error,
#                                 on_close=on_close,
#                                 on_open=on_open)
#     ws.question = question
#     threading.Thread(target=lambda: ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})).start()


connection_queues = {}

def on_close(ws, close_status_code, close_msg):
    connection_id = ws.get_id()
    if connection_id in connection_queues:
        del connection_queues[connection_id]
    print("WebSocket closed")


def on_message(ws, message):
    connection_id = ws.get_id()  # 确保每个 WebSocket 连接都有唯一的 ID
    queue = connection_queues.get(connection_id)
    if not queue:
        return
    
    try:
        data = json.loads(message)
        if data['header']['code'] != 0:
            error_code = data['header']['code']
            error_message = data['header'].get('message', '未知错误')
            print(f'请求错误: {error_code}, {data}')
            
            # 特殊处理QPS限制错误
            if error_code == 11202:  # AppIdQpsOverFlowError
                queue.put("⚠️ 当前请求量过大，请稍后再试...")
            elif error_code == 11200:  # AppIdNoAuthError
                queue.put("❌ API认证失败，请检查配置...")
            else:
                queue.put(f"❌ 请求失败: {error_message}")
            
            ws.close()
        else:
            # 安全地提取内容，处理不同的字段名
            text_data = data["payload"]["choices"]["text"][0]
            content = ""
            
            # 尝试不同的字段名
            if "reasoning_content" in text_data:
                content = text_data["reasoning_content"]
            elif "content" in text_data:
                content = text_data["content"]
            else:
                # 如果都没有，跳过这条消息
                return
                
            if content:  # 只有当内容不为空时才放入队列
                queue.put(content)
                
            if data["payload"]["choices"]["status"] == 2:
                ws.close()
    except Exception as e:
        print(f"Error: {e}")
        # 不关闭连接，继续处理其他消息

def start_websocket_connection(params, question):
    connection_id = str(uuid.uuid4())  # 生成一个唯一标识符
    ws_param = Ws_Param(params['appid'], params['api_key'], params['api_secret'], params['spark_url'])
    ws_url = ws_param.create_url()
    queue = Queue()
    connection_queues[connection_id] = queue
    
    # 添加连接状态跟踪
    connection_ready = threading.Event()
    
    def on_open_optimized(ws):
        # 发送消息
        data = json.dumps(ws.question)
        ws.send(data)
        # 标记连接已就绪
        connection_ready.set()
    
    ws = websocket.WebSocketApp(ws_url,
                                on_message=lambda ws, msg: on_message(ws, msg),
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open_optimized)
    ws.question = question
    ws.get_id = lambda: connection_id
    
    # 启动WebSocket连接
    threading.Thread(target=lambda: ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})).start()
    
    # 等待连接建立（最多等待2秒）
    if connection_ready.wait(timeout=2.0):
        print("WebSocket连接已建立，开始接收消息")
    else:
        print("WebSocket连接建立超时")
    
    return queue