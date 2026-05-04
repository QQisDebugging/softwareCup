
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
from utils import DelDataById,InsertData,UpdateData,GetSql2,get_db_connection,get_access_token,DocumentUpload,on_close,on_error,on_message,on_open,AIPPT,add_body,add_MainHeading,generate_text_from_model,extract_high_freq_words_from_file,generate_text_from_model_spark
from spark_client import Document_Q_And_A,on_error_doc,on_close_doc,on_open_doc,on_message_doc
from pymysql.err import IntegrityError

from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH


app = Blueprint('common',__name__)


# 提交学习时间
@app.route('/pushStudyTime', methods=['POST'])
#@token_required
def pushStudyTime():
    if not request.json:
        return jsonify({'error': '无效的请求数据'}), 400
    
    username = request.json.get('username')
    addtime = request.json.get('studytime')
    if username and addtime:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '数据库连接失败'}), 500

        cur = conn.cursor()
        try:
            sql = 'UPDATE student SET study_time = study_time + %s WHERE sno = %s;'
            cur.execute(sql, (addtime,username))
            conn.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            return jsonify({'error': '数据库错误', 'details': str(e)}), 500
        finally:
            
            conn.close()       
        
    else:
       return jsonify({'success': False, 'message': '缺少参数'}), 400   
 
    

# @app.route('/pushRequestTimes', methods=['POST'])
# @add_request_func
def pushRequestTimes(username,times):
    if username and times:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '数据库连接失败'}), 500

        cur = conn.cursor()
        try:
            sql = 'UPDATE student SET request_times = request_times + %s WHERE sno = %s;'
            cur.execute(sql, (times, username))
            conn.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            return jsonify({'error': '数据库错误', 'details': str(e)}), 500
        finally:
            conn.close()
    else:
       return jsonify({'success': False, 'message': '缺少参数'}), 400
    

# 每日请求+1
@app.route('/addRequest', methods=['POST'])
def addRequest():
    if not request.json:
        return jsonify({'error': '无效的请求数据'}), 400
    
    sno = request.json.get('username')
    if sno:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '数据库连接失败'}), 500

        cur = conn.cursor()
        try:
            today = datetime.date.today()
            # Check if there is already a record for today (使用本地数据库的小写表名)
            cur.execute('SELECT * FROM userrequests WHERE user_id = %s AND request_date = %s', (sno, today))
            result = cur.fetchone()
            
            if result:
                # If there is already a record, update the request_count
                cur.execute('UPDATE userrequests SET request_count = request_count + 1 WHERE user_id = %s AND request_date = %s', (sno, today))
            else:
                # If no record exists for today, insert a new record
                cur.execute('INSERT INTO userrequests (user_id, request_date, request_count) VALUES (%s, %s, 1)', (sno, today))
            
            conn.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            return jsonify({'error': '数据库错误', 'details': str(e)}), 500
        finally:
            conn.close()
    else:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
