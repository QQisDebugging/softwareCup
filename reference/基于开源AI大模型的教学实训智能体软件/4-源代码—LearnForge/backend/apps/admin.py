
from flask_login import LoginManager, UserMixin, login_user, logout_user
import websocket
from  pymysql import MySQLError
import time
from urllib.parse import urlencode
import json
import websocket
import _thread as thread
import ssl
from flask import Blueprint, request, current_app
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
from decimal import Decimal
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
app = Blueprint('admin',__name__)



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
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
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

# 使用jwt验证是否为管理员
def admin_required(f):
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
        if current_user == (request.get_json().get('tno')):
           
            # 判断登陆是否过期，暂时不想实现
            # if exp and datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(exp):
            #     return jsonify({'message': 'Token has expired!'}), 401
        # except jwt.ExpiredSignatureError:
        #     return jsonify({'message': 'Token has expired!'}), 401
        # except jwt.InvalidTokenError:
        #     return jsonify({'message': 'Token is invalid!'}), 401
            return f( *args, **kwargs)

    return decorated



# 获取排名（前100）根据学习时间
@app.route('/getRank', methods=['GET'])
def getRank():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        sql = 'SELECT name, major, study_time, description,request_times,sno FROM student ORDER BY request_times DESC,study_time DESC ;'
        cur.execute(sql)
        rows = cur.fetchall()
    
        
        # 将查询结果组装成 JSON 格式
        rank_list = [{'idx': idx + 1, 'name': row[0], 'major': row[1], 'study_time': row[2], 'description': row[3], "request_times": row[4], "user_id": row[5]} for idx, row in enumerate(rows)]

        
        return json.dumps(rank_list,ensure_ascii=False), 200,
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        conn.close()


@app.route('/get15days', methods=['GET'])
def get7days_request():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        sql = '''
        SELECT 
            request_date,
            SUM(request_count) AS total_requests
        FROM 
            userrequests
        WHERE 
            request_date >= CURDATE() - INTERVAL 15 DAY
        GROUP BY 
            request_date
        ORDER BY 
            request_date;
        '''
        cur.execute(sql)
        rows = cur.fetchall()
        
        # 将查询结果组装成 JSON 格式，并处理 Decimal 类型
        request_list = [
            {
                'request_date': row[0].strftime('%Y-%m-%d'),
                'total_requests': float(row[1]) if isinstance(row[1], Decimal) else row[1]
            }
            for row in rows
        ]
        
        return json.dumps(request_list, ensure_ascii=False), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        conn.close()


@app.route('/getActiviteMap', methods=['GET'])
def getActiviteMap():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    # 从请求中获取用户 ID 和请求日期
    user_id = request.args.get('sno')
    # request_date = datetime.date.today().strftime('%Y-%m-%d')
    # print(request_date)
    
    if not user_id:
        return jsonify({'error': '缺少用户 ID 参数'}), 400

    cur = conn.cursor()
    try:

        # 如果提供了请求日期，则使用用户 ID 和请求日期进行查询
        sql = 'SELECT request_date, request_count FROM userrequests WHERE user_id = %s  ORDER BY request_date DESC;'
        cur.execute(sql, (user_id, ))
        
        rows = cur.fetchall()
       
        
        # 将查询结果组装成 JSON 格式
        activity_map = [{'date': row[0].strftime('%Y-%m-%d'), 'count': row[1]} for row in rows]
       
        return json.dumps(activity_map, ensure_ascii=False), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        conn.close()


