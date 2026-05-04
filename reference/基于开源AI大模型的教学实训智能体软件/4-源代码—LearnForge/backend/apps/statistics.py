
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
from flask import Flask, jsonify, make_response, request, session
from flask_cors import CORS
from functools import wraps
from flask import Flask, render_template, request, flash, url_for, redirect
from utils import DelDataById,InsertData,UpdateData,GetSql2,get_db_connection,get_access_token,DocumentUpload,on_close,on_error,on_message,on_open,AIPPT,add_body,add_MainHeading,generate_text_from_model,extract_high_freq_words_from_file,generate_text_from_model_spark
from spark_client import Document_Q_And_A,on_error_doc,on_close_doc,on_open_doc,on_message_doc
from pymysql.err import IntegrityError

from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from apps.common import pushRequestTimes

app = Blueprint('statistics',__name__)

@app.route('/top3UsersToday', methods=['GET'])
def get_top3_users_today():
    today_str = str(datetime.date.today())
    print(today_str)
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '无法连接到数据库'}), 500
        
        cur = conn.cursor()
    
        print(today_str)
        # 查询当天请求次数最多的三位用户
        cur.execute('''
            SELECT ur.user_id, s.name,ur.request_count
            FROM userrequests ur
            JOIN student s ON ur.user_id = s.sno
            WHERE ur.request_date = %s
            ORDER BY ur.request_count DESC
            LIMIT 6
        ''', (today_str,))
        
        top_users = cur.fetchall()
        print(top_users)

        if not top_users:
            return jsonify({'message': '今天没有请求记录'}), 404
        
        # 构建字典列表
        users_list = []
        for user in top_users:
            user_dict = {
                'user_id': user[0],
                'name': user[1],
                'request_count': user[2]
            }
            users_list.append(user_dict)

        cur.close()
        conn.close()

        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500



@app.route('/todayContestSubmissions', methods=['GET'])
def get_today_contest_submissions():
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '无法连接到数据库'}), 500
        
        cur = conn.cursor()
    
        # 查询当天提交的contest，包括contest信息、提交次数、提交者姓名和学号
        cur.execute('''
            SELECT 
                c.contest_id, 
                c.contest_name, 
                s.sno, 
                s.name
            FROM 
                contest c
            JOIN 
                student_contest_answers sca ON c.contest_id = sca.contest_id
            JOIN 
                student s ON sca.sno = s.sno
            WHERE 
                DATE(sca.submission_date) = %s
            GROUP BY 
                c.contest_id, s.sno
            ORDER BY 
                c.contest_id, s.sno;
        ''', (today_str,))
        
        submissions = cur.fetchall()

        if not submissions:
            return jsonify({'message': '今天没有提交记录'}), 404
        
        # 构建返回的字典列表
        contests = {}
        for submission in submissions:
            contest_id = submission[0]
            if contest_id not in contests:
                contests[contest_id] = {
                    'contest_id': submission[0],
                    'contest_name': submission[1],
                    'submissions': []
                }
            contests[contest_id]['submissions'].append({
                'sno': submission[2],
                'name': submission[3]
            })

        cur.close()
        conn.close()

        # 将结果转换为列表返回
        return jsonify(list(contests.values())), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500


@app.route('/todayActivities', methods=['GET'])
def get_today_activities():
    today_str = str(datetime.date.today())
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '无法连接到数据库'}), 500
        
        cur = conn.cursor()
        
        # 查询当天提交的活动信息、提交次数及提交人信息
        cur.execute('''
            SELECT 
                a.activity_name,
                a.activity_id,
                s.sno,
                s.name,
                s.ClassID
            FROM 
                student_assignment sa
            JOIN 
                student s ON sa.sno = s.sno
            JOIN 
                activity a ON sa.activity_id = a.activity_id
            WHERE 
                DATE(sa.submission_date) = %s
            ORDER BY 
                a.activity_id, s.sno;
        ''', (today_str,))
        
        activities = cur.fetchall()
        
        if not activities:
            return jsonify({'message': '今天没有提交的活动'}), 404

        # 构建返回的字典列表
        activities_dict = {}
        for activity in activities:
            activity_id = activity[1]
            if activity_id not in activities_dict:
                activities_dict[activity_id] = {
                    'activity_id': activity_id,
                    'activity_name': activity[0],
                    'submission_count': 0,
                    'submissions': []
                }
            activities_dict[activity_id]['submissions'].append({
                'sno': activity[2],
                'name': activity[3],
                'ClassID': activity[4]
            })
            # 更新提交次数
            activities_dict[activity_id]['submission_count'] = len(activities_dict[activity_id]['submissions'])

        cur.close()
        conn.close()

        # 将结果转换为列表返回
        return jsonify(list(activities_dict.values())), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500


