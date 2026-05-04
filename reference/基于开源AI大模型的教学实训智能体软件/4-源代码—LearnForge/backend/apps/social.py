
from flask_login import LoginManager, UserMixin, login_user, logout_user
import websocket
from  pymysql import MySQLError
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


app = Blueprint('social',__name__)


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return f'<User {self.username}>'
    

# 使用jwt验证
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        # try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        current_user = data['user']
        print(current_user)
        print(request.get_json().get('follower_id') )
        print( request.get_json().get('sno'))
        if current_user == (request.get_json().get('follower_id')):
           
            # 判断登陆是否过期，暂时不想实现
            # if exp and datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(exp):
            #     return jsonify({'message': 'Token has expired!'}), 401
        # except jwt.ExpiredSignatureError:
        #     return jsonify({'message': 'Token has expired!'}), 401
        # except jwt.InvalidTokenError:
        #     return jsonify({'message': 'Token is invalid!'}), 401
            return f( *args, **kwargs)

    return decorated


def isMySelf(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        # try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        current_user = data['user']
        print(current_user)
        print( request.get_json().get('sno'))
        if current_user == (request.get_json().get('sno')):
           
            # 判断登陆是否过期，暂时不想实现
            # if exp and datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(exp):
            #     return jsonify({'message': 'Token has expired!'}), 401
        # except jwt.ExpiredSignatureError:
        #     return jsonify({'message': 'Token has expired!'}), 401
        # except jwt.InvalidTokenError:
        #     return jsonify({'message': 'Token is invalid!'}), 401
            return f( *args, **kwargs)

    return decorated

# 获取学生信息
@app.route('/getStudentInfo', methods=['GET'])
def get_student_info():
    sno = request.args.get('sno')
    if not sno:
        return jsonify({'error': '缺少学号'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 查询学生信息
        cur.execute('SELECT sno, request_times, name, gender, description, major, study_time, ClassID, tags, rank, bio FROM student WHERE sno = %s', (sno,))
        student = cur.fetchone()

        if not student:
            return jsonify({'error': '找不到该学生'}), 404

        # 将 tags 字符串转换为列表
        tags = student[8]
        if tags:
            tags_list = tags.split(',')
        else:
            tags_list = []


        # 构建学生信息字典
        student_info = {
            'sno': student[0],
            'request_times': student[1],
            'name': student[2],
            'gender': student[3],
            'description': student[4],
            'major': student[5],
            'study_time': student[6],
            'ClassID': student[7],
            'tags': tags_list,
            'rank': student[9],
            'bio' : student[10]
        }

        cur.close()
        conn.close()

        return jsonify(student_info), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    
# 更新tags
@app.route('/updateTags', methods=['POST'])
@isMySelf
def update_tags():
    data = request.get_json()
    sno = data.get('sno')
    tags = data.get('tags')

    if not sno:
        return jsonify({'error': '缺少学号'}), 400

    if not isinstance(tags, list):
        return jsonify({'error': '标签格式不正确，应为数组'}), 400

    # 将标签列表转换为逗号分隔的字符串
    tags_str = ','.join(tags)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 更新学生的标签
        cur.execute('UPDATE student SET tags = %s WHERE sno = %s', (tags_str, sno))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': '标签更新成功'}), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    
@app.route('/updateBio', methods=['POST'])
@isMySelf
def update_bio():
    data = request.get_json()
    sno = data.get('sno')
    bio = data.get('bio')

    if not sno:
        return jsonify({'error': '缺少学号'}), 400

    if not isinstance(bio, str):
        return jsonify({'error': 'bio格式不正确，应为字符串'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 更新学生的bio
        cur.execute('UPDATE student SET bio = %s WHERE sno = %s', (bio, sno))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': 'bio更新成功'}), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500

    
@app.route('/checkSocialStatus', methods=['POST'])
@token_required
def check_social_status():
    follower_sno = request.get_json().get('follower_id')
    followed_sno = request.get_json().get('following_id')

    if not follower_sno or not followed_sno:
        return jsonify({'error': '缺少关键参数'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if follower_sno follows followed_sno
        cur.execute('SELECT COUNT(*) FROM follows WHERE follower_id = %s AND following_id = %s', (follower_sno, followed_sno))
        count_following = cur.fetchone()[0]

        # Get number of followers for followed_sno
        cur.execute('SELECT COUNT(*) FROM follows WHERE following_id = %s', (followed_sno,))
        count_followers = cur.fetchone()[0]

        # Get number of people followed by followed_sno
        cur.execute('SELECT COUNT(*) FROM follows WHERE follower_id = %s', (followed_sno,))
        count_followed = cur.fetchone()[0]

        cur.close()
        conn.close()

        # Return true if there's a record (follower follows followed), otherwise false
        return jsonify({
            'is_following': count_following > 0,
            'followers_count': count_followers,
            'following_count': count_followed
        }), 200

    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500


@app.route('/follow', methods=['POST'])
@token_required
def follow_student():
    data = request.json
    follower_id = data.get('follower_id')
    following_id = data.get('following_id')

    if not follower_id or not following_id:
        return jsonify({'error': '缺少参数'}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor()
        # 检查关注关系是否已存在
        cursor.execute('SELECT * FROM follows WHERE follower_id = %s AND following_id = %s', (follower_id, following_id))
        if cursor.fetchone():
            return jsonify({'error': '关注关系已存在'}), 400

        # 创建关注关系
        cursor.execute('INSERT INTO follows (follower_id, following_id) VALUES (%s, %s)', (follower_id, following_id))
        db.commit()
        cursor.close()
        return jsonify({'message': '关注成功'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cursor.close()

@app.route('/unfollow', methods=['POST'])
@token_required
def unfollow_student():
    data = request.json
    follower_id = data.get('follower_id')
    following_id = data.get('following_id')

    if not follower_id or not following_id:
        return jsonify({'error': '缺少参数'}), 400

    try:
        db = get_db_connection()        
        cursor = db.cursor()
        # 删除关注关系
        cursor.execute('DELETE FROM follows WHERE follower_id = %s AND following_id = %s', (follower_id, following_id))
        db.commit()
        cursor.close()
        return jsonify({'message': '取消关注成功'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cursor.close()


@app.route('/following', methods=['GET'])
def get_following():
    sno = request.args.get('sno')
    try:
        db = get_db_connection()        
        cursor = db.cursor()
        # 查询关注列表
        cursor.execute('SELECT s.sno, s.name FROM student s INNER JOIN follows f ON s.sno = f.following_id WHERE f.follower_id = %s', (sno,))
        following_list = cursor.fetchall()
        cursor.close()
        
        following_info = [{'sno': row[0], 'name': row[1]} for row in following_list]
        return jsonify(following_info), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500

@app.route('/followers', methods=['GET'])
def get_followers():
    sno = request.args.get('sno')
    try:
        db = get_db_connection()        
        cursor = db.cursor()
        # 查询粉丝列表
        cursor.execute('SELECT s.sno, s.name FROM student s INNER JOIN follows f ON s.sno = f.follower_id WHERE f.following_id = %s', (sno,))
        followers_list = cursor.fetchall()
        cursor.close()
        
        followers_info = [{'sno': row[0], 'name': row[1]} for row in followers_list]
        return jsonify(followers_info), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500



# 修改密码

@app.route('/updatePassword', methods=['POST'])
@isMySelf
def update_password():
    data = request.get_json()
    sno = data.get('sno')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not sno or not old_password or not new_password:
        return jsonify({'error': '缺少学号、旧密码或新密码'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 获取旧密码
        cur.execute('SELECT password FROM student WHERE sno = %s', (sno,))
        result = cur.fetchone()

        if result is None:
            return jsonify({'error': '用户不存在'}), 404

        fetched_old_password = result[0]
        if fetched_old_password != old_password:
            return jsonify({'error': '旧密码错误'}), 400

        # 更新密码
        cur.execute('UPDATE student SET password = %s WHERE sno = %s', (new_password, sno))
        conn.commit()

        cur.close()
        conn.close()
        return jsonify({'message': '密码更新成功'}), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    
 # 修改签名
@app.route('/updateDescription', methods=['POST'])
@isMySelf
def update_description():
    data = request.get_json()
    sno = data.get('sno')
    new_description = data.get('new_description')

    if not sno or not new_description:
        return jsonify({'error': '缺少学号或新签名'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 更新签名
        cur.execute('UPDATE student SET description = %s WHERE sno = %s', (new_description, sno))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': '签名更新成功'}), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    



@app.route('/toby', methods=['POST'])
@isMySelf
def coin():
    data = request.get_json()
    username = data.get('sno')
    targetsno = str(data.get('targetsno'))
    num = data.get('num')
    print(username)
    print(targetsno)
    if len(username)==7:
        return jsonify({'error': '老师不能投币'}), 400
    if num >2:
        return jsonify({'error': '投币数不能超过2'}), 400
    
    if username==targetsno:
        return jsonify({'error': '不能投自己'}), 400

    if not username or not targetsno or not num:
        return jsonify({'error': '缺少参数'}), 400

    try:
        num = int(num)
        if num <= 0:
            return jsonify({'error': '投币数必须为正整数'}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # 获取用户名的 request_times
        cur.execute('SELECT sno, request_times FROM student WHERE sno = %s', (username,))
        user = cur.fetchone()
        if not user:
            return jsonify({'error': '用户名不存在'}), 404

        username_sno, username_request_times = user
        if username_request_times < num:
            return jsonify({'error': '投币数超出余额'}), 400

        # 更新 request_times
        cur.execute('UPDATE student SET request_times = request_times - %s WHERE sno = %s', (num, username_sno))
        cur.execute('UPDATE student SET request_times = request_times + %s WHERE sno = %s', (num, targetsno))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': '投币成功'}), 200

    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500


# 消息模块
@app.route('/getMessages', methods=['POST'])
def get_messages():
    sno = request.get_json().get('sno')
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            # Query to get messages from student_message table with sender and receiver names
            query_student_messages = """
            SELECT 
                sm.id,
                sm.sender_sno,
                sm.receiver_sno,
                sm.content,
                sm.timestamp,
                sm.is_read,
                s1.name AS sender_name,
                s2.name AS receiver_name
            FROM 
                student_message sm
            JOIN 
                student s1 ON sm.sender_sno = s1.sno
            JOIN 
                student s2 ON sm.receiver_sno = s2.sno
            WHERE 
                sm.sender_sno = %s OR sm.receiver_sno = %s
            """
            
            # Query to get messages from teacher_notification table with sender name
            query_teacher_notifications = """
            SELECT 
                tn.id,
                tn.tno AS sender_sno,
                tn.sno AS receiver_sno,
                tn.message AS content,
                tn.timestamp,
                tn.is_read,
                t.name AS sender_name,
                s.name AS receiver_name
            FROM 
                teacher_notification tn
            JOIN 
                teacher t ON tn.tno = t.tno
            JOIN 
                student s ON tn.sno = s.sno
            WHERE 
                tn.tno = %s OR tn.sno = %s
            """
            
            # Execute both queries
            cursor.execute(query_student_messages, (sno, sno))
            student_messages = cursor.fetchall()
            
            cursor.execute(query_teacher_notifications, (sno, sno))
            teacher_notifications = cursor.fetchall()
            # print(sno)
            # print(row[1])
            
            # Construct JSON responses
            student_messages_json = [
                {
                    'id': row[0],
                    'sender_sno': row[1],
                    'receiver_sno': row[2],
                    'content': row[3],
                    'timestamp': row[4],
                    'is_read': row[5],
                    'sender_name': row[6],
                    'receiver_name': row[7],
                    'partner_name': row[7] if sno == str(row[1]) else row[6],
                    # 'partner_sno': row[2] if sno == str(row[1]) else row[1]
                } for row in student_messages
            ]

            
            admin_messages_json = [
                {
                    'id': row[0],
                    'sender_sno': row[1],
                    'receiver_sno': row[2],
                    'content': row[3],
                    'timestamp': row[4],
                    'is_read': row[5],
                    'sender_name': row[6],
                    'receiver_name': row[7]
                } for row in teacher_notifications
            ]
            
            # Return the constructed JSON
            return jsonify({
                'status': 'success', 
                'admin_messages': admin_messages_json, 
                'student_messages': student_messages_json
            }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        connection.close()

@app.route('/updateMessage', methods=['POST'])
def update_message():
    data = request.get_json()
    sender = data.get('sender')
    receiver = data.get('receiver')
    content = data.get('content')

    if not sender or not receiver or not content:
        return jsonify({'error': 'Missing sender, receiver, or content'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Update the message content considering any order of sender and receiver
        update_query = '''
        UPDATE student_message
        SET content = %s
        WHERE 
            (sender_sno = %s AND receiver_sno = %s) OR
            (sender_sno = %s AND receiver_sno = %s)
        '''
        cur.execute(update_query, (content, sender, receiver, receiver, sender))
        conn.commit()

        # Check if any rows were affected
        if cur.rowcount == 0:
            return jsonify({'error': 'Message not found or not updated'}), 404

        cur.close()
        conn.close()

        return jsonify({'message': 'Message updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
@app.route('/createChat', methods=['POST'])
def create_chat():
    data = request.get_json()
    sender = data.get('sender')
    receiver = data.get('receiver')

    if not sender or not receiver:
        return jsonify({'error': 'Missing sender or receiver'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if a chat already exists between the sender and receiver
        check_query = '''
        SELECT COUNT(*) FROM student_message
        WHERE 
            (sender_sno = %s AND receiver_sno = %s) OR
            (sender_sno = %s AND receiver_sno = %s)
        '''
        cur.execute(check_query, (sender, receiver, receiver, sender))
        count = cur.fetchone()[0]

        if count > 0:
            return jsonify({'message': 'Chat already exists'}), 200

        # Default content structure
        content = {
            "sender": sender,
            "receiver": receiver,
            "messages": []
        }

        # Insert a new chat entry into the student_message table
        insert_query = '''
        INSERT INTO student_message (sender_sno, receiver_sno, content, timestamp, is_read)
        VALUES (%s, %s, %s, NOW(), 0)
        '''
        cur.execute(insert_query, (sender, receiver, json.dumps(content)))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': 'Chat created successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500



@app.route('/fetchMessages', methods=['GET'])
def fetch_messages():
    sender = request.args.get('sender')
    receiver = request.args.get('receiver')

    if not sender or not receiver:
        return jsonify({'error': 'Missing sender or receiver'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch messages based on sender and receiver
        fetch_query = '''
        SELECT id, sender_sno, receiver_sno, content, timestamp, is_read
        FROM student_message
        WHERE sender_sno = %s AND receiver_sno = %s
        ORDER BY timestamp ASC
        '''
        cur.execute(fetch_query, (sender, receiver))
        messages = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'messages': messages}), 200
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500