@app.route('/generateWork', methods=['POST'])
def generate_tasks():
    try:
        data = request.json
        content = data.get('content')
        
        if not content or not content.strip():
            return jsonify({'error': '请提供实训项目描述'}), 400
        
        print(f"收到实训生成请求: {content}")
        
        # 尝试调用AI生成任务
        try:
            prompt1 = f"""需要用c语言设计一个 {content}，你需要输出完成这样一个任务所需要学习的知识点，例如基本输入输出，文件操作等等，然后给每一个知识点设计一个题目。
请严格按照下面的JSON格式输出，确保是有效的JSON数组：
[
    {{
        "知识点":"基本输入输出",
        "题目":"编写一个程序，要求用户输入两个整数，然后输出它们的和"
    }},
    {{
        "知识点":"变量和数据类型",
        "题目":"声明不同类型的变量（int、float、char），并为它们赋值，然后打印输出"
    }}
]

注意：请只输出JSON数组，不要包含任何其他文字说明。"""
            
            # 调用AI生成任务
            tasks_text = generate_text_from_model_spark(prompt1)
            print("AI返回的原始文本:", tasks_text)
            
            # 尝试解析JSON
            try:
                # 清理可能的markdown格式
                cleaned_text = tasks_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith('```'):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()
                
                tasks = json.loads(cleaned_text)
                
                # 验证数据格式
                if not isinstance(tasks, list) or len(tasks) == 0:
                    raise ValueError("AI返回的不是有效的任务列表")
                
                # 验证每个任务的格式
                for i, task in enumerate(tasks):
                    if not isinstance(task, dict) or '知识点' not in task or '题目' not in task:
                        raise ValueError(f"第{i+1}个任务格式不正确")
                
                print(f"AI生成成功，共{len(tasks)}个任务")
                return jsonify(tasks), 200
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"AI响应解析失败: {e}, 使用备用数据")
                # 解析失败，使用备用数据
                raise Exception("AI解析失败")
                
        except Exception as ai_error:
            print(f"AI服务调用失败: {ai_error}")
            # AI服务失败，使用基于项目描述的智能备用数据
            
            # 根据项目描述生成相关的任务
            fallback_tasks = []
            
            # 基础任务（适用于所有项目）
            basic_tasks = [
                {
                    "知识点": "基本输入输出",
                    "题目": f"为{content}编写一个程序，实现基本的数据输入和输出功能，使用scanf和printf函数"
                },
                {
                    "知识点": "变量和数据类型",
                    "题目": f"在{content}中声明和使用不同类型的变量（int、float、char、字符串等）来存储相关数据"
                }
            ]
            fallback_tasks.extend(basic_tasks)
            
            # 根据关键词添加特定任务
            content_lower = content.lower()
            
            if any(keyword in content_lower for keyword in ['管理', '系统', '信息']):
                fallback_tasks.extend([
                    {
                        "知识点": "结构体",
                        "题目": f"为{content}设计合适的结构体来存储相关信息，如用户信息、记录信息等"
                    },
                    {
                        "知识点": "文件操作",
                        "题目": f"实现{content}的数据持久化，使用文件读写操作保存和加载数据"
                    }
                ])
            
            if any(keyword in content_lower for keyword in ['计算', '算法', '数学']):
                fallback_tasks.append({
                    "知识点": "算法设计",
                    "题目": f"为{content}设计高效的算法，实现核心计算功能"
                })
            
            if any(keyword in content_lower for keyword in ['排序', '查找', '搜索']):
                fallback_tasks.append({
                    "知识点": "排序和查找",
                    "题目": f"在{content}中实现数据排序和查找功能，使用适当的排序和查找算法"
                })
            
            if any(keyword in content_lower for keyword in ['菜单', '界面', '交互']):
                fallback_tasks.append({
                    "知识点": "程序控制结构",
                    "题目": f"为{content}设计用户友好的菜单界面，使用循环和条件语句实现交互功能"
                })
            
            # 如果没有特定匹配，添加通用任务
            if len(fallback_tasks) == 2:  # 只有基础任务
                fallback_tasks.extend([
                    {
                        "知识点": "条件语句",
                        "题目": f"在{content}中使用if-else语句实现条件判断功能"
                    },
                    {
                        "知识点": "循环语句",
                        "题目": f"使用for或while循环实现{content}中的重复操作功能"
                    },
                    {
                        "知识点": "函数设计",
                        "题目": f"将{content}的功能模块化，设计并实现相关的函数"
                    }
                ])
            
            print(f"使用智能备用数据，共{len(fallback_tasks)}个任务")
            return jsonify(fallback_tasks), 200
            
    except Exception as e:
        print("生成任务时发生严重错误:", str(e))
        # 最后的兜底方案
        emergency_tasks = [
            {
                "知识点": "基本输入输出",
                "题目": "编写一个C语言程序，要求用户输入两个整数，然后输出它们的和"
            },
            {
                "知识点": "变量和数据类型", 
                "题目": "声明不同类型的变量并为它们赋值，然后打印输出"
            },
            {
                "知识点": "条件语句",
                "题目": "编写程序判断用户输入的数字是正数、负数还是零"
            }
        ]
        return jsonify(emergency_tasks), 200