@app.route('/todayAssignments', methods=['GET'])
def get_today_assignments():
    today_str = str(datetime.date.today())
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '无法连接到数据库'}), 500
        
        cur = conn.cursor()
        
        # 查询当天提交的作业信息、提交次数及提交人信息
        cur.execute('''
            SELECT 
                a.assignment_name,
                a.assignment_id,
                s.sno,
                s.name,
                s.ClassID
            FROM 
                student_assignment_submission sas
            JOIN 
                student s ON sas.sno = s.sno
            JOIN 
                assignment a ON sas.assignment_id = a.assignment_id
            WHERE 
                DATE(sas.submission_date) = %s
            ORDER BY 
                a.assignment_id, s.sno;
        ''', (today_str,))
        
        assignments = cur.fetchall()
        
        if not assignments:
            return jsonify({'message': '今天没有提交的作业'}), 404
        
        # 构建返回的字典列表
        assignments_dict = {}
        for assignment in assignments:
            assignment_id = assignment[1]
            if assignment_id not in assignments_dict:
                assignments_dict[assignment_id] = {
                    'assignment_id': assignment_id,
                    'assignment_name': assignment[0],
                    'submission_count': 0,
                    'submissions': []
                }
            assignments_dict[assignment_id]['submissions'].append({
                'sno': assignment[2],
                'name': assignment[3],
                'ClassID': assignment[4]
            })
            # 更新提交次数
            assignments_dict[assignment_id]['submission_count'] = len(assignments_dict[assignment_id]['submissions'])

        cur.close()
        conn.close()

        # 将结果转换为列表返回
        return jsonify(list(assignments_dict.values())), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    



@app.route('/classSubmissions', methods=['GET'])
def get_class_submissions():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '无法连接到数据库'}), 500
        
        cur = conn.cursor()
        
        # 修复的查询：分别统计每个班级的各种提交类型，避免笛卡尔积
        cur.execute('''
            WITH class_activity_submissions AS (
                SELECT 
                    c.ClassID,
                    COUNT(DISTINCT sa.assignment_id) AS activity_submission_count
                FROM 
                    classes c
                LEFT JOIN 
                    student s ON c.ClassID = s.ClassID
                LEFT JOIN 
                    student_assignment sa ON s.sno = sa.sno
                GROUP BY 
                    c.ClassID
            ),
            class_assignment_submissions AS (
                SELECT 
                    c.ClassID,
                    COUNT(DISTINCT sas.submission_id) AS assignment_submission_count
                FROM 
                    classes c
                LEFT JOIN 
                    student s ON c.ClassID = s.ClassID
                LEFT JOIN 
                    student_assignment_submission sas ON s.sno = sas.sno
                GROUP BY 
                    c.ClassID
            ),
            class_contest_submissions AS (
                SELECT 
                    c.ClassID,
                    COUNT(DISTINCT sca.id) AS contest_submission_count
                FROM 
                    classes c
                LEFT JOIN 
                    student s ON c.ClassID = s.ClassID
                LEFT JOIN 
                    student_contest_answers sca ON s.sno = sca.sno
                GROUP BY 
                    c.ClassID
            )
            SELECT 
                c.ClassID,
                c.ClassName,
                COALESCE(cas.activity_submission_count, 0) AS activity_submission_count,
                COALESCE(cass.assignment_submission_count, 0) AS assignment_submission_count,
                COALESCE(ccs.contest_submission_count, 0) AS contest_submission_count,
                (COALESCE(cas.activity_submission_count, 0) + 
                 COALESCE(cass.assignment_submission_count, 0) + 
                 COALESCE(ccs.contest_submission_count, 0)) AS total_submission_count
            FROM 
                classes c
            LEFT JOIN 
                class_activity_submissions cas ON c.ClassID = cas.ClassID
            LEFT JOIN 
                class_assignment_submissions cass ON c.ClassID = cass.ClassID
            LEFT JOIN 
                class_contest_submissions ccs ON c.ClassID = ccs.ClassID
            WHERE
                (COALESCE(cas.activity_submission_count, 0) + 
                 COALESCE(cass.assignment_submission_count, 0) + 
                 COALESCE(ccs.contest_submission_count, 0)) > 0
            ORDER BY 
                total_submission_count DESC
            LIMIT 10;
        ''')
        
        class_submissions = cur.fetchall()
        
        cur.close()
        conn.close()

        if not class_submissions:
            return jsonify({'message': '没有找到提交记录'}), 404
        
        # 构建返回的字典列表
        class_submissions_dict = []
        for row in class_submissions:
            class_submissions_dict.append({
                'ClassID': row[0],
                'ClassName': row[1],
                'activity_submission_count': row[2],
                'assignment_submission_count': row[3],
                'contest_submission_count': row[4],
                'total_submission_count': row[5]
            })
        
        return jsonify(class_submissions_dict), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
