
from flask_login import LoginManager, UserMixin, login_user, logout_user
import websocket
from  pymysql import MySQLError
import time
from urllib.parse import urlencode
import json
import websocket
import _thread as thread
import ssl
from flask import Blueprint, request, Response, send_file, send_from_directory,current_app
import requests
import json
import os
from flask_cors import CORS  
from spark_client import start_websocket_connection
from datetime import timedelta
import datetime
import jwt
# from psycopg2 import OperationalError
from flask import Flask, jsonify, make_response, request, session
from flask_cors import CORS
# import psycopg2
# import hashlib
from functools import wraps
from flask import Flask, render_template, request, flash, url_for, redirect
# from flask_bootstrap import Bootstrap
# from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
# from wtforms import SelectField
# from wtforms.fields import StringField,PasswordField,PasswordField,SubmitField
# from wtforms.validators import DataRequired, Length
# from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from utils import DelDataById,InsertData,UpdateData,GetSql2,get_db_connection,get_access_token,DocumentUpload,on_close,on_error,on_message,on_open,AIPPT,add_body,add_MainHeading,generate_text_from_model,extract_high_freq_words_from_file,generate_text_from_model_spark
from spark_client import Document_Q_And_A,on_error_doc,on_close_doc,on_open_doc,on_message_doc
from pymysql.err import IntegrityError

from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH


app = Blueprint('user',__name__)


# 安全模块
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'  # 未登录用户将被重定向到登录页面
# 设置越权登录提示
login_manager.login_message = "先登录哈"


@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id,username=user_id,password_hash="11111111")


   


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return f'<User {self.username}>'
    




# 登录
@app.route('/login', methods=['POST'])
# @add_request_func
def login():
    # print("hello")
    username = request.json.get('username')
    password = request.json.get('password')
    tag = request.json.get('role')

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cur = conn.cursor()
    try:
        if tag=='student':
            sql = 'SELECT name FROM student WHERE sno=%s AND password=%s'
        else:
            sql = 'SELECT name FROM teacher WHERE tno=%s AND password=%s'
        cur.execute(sql, (username, password))
        
        is_valid_user = cur.fetchone()
    except Exception:
        return jsonify({'error': 'Database error'}), 500
    finally:
        conn.close()

    if is_valid_user:
        # #添加登陆状态
        user = User(id=username, username=is_valid_user[0], password_hash=password)
        # logout_user()
        login_user(user)
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token,'realname':is_valid_user[0]})
    else:
        return jsonify({'success': False, 'message': '账号或密码错误'}), 401
    
# 登出接口
@app.route('/logout', methods=['POST'])
# @add_request_func
def logout():
    try:
        logout_user()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'error': 'Logout failed', 'message': str(e)}), 500
    
# 学生注册
@app.route('/registerStudent', methods=['POST'])
def register_student():
    data = request.json
    sno = data.get('sno')
    name = data.get('name')
    gender = data.get('gender')
    password = data.get('password')
    class_id = data.get('class_id')
    major = data.get('major')

    if not sno or not name or not password or not class_id:
        return jsonify({'error': '学号, 姓名, 密码和班级ID是必填项'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500
    print((sno, name, gender, password, class_id,major))

    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO student (sno, name, gender, password, ClassID, major)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sno, name, gender, password, class_id, major))
        conn.commit()
        print(11111)
        return jsonify({'message': '学生注册成功'}), 201
    except IntegrityError as e:
        return jsonify({'error': '学号已存在', 'details': str(e)}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()