# 教师创建实训内容
@app.route('/createAssignment', methods=['POST'])
#@token_required
def create_assignment():
    data = request.get_json()
    assignment_name = data.get('assignmentName')
    creator_tno = data.get('creatorTno')
    tasks_json = data.get('tasksJson')
    publish_date = data.get('publishDate')
    selected_classes = data.get('selectedClasses')

    # 检查必填字段
    if not assignment_name or not tasks_json or not publish_date:
        return jsonify({'error': '缺少必填字段'}), 400

    # 检查日期格式
    try:
        from datetime import datetime
        publish_date = datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        return jsonify({'error': '无效的日期格式，应该为 ISO 8601 格式'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 插入 assignment 表
        sql = '''
        INSERT INTO assignment (assignment_name, creator_tno, tasks_json, publish_date)
        VALUES (%s, %s, %s, %s)
        '''
        cur.execute(sql, (assignment_name, creator_tno, tasks_json, publish_date))
        assignment_id = cur.lastrowid  # 获取刚刚插入的 assignment ID

        # 将选定的班级插入到关联表中
        for class_id in selected_classes:
            sql = '''
            INSERT INTO assignment_class (assignment_id, class_id)
            VALUES (%s, %s)
            '''
            cur.execute(sql, (assignment_id, class_id))

        conn.commit()
        return jsonify({'message': '作业创建成功'}), 201
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/getTeacherAssignments', methods=['GET'])
def getTeacherAssignments():
    tno = request.args.get('tno')
    if not tno:
        return jsonify({'error': '缺少教师编号 tno'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取指定教师布置的作业
        cur.execute('''
        SELECT a.assignment_id, a.assignment_name, a.tasks_json, a.publish_date
        FROM assignment a
        WHERE a.creator_tno = %s
        ORDER BY a.publish_date DESC
        ''', (tno,))
        assignments = cur.fetchall()
        
        assignment_details = []
        for assignment in assignments:
            assignment_info = {
                'assignment_id': assignment[0],
                'assignment_name': assignment[1],
                'tasks_json': assignment[2],
                'publish_date': assignment[3]
            }
            assignment_details.append(assignment_info)
            
        return jsonify(assignment_details), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/deleteAssignment', methods=['POST'])
@admin_required
def delete_assignment():
    assignment_id = request.json.get('assignment_id')
    if not assignment_id:
        return jsonify({'error': '缺少作业编号 assignment_id'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 先删除 student_assignment_submission 中的相关记录
        cur.execute('''
        DELETE FROM student_assignment_submission
        WHERE assignment_id = %s
        ''', (assignment_id,))

        # 再删除 assignment_class 中的相关记录
        cur.execute('''
        DELETE FROM assignment_class
        WHERE assignment_id = %s
        ''', (assignment_id,))

        # 最后删除 assignment 表中的记录
        cur.execute('''
        DELETE FROM assignment
        WHERE assignment_id = %s
        ''', (assignment_id,))

        conn.commit()
        return jsonify({'message': '作业删除成功'}), 200
    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



# 获取实训详情
@app.route('/getAssignmentDetails', methods=['GET'])
def get_assignment_details():
    assignment_id = request.args.get('assignment_id')
    if not assignment_id:
        return jsonify({'error': '缺少作业ID'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取作业基本信息
        cur.execute('''
        SELECT a.assignment_name, a.tasks_json, a.publish_date, a.creator_tno, t.name
        FROM assignment a
        LEFT JOIN teacher t ON a.creator_tno = t.tno
        WHERE a.assignment_id = %s
        ''', (assignment_id,))
        assignment_info = cur.fetchone()
        if not assignment_info:
            return jsonify({'error': '未找到指定作业'}), 404
        
        assignment_details = {
            'assignment_name': assignment_info[0],
            'tasks_json': assignment_info[1],
            'publish_date': assignment_info[2],
            'creator_tno': assignment_info[3],
            'creator_name': assignment_info[4],
            'student_submissions': []
        }

        # 获取参与该作业的学生的提交情况
        cur.execute('''
        SELECT sas.sno, sas.answers, sas.score, sas.submission_date, s.name, s.major
        FROM student_assignment_submission sas
        LEFT JOIN student s ON sas.sno = s.sno
        WHERE sas.assignment_id = %s
        ORDER BY sas.score DESC, sas.submission_date DESC
        ''', (assignment_id,))
        student_submissions = cur.fetchall()
        for submission_info in student_submissions:
            submission_details = {
                'sno': submission_info[0],
                'answers': submission_info[1],
                'score': submission_info[2],
                'submission_date': submission_info[3],
                'name': submission_info[4],
                'major': submission_info[5]
            }
            assignment_details['student_submissions'].append(submission_details)
        
        return jsonify(assignment_details), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()


        
# 教师创建作业
@app.route('/createContest', methods=['POST'])
#@token_required
def submit_contest():
    data = request.get_json()
    contest_name = data.get('contestName')
    creator_name = data.get('creatorName')
    question_json = data.get('questionJson')
    question_type = data.get('questionType')
    publish_date = data.get('publishDate')
    selected_classes = data.get('selectedClasses')

    # 检查必填字段
    if not contest_name or not question_json or not question_type or not publish_date:
        return jsonify({'error': '缺少必填字段'}), 400

    # 检查日期格式
    try:
        from datetime import datetime
        publish_date = datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        return jsonify({'error': '无效的日期格式，应该为 ISO 8601 格式'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 插入 contest 表
        sql = '''
        INSERT INTO contest (creator_tno,contest_name, question_json, question_type, publish_date)
        VALUES (%s, %s, %s, %s, %s)
        '''
        cur.execute(sql, (creator_name,contest_name, question_json, question_type, publish_date))
        contest_id = cur.lastrowid  # 获取刚刚插入的 contest ID

        # 将选定的班级插入到关联表中
        for class_id in selected_classes:
            sql = '''
            INSERT INTO contest_class (contest_id, class_id)
            VALUES (%s, %s)
            '''
            cur.execute(sql, (contest_id, class_id))

        conn.commit()
        return jsonify({'message': '题目发布成功'}), 201
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



@app.route('/getTeacherActivities', methods=['GET'])
def get_teacher_activities():
    tno = request.args.get('tno')
    if not tno:
        return jsonify({'error': '缺少教师编号tno'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取指定教师创建的活动
        cur.execute('''
        SELECT a.activity_id, a.activity_name, a.description, a.created_date
        FROM activity a
        WHERE a.creator_tno = %s
        ORDER BY a.created_date DESC
        ''', (tno,))
        activities = cur.fetchall()
        
        activity_details = []
        for activity in activities:
            activity_info = {
                'activity_id': activity[0],
                'activity_name': activity[1],
                'description': activity[2],
                'created_date': activity[3]
            }
            activity_details.append(activity_info)
            
        return jsonify(activity_details), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()
@app.route('/getTeacherContests', methods=['GET'])
def getTeacherContests():
    tno = request.args.get('tno')
    if not tno:
        return jsonify({'error': '缺少教师编号tno'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取指定教师创建的竞赛
        cur.execute('''
        SELECT c.contest_id, c.contest_name, c.question_json, c.question_type, c.publish_date
        FROM contest c
        WHERE c.creator_tno = %s
        ORDER BY c.publish_date DESC
        ''', (tno,))
        contests = cur.fetchall()
        
        contest_details = []
        for contest in contests:
            contest_info = {
                'contest_id': contest[0],
                'contest_name': contest[1],
                'question_json': contest[2],
                'question_type': contest[3],
                'publish_date': contest[4]
            }
            contest_details.append(contest_info)
            
        return jsonify(contest_details), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()
@app.route('/deleteContest', methods=['POST'])
@admin_required
def deleteContest():
    data = request.get_json()
    contest_id = data.get('contest_id')

    if not contest_id:
        return jsonify({'error': '缺少竞赛编号contest_id'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 删除student_contest_answers表中与contest_id相关的记录
        cur.execute('DELETE FROM student_contest_answers WHERE contest_id = %s', (contest_id,))
        
        # 删除contest_class表中与contest_id相关的记录
        cur.execute('DELETE FROM contest_class WHERE contest_id = %s', (contest_id,))
        
        # 删除contest表中与contest_id相关的记录
        cur.execute('DELETE FROM contest WHERE contest_id = %s', (contest_id,))
        conn.commit()
        
        if cur.rowcount == 0:
            return jsonify({'error': '竞赛不存在或已删除'}), 404
        
        return jsonify({'message': '竞赛删除成功'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



# 教师创建活动
@app.route('/createActivity', methods=['POST'])
def create_activity():
    data = request.get_json()
    activity_name = data.get('activity_name')
    creator_tno = data.get('creator_tno')
    description = data.get('description')
    # created_date = data.get('created_date')
    selected_classes = data.get('selectedClasses') # 获取选定的班级列表
    from datetime import datetime
    created_date = datetime.now()

    # 检查必填字段
    if not activity_name or not creator_tno or not created_date:
        return jsonify({'error': '缺少必填字段'}), 400

    # 检查日期格式
    # try:
    #     from datetime import datetime
    #     created_date = datetime.strptime(created_date, '%Y-%m-%d').date()
    # except ValueError:
    #     return jsonify({'error': '无效的日期格式，应该为 YYYY-MM-DD'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        sql = '''
        INSERT INTO activity (activity_name, creator_tno, description, created_date)
        VALUES (%s, %s, %s, %s)
        '''
        cur.execute(sql, (activity_name, creator_tno, description, created_date))
        activity_id = cur.lastrowid # 获取刚刚插入的活动ID

        # 将选定的班级插入到关联表中
        for class_id in selected_classes:
            sql = '''
            INSERT INTO activity_classes (activity_id, class_id)
            VALUES (%s, %s)
            '''
            cur.execute(sql, (activity_id, class_id))

        conn.commit()
        return jsonify({'message': '活动创建成功'}), 201
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()




# 获取 classes 表的数据并转换成字典
def get_class_dict():
    conn = get_db_connection()
    if conn is None:
        return None, '数据库连接失败'

    cur = conn.cursor()
    try:
        cur.execute('SELECT ClassID, ClassName FROM classes;')
        classes = cur.fetchall()
        class_dict = {cls[1]: cls[0] for cls in classes}
        print(class_dict)
        return class_dict, None
    except Exception as e:
        return None, str(e)
    finally:
        cur.close()
        conn.close()



# 一键导入学生
@app.route('/importStudents', methods=['POST'])
def importStudents():
    students = request.json.get('students')
    if not students or not isinstance(students, list):
        return jsonify({'success': False, 'message': '缺少学生数据或数据格式错误'}), 400

    class_dict, error = get_class_dict()
    if error:
        return jsonify({'error': error}), 500

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        for student in students:
            sno = student.get('学号')
            name = student.get('姓名')
            gender = student.get('性别')
            classname = student.get('班级')

            if not (sno and name and classname):
                return jsonify({'success': False, 'message': '缺少必填字段'}), 400

            class_id = class_dict.get(classname)
            if not class_id:
                return jsonify({'success': False, 'message': f'找不到班级 {classname} 对应的ClassID'}), 400

            # 插入学生数据
            sql = '''
                INSERT INTO student (sno, name, gender, major, ClassID)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                gender = VALUES(gender),
                major = VALUES(major),
                ClassID = VALUES(ClassID);
            '''
            cur.execute(sql, (sno, name, gender, classname, class_id))
            print()

        conn.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/deleteActivity', methods=['POST'])
@admin_required
def delete_activity():
    data = request.get_json()
    activity_id = data.get('activity_id')

    if not activity_id:
        return jsonify({'error': '缺少任务编号activity_id'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 删除student_assignment表中与activity_id相关的记录
        cur.execute('DELETE FROM student_assignment WHERE activity_id = %s', (activity_id,))
        
        # 删除activity_classes表中与activity_id相关的记录
        cur.execute('DELETE FROM activity_classes WHERE activity_id = %s', (activity_id,))
        
        # 删除activity表中与activity_id相关的记录
        cur.execute('DELETE FROM activity WHERE activity_id = %s', (activity_id,))
        conn.commit()
        
        if cur.rowcount == 0:
            return jsonify({'error': '任务不存在或已删除'}), 404
        
        return jsonify({'message': '任务删除成功'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()


        
@app.route('/getContestDetails', methods=['GET'])
def get_contest_details():
    contest_id = request.args.get('contest_id')
    if not contest_id:
        return jsonify({'error': '缺少竞赛ID'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取竞赛基本信息
        cur.execute('''
        SELECT c.contest_name, c.question_json, c.question_type, c.publish_date, c.creator_tno, s.name, s.major
        FROM contest c
        LEFT JOIN student_contest_answers sca ON c.contest_id = sca.contest_id
        LEFT JOIN student s ON sca.sno = s.sno
        WHERE c.contest_id = %s
        ''', (contest_id,))
        contest_info = cur.fetchone()
        if not contest_info:
            return jsonify({'error': '未找到指定竞赛'}), 404
        
        contest_details = {
            'contest_name': contest_info[0],
            'question_json': contest_info[1],
            'question_type': contest_info[2],
            'publish_date': contest_info[3],
            'creator_tno': contest_info[4],
            'student_answers': []
        }

        # 获取参与该竞赛的学生的答题情况
        cur.execute('''
        SELECT sca.sno, sca.question_type, sca.answers, sca.score, sca.submission_date, s.name, s.major
        FROM student_contest_answers sca
        LEFT JOIN student s ON sca.sno = s.sno
        WHERE sca.contest_id = %s
        ORDER BY sca.score DESC, sca.submission_date DESC
        ''', (contest_id,))
        student_answers = cur.fetchall()
        for answer_info in student_answers:
            answer_details = {
                'sno': answer_info[0],
                'question_type': answer_info[1],
                'answers': answer_info[2],
                'score': answer_info[3],
                'submission_date': answer_info[4],
                'name': answer_info[5],
                'major': answer_info[6]
            }
            contest_details['student_answers'].append(answer_details)
        
        return jsonify(contest_details), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



# 获取活动详情，包括作业提交情况
@app.route('/getActivityDetails', methods=['GET'])
def get_activity_details():
    activity_id = request.args.get('activity_id')
    if not activity_id:
        return jsonify({'error': '缺少活动ID'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        # 获取活动基本信息
        cur.execute('''
        SELECT activity_name, description, created_date, creator_tno
        FROM activity
        WHERE activity_id = %s
        ''', (activity_id,))
        activity_info = cur.fetchone()
        if not activity_info:
            return jsonify({'error': '未找到指定活动'}), 404
        
        activity_details = {
            'activity_name': activity_info[0],
            'description': activity_info[1],
            'created_date': activity_info[2],
            'creator_tno': activity_info[3],
            'student_assignments': []
        }

        # 获取参与该活动的学生的作业情况
        cur.execute('''
        SELECT sa.assignment_id, sa.content, sa.submission_date, s.name AS student_name
        FROM student_assignment sa
        JOIN student s ON sa.sno = s.sno
        WHERE sa.activity_id = %s
     
        ''', (activity_id,))
        student_assignments = cur.fetchall()
        for assignment_info in student_assignments:
            assignment_details = {
                'assignment_id': assignment_info[0],
                'content': assignment_info[1],
                'submission_date': assignment_info[2],
                'student_name': assignment_info[3]
            }
            activity_details['student_assignments'].append(assignment_details)
        print(activity_details)
        return jsonify(activity_details), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# 通过竞赛ID获取竞赛详情
@app.route('/getContestDetailsById', methods=['GET'])
def get_contest_details_by_id():
    contest_id = request.args.get('contest_id')
    if not contest_id:
        return jsonify({'error': '缺少竞赛编号'}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': '数据库连接失败'}), 500

        cur = conn.cursor()

        # 查询竞赛详情
        cur.execute('SELECT contest_id, contest_name, publish_date, question_type, question_json FROM contest WHERE contest_id = %s', (contest_id,))
        contest = cur.fetchone()

        if not contest:
            return jsonify({'error': '找不到该竞赛'}), 404

        # 构建竞赛详情字典
        contest_details = {
            'contest_id': contest[0],
            'contest_name': contest[1],
            'publish_date': contest[2],
            'question_type': contest[3],
            'question_json': contest[4]
        }

        return jsonify(contest_details), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        if 'cur' in locals() and cur is not None:
            cur.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

# 通过活动ID获取活动
@app.route('/getActivityDetailsById', methods=['GET'])
def get_activity_details_by_id():
    activity_id = request.args.get('activity_id')
    if not activity_id:
        return jsonify({'error': '缺少活动编号'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 查询活动详情
        cur.execute('SELECT activity_id, activity_name, description, created_date FROM activity WHERE activity_id = %s', (activity_id,))
        activity = cur.fetchone()

        if not activity:
            return jsonify({'error': '找不到该活动'}), 404

        # 构建活动详情字典
        activity_details = {
            'activity_id': activity[0],
            'activity_name': activity[1],
            'description': activity[2],
            'created_date': activity[3]
        }

        return jsonify(activity_details), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()



# 获取所有班级
@app.route('/getClasses', methods=['GET'])
def get_classes():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': '数据库连接失败'}), 500

    cur = conn.cursor()
    try:
        cur.execute("SELECT ClassID, ClassName FROM classes ORDER BY GradeID,MajorID DESC")
        classes = cur.fetchall()
        class_list = [{'ClassID': c[0], 'ClassName': c[1]} for c in classes]
        print(class_list)
        return jsonify(class_list), 200
    except Exception as e:
        print(e)
        return jsonify({'error': '数据库错误', 'details': str(e)}), 500
    finally:
        cur.close()
        conn.close()