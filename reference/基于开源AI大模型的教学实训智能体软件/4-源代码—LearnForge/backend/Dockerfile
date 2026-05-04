# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# 复制应用代码到工作目录
COPY . .

# 启动 Gunicorn 服务器，监听 0.0.0.0:5000，使用 app:app 作为应用入口
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "4", "--worker-class", "gevent", "--timeout", "1200"]
