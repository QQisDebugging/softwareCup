
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

app = Blueprint('student',__name__)




# 根据学号获取学生实训        
@app.route('/getStudentAssignments', methods=['GET'])
def get_student_assignments():
    sno = request.args.get('sno')
    if not sno:
        return jsonify({'error': '缺少学生编号sno'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取学生的 ClassID
        cur.execute('SELECT ClassID FROM student WHERE sno = %s', (sno,))
        class_result = cur.fetchone()
        if not class_result:
            return jsonify({'error': '学生不存在'}), 404
        class_id = class_result[0]  # 这里使用索引来获取 ClassID

        # 获取学生班级参与的作业
        cur.execute('''
        SELECT a.assignment_id, a.assignment_name, a.tasks_json, a.publish_date, a.creator_tno
        FROM assignment a
        JOIN assignment_class ac ON a.assignment_id = ac.assignment_id
        WHERE ac.class_id = %s
        ORDER BY a.publish_date DESC
        ''', (class_id,))
        assignments = cur.fetchall()

        # 获取学生的作业完成状态
        cur.execute('''
        SELECT sa.assignment_id
        FROM student_assignment sa
        WHERE sa.sno = %s
        ''', (sno,))
        completed_assignments = cur.fetchall()
        completed_assignments_set = {row[0] for row in completed_assignments}

        assignment_list = []
        for assignment in assignments:
            assignment_info = {
                'assignment_id': assignment[0],
                'assignment_name': assignment[1],
                'tasks_json': assignment[2],
                'publish_date': assignment[3],
                'creator_tno': assignment[4],
                # 'isDone': assignment[0] in completed_assignments_set
            }
            assignment_list.append(assignment_info)

        return jsonify(assignment_list), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



@app.route('/getStudentContests', methods=['GET'])
def get_contests():
    sno = request.args.get('sno')
    if not sno:
        return jsonify({'error': '缺少学生编号sno'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取学生的 ClassID
        cur.execute('SELECT ClassID FROM student WHERE sno = %s', (sno,))
        class_result = cur.fetchone()
        if not class_result:
            return jsonify({'error': '学生不存在'}), 404
        class_id = class_result[0]

        # 获取学生班级参与的竞赛，按发布日期降序排列
        cur.execute('''
        SELECT c.contest_id, c.contest_name, c.question_json, c.question_type, c.publish_date
        FROM contest c
        JOIN contest_class cc ON c.contest_id = cc.contest_id
        WHERE cc.class_id = %s
        ORDER BY c.publish_date DESC
        ''', (class_id,))
        contests = cur.fetchall()

        contest_list = []
        for contest in contests:
            contest_id = contest[0]
            # 检查学生是否提交过该竞赛的答案
            cur.execute('''
            SELECT COUNT(*) FROM student_contest_answers 
            WHERE contest_id = %s AND sno = %s
            ''', (contest_id, sno))
            submission_result = cur.fetchone()
            is_done = submission_result[0] > 0  # 如果有记录，则表示已提交

            contest_info = {
                'contest_id': contest_id,
                'contest_name': contest[1],
                'question_json': contest[2],
                'question_type': contest[3],
                'publish_date': contest[4],
                'isDone': is_done
            }
            contest_list.append(contest_info)

        return jsonify(contest_list), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



# 通过学号获取属于该名学生的活动
@app.route('/getStudentActivities', methods=['GET'])
def get_activities():
    sno = request.args.get('sno')
    if not sno:
        return jsonify({'error': '缺少学生编号sno'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取学生的 ClassID
        cur.execute('SELECT ClassID FROM student WHERE sno = %s', (sno,))
        class_result = cur.fetchone()
        if not class_result:
            return jsonify({'error': '学生不存在'}), 404
        class_id = class_result[0]  # 这里使用索引来获取 ClassID

        # 获取学生班级参与的活动
        cur.execute('''
        SELECT a.activity_id, a.activity_name, a.description, a.created_date
        FROM activity a
        JOIN activity_classes ac ON a.activity_id = ac.activity_id
        WHERE ac.class_id = %s
        ORDER BY a.created_date DESC
        ''', (class_id,))
        activities = cur.fetchall()

        activity_list = []
        for activity in activities:
            activity_info = {
                'activity_id': activity[0],
                'activity_name': activity[1],
                'description': activity[2],
                'created_date': activity[3]
            }
            activity_list.append(activity_info)
        print(activity_list)
        return jsonify(activity_list), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



@app.route('/submitWorkAnswers', methods=['POST'])
def submitWorkAnswers():
    data = request.get_json()
    assignment_id = data.get('assignment_id')
    sno = data.get('sno')
    answers = data.get('answers')
    from datetime import datetime
    submission_date = datetime.now()

    if not all([assignment_id, sno, answers]):
        return jsonify({'error': '缺少必要的参数'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO student_assignment_submission (assignment_id, sno, answers, submission_date)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                answers = VALUES(answers),
                submission_date = VALUES(submission_date)
        ''', (assignment_id, sno, json.dumps(answers), submission_date))
        conn.commit()
        return jsonify({'message': '提交成功'}), 201
    except Exception as e:
        return jsonify({'error': '服务器错误', 'details': str(e)}), 500
    finally:
        pushRequestTimes(sno,1)
        cur.close()
        conn.close()



@app.route('/submitContestAnswers', methods=['POST'])
def submitContestAnswers():
    data = request.get_json()
    contest_id = data.get('contest_id')
    sno = data.get('sno')
    answers = data.get('answers')
    question_type = data.get('question_type')
    score = data.get('score')
    from datetime import datetime
    submission_date = datetime.now()

    if not all([contest_id, sno, question_type]):
        return jsonify({'error': '缺少必要的参数'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO student_contest_answers (contest_id, sno, question_type, score, submission_date)
            VALUES (%s, %s, %s, %s, %s)
        ''', (contest_id, sno, question_type, score, submission_date))
        conn.commit()
        return jsonify({'message': '提交成功'}), 201
    except Exception as e:
        if e.args[0] == 1062:
            return jsonify({'error': '重复提交', 'details': str(e)}), 409
        else:
            return jsonify({'error': '服务器错误', 'details': str(e)}), 500
    finally:
        pushRequestTimes(sno,1)
        cur.close()
        conn.close()

        
# 提交作业
@app.route('/submitAssignmentAnswers', methods=['POST'])
def submit_assignment():
    try:
        assignment_data = request.get_json()
        sno = assignment_data.get('sno')
        activity_id = assignment_data.get('activity_id')
        content = assignment_data.get('content')
        analyse_result = assignment_data.get('analyse_result')
        from datetime import datetime
        submission_date = datetime.now()
        final_content = json.dumps({"code": content, "analyse_result": analyse_result}, ensure_ascii=False)

        if not (sno and activity_id and content):
            return jsonify({'error': '缺少必要参数'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '数据库连接失败'}), 500

        cur = conn.cursor()

        # Check if the entry already exists
        cur.execute('''
            SELECT COUNT(*) FROM student_assignment 
            WHERE sno = %s AND activity_id = %s
        ''', (sno, activity_id))
        entry_exists = cur.fetchone()[0] > 0

        if entry_exists:
            # Update the existing entry
            cur.execute('''
                UPDATE student_assignment 
                SET content = %s, submission_date = %s 
                WHERE sno = %s AND activity_id = %s
            ''', (final_content, submission_date, sno, activity_id))
        else:
            # Insert a new entry
            cur.execute('''
                INSERT INTO student_assignment (sno, activity_id, content, submission_date)
                VALUES (%s, %s, %s, %s)
            ''', (sno, activity_id, final_content, submission_date))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'success': True}), 200
    except Exception as e:
        pushRequestTimes(sno,1)
        return jsonify({'error': '作业提交失败', 'details': str(e)}), 500

    