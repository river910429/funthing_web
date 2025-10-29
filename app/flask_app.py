# coding=utf-8
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
import json, pickle
import os, platform, re, hashlib
from datetime import timedelta, datetime
from stt_service_api import taiwanese_recognize
from ttp_service_api import process as tlpa_trans
# from tts_service_api import tts
from tts_service_api import tts
import random

app = Flask(__name__)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.secret_key = os.urandom(24)
APP_ROOT = os.path.join(os.getcwd())
APP_TEMP = os.path.join(APP_ROOT, "temp")
if not os.path.exists(APP_TEMP):
    os.makedirs(APP_TEMP)

AUDIO_DIR = os.path.join('static', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

class SQL(): 
    def __init__(self, mode="stu"):
        self.db_settings = {"host": "140.116.245.150",
							#3333 --> 3306
                            "port": 3306,
							#"user": "root",
                            "user": "funthing_teach_web_root",
							#"password": "wmmkscsie",
                            "password": "Funthing_teach_web_01",
                            #"db": "funthing_teach",
							"db": "funthing_teach_old_ver",
                            "charset": "utf8"}
        try:
            self.conn = pymysql.connect(**self.db_settings)
        except Exception as e:
            print(e)
    
    def __del__(self):
        self.conn.close()

    def connect(self):
        try:
            self.conn = pymysql.connect(**self.db_settings)
        except Exception as e:
            print(e)

    def close(self):
        self.conn.close()

    def runsql(self, str):
        with self.conn.cursor() as cursor:
            cursor.execute(str)

    def validate_account(self, identity, account):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM " + identity + " WHERE account = '{}';".format(account))
            result = cursor.fetchall()
            print(result)
            if result != ():
                return True
            else:
                return False

    def validate_password(self, account, pwd):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Password WHERE account = '{}' and pwd = '{}';".format(account, pwd))
            result = cursor.fetchall()
            if result != ():
                return True
            else:
                return False

    def get_name(self, identity, account):
        with self.conn.cursor() as cursor:
            try:
                if identity == "Student":
                    cursor.execute("SELECT student_name FROM Student WHERE account='{}'".format(account))
                    result = cursor.fetchone()
                    name = result[0]
                # "SELECT teacher_name FROM Teacher WHERE account='{}'".format(account)
                
                return name
            except Exception as e:
                return ""

    def set_name(self, identity, account, name):
        with self.conn.cursor() as cursor:
            try:
                if identity == "Student":
                    cursor.execute("UPDATE Student SET student_name='{}' WHERE account='{}'".format(name, account))
                    self.conn.commit()
                # "UPDATE Teacher SET teacher_name='{}' WHERE account='{}'".format(name, account)
                
                return True
            except Exception as e:
                return False

    def init_stu_info(self, account, class_id, password):
        with self.conn.cursor() as cursor:
            cursor.execute("insert into Student (account, class_id, student_name) values ({}, {}, '');".format(account, class_id))
            cursor.execute("select student_id from Student where account = {};".format(account))
            student_id = cursor.fetchone()[0]
            cursor.execute("insert into Stu_info(student_id, level, acc_score, equip_now, equip_1_gain, equip_2_gain, equip_3_gain, equip_4_gain, equip_5_gain, equip_6_gain, equip_7_gain) values ({}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);"
                .format(student_id))
            cursor.execute("insert into Password (account, pwd) values ({}, {});".format(account, password))

    def get_stu_level_score(self, stu_id):
        with self.conn.cursor() as cursor:
            cursor.execute("select level, acc_score from Stu_info where student_id = '{}'".format(stu_id))
            result = cursor.fetchone()
            prev_level = result[0]
            prev_score = result[1]
        return prev_level, prev_score

    def upload_score(self, stu_id, score, level):
        with self.conn.cursor() as cursor:
            # equipment_field = 'equip_{}_gain'.format(equipment)
            command = "UPDATE Stu_info SET acc_score='{}', level='{}' WHERE student_id='{}'".format(score, level, stu_id)
            print(command)
            cursor.execute(command)
            try:
                self.conn.commit()
                return True
            except Exception as e:
                return False

    def update_equipment_gain(self, stu_id, equipment):
        with self.conn.cursor() as cursor:
            equipment_field = 'equip_{}_gain'.format(equipment)
            command = "UPDATE Stu_info SET {}='{}' WHERE student_id='{}'".format(equipment_field, 1, stu_id)
            print(command)
            cursor.execute(command)
            try:
                self.conn.commit()
                return True
            except Exception as e:
                return False
    
    def get_student_id(self, account):
        with self.conn.cursor() as cursor:
            cursor.execute("select Student_id from Student where account = '{}'".format(account))
            result = cursor.fetchone()
            stu_id = result[0]
        return stu_id

    # def get_class_leaderboard(self, class_name):
    #     with self.conn.cursor() as cursor:
    #         cursor.execute("SELECT RANK() OVER(ORDER BY s1.acc_score DESC) AS r, s2.account, s2.student_name, s1.level, s1.acc_score FROM Stu_info AS s1 JOIN Student AS s2 ON s1.student_id = s2.student_id WHERE s2.account LIKE '{}%';".format(class_name))
    #         data = cursor.fetchall()
    #         print(data)
    #     return data

    # def get_school_leaderboard(self):
    #     with self.conn.cursor() as cursor:
    #         cursor.execute("SELECT RANK() OVER(ORDER BY s1.acc_score DESC) AS r, s2.account, s2.student_name, s1.level, s1.acc_score FROM Stu_info AS s1 JOIN Student AS s2 ON s1.student_id = s2.student_id;")
    #         data = cursor.fetchall()
    #         print(data)
    #     return data

    def get_school_leaderboard(self):
        sql = """
        SELECT r, account, student_name, level, acc_score
        FROM (
            SELECT
                @rownum := @rownum + 1 AS rownum,
                @rank := IF(@prev_score = s1.acc_score, @rank, @rownum) AS r,
                @prev_score := s1.acc_score,
                s2.account,
                s2.student_name,
                s1.level,
                s1.acc_score
            FROM Stu_info AS s1
            JOIN Student  AS s2 ON s1.student_id = s2.student_id
            CROSS JOIN (SELECT @rownum := 0, @rank := 0, @prev_score := NULL) vars
            ORDER BY s1.acc_score DESC, s2.student_name ASC
        ) t
        ORDER BY r ASC, acc_score DESC, student_name ASC;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
            print(data)
        return data

    def get_class_leaderboard(self, class_name):
        sql = """
        SELECT r, account, student_name, level, acc_score
        FROM (
            SELECT
                @rownum := @rownum + 1 AS rownum,
                @rank := IF(@prev_score = s1.acc_score, @rank, @rownum) AS r,
                @prev_score := s1.acc_score,
                s2.account,
                s2.student_name,
                s1.level,
                s1.acc_score
            FROM Stu_info AS s1
            JOIN Student  AS s2 ON s1.student_id = s2.student_id
            CROSS JOIN (SELECT @rownum := 0, @rank := 0, @prev_score := NULL) vars
            WHERE s2.account LIKE %s
            ORDER BY s1.acc_score DESC, s2.student_name ASC
        ) t
        ORDER BY r ASC, acc_score DESC, student_name ASC;
        """
        like_prefix = f"{class_name}%"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (like_prefix,))
            data = cursor.fetchall()
            print(data)
        return data



    def get_stu_equip_now(self, stu_id):
        with self.conn.cursor() as cursor:
            cursor.execute("select equip_now from Stu_info where student_id = '{}'".format(stu_id))
            result = cursor.fetchone()
            wear_now = result[0]
        return wear_now

    def get_stu_equip_gain_info(self, stu_id):
        with self.conn.cursor() as cursor:
            cursor.execute("select equip_1_gain, equip_2_gain, equip_3_gain, equip_4_gain, equip_5_gain, equip_6_gain, equip_7_gain from Stu_info where student_id = '{}'".format(stu_id))
            result = cursor.fetchone()
            # wear_now = result[0]
        return result

    def update_wear_now(self, equip_id, stu_id):
        with self.conn.cursor() as cursor:
            command = "UPDATE Stu_info SET equip_now='{}' WHERE student_id='{}'".format(equip_id, stu_id)
            print(command)
            cursor.execute(command)
            try:
                self.conn.commit()
                return True
            except Exception as e:
                return False

    ##############################
    #        ta_template         #
    ##############################

    def get_classgame(self, class_name, game_name):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT {} FROM Class WHERE class_name = {};".format(game_name, class_name))
            data = cursor.fetchall()
            print(data[0][0])

        return data[0][0]

    def update_classgame(self, class_name, game_name, course_id):
        with self.conn.cursor() as cursor:
            cursor.execute("UPDATE Class SET {}={} WHERE class_name={};".format(game_name, course_id, class_name))
            data = cursor.fetchall()
            print(data)

        return data

    ##############################
    #         ta_course          #
    ##############################
    def get_course(self, search_name):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT c.course_id, c.course_name, COUNT(w.word_id), c.ts FROM Course AS c LEFT JOIN Word AS w ON c.course_id = w.course_id WHERE c.course_name LIKE '%{}%' GROUP BY c.course_id ORDER BY c.ts DESC;".format(search_name))
            data = cursor.fetchall()
            print(data)

        result = list()
        for i, item in enumerate(data):
            temp = {
                "id": item[0],
                "number": i,
                "name": item[1],
                "words": item[2],
                "lastmodify": item[3].strftime("%Y-%m-%d")
            }
            result.append(temp)
        return result

    def update_course(self, course_id, update_name):
        with self.conn.cursor() as cursor:
            print(update_name, course_id)
            cursor.execute("UPDATE Course SET course_name='{}' WHERE course_id={};".format(update_name, course_id))
            data = cursor.fetchall()
            print(data)

        return self.get_course("")
    
    def insert_course(self, insert_name):
        with self.conn.cursor() as cursor:
            print(insert_name)
            cursor.execute("INSERT INTO Course (course_name) values ('{}');".format(insert_name))
            data = cursor.fetchall()
            print(data)

        return self.get_course("")

    def delete_course(self, delete_id):
        with self.conn.cursor() as cursor:
            print(delete_id)
            cursor.execute("DELETE FROM Course WHERE course_id={};".format(delete_id))
            data = cursor.fetchall()
            print(data)

        return self.get_course("")

    def update_modifyts(self, course_id):
        with self.conn.cursor() as cursor:
            print(course_id)
            cursor.execute("UPDATE Course SET ts=now() WHERE course_id={};".format(course_id))
            data = cursor.fetchall()
            print(data)
            
        return data

    ##############################
    #      ta_course_vocab       #
    ##############################
    def get_course_vocab(self, course_id, search_word):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Word WHERE course_id = {} AND ch_word LIKE '%{}%' ORDER BY ts DESC;".format(course_id, search_word))
            data = cursor.fetchall()
            print(data)

        result = list()
        for i, item in enumerate(data):
            temp = {
                "id": item[0],
                "number": i,
                "CHword": item[2],
                "TWword": item[3],
                "TLPA": item[4],
            }
            result.append(temp)
        return result

    def update_course_vocab(self, course_id, word_id, update_CHword, update_TWword, update_TLPA):
        with self.conn.cursor() as cursor:
            print(word_id, update_CHword, update_TWword, update_TLPA)
            cursor.execute("UPDATE Word SET ch_word='{}', tw_word='{}', tlpa='{}' WHERE word_id={};".format(update_CHword, update_TWword, update_TLPA, word_id))
            data = cursor.fetchall()
            print(data)

        return self.get_course_vocab(course_id, "")

    def insert_course_vocab(self, course_id, insert_CHword, insert_TWword, insert_TLPA):
        with self.conn.cursor() as cursor:
            print(course_id, insert_CHword, insert_TWword, insert_TLPA)
            cursor.execute("INSERT INTO Word (course_id, ch_word, tw_word, tlpa) values ('{}', '{}', '{}', '{}');".format(course_id, insert_CHword, insert_TWword, insert_TLPA))
            data = cursor.fetchall()
            print(data)

        return self.get_course_vocab(course_id, "")

    def delete_course_vocab(self, course_id, delete_id):
        with self.conn.cursor() as cursor:
            print(delete_id)
            cursor.execute("DELETE FROM Word WHERE word_id={};".format(delete_id))
            data = cursor.fetchall()
            print(data)

        return self.get_course_vocab(course_id, "")
    
    # student register
    def create_student(self, account: str, class_id: int, password: str, name: str = "") -> bool:
        """
        建立新學生：
        - Student(account, class_id, student_name)
        - Stu_info(student_id, level=0, acc_score=0, equip_now=0, equip_1~7_gain=0)
        - Password(account, pwd)
        全部成功才 commit；任一失敗 rollback。
        """
        try:
            with self.conn.cursor() as cursor:
                # 確認帳號是否已存在（Student 或 Password 任一處有就視為存在）
                cursor.execute("SELECT 1 FROM Student WHERE account=%s LIMIT 1;", (account,))
                if cursor.fetchone():
                    return False
                cursor.execute("SELECT 1 FROM Password WHERE account=%s LIMIT 1;", (account,))
                if cursor.fetchone():
                    return False

                # 建立 Student
                cursor.execute(
                    "INSERT INTO Student (account, class_id, student_name) VALUES (%s, %s, %s);",
                    (account, class_id, name or "")
                )

                # 取得 student_id
                cursor.execute("SELECT student_id FROM Student WHERE account=%s;", (account,))
                row = cursor.fetchone()
                if not row:
                    self.conn.rollback()
                    return False
                student_id = row[0]

                # 建立 Stu_info（全部 0）
                cursor.execute("""
                    INSERT INTO Stu_info
                      (student_id, level, acc_score, equip_now,
                       equip_1_gain, equip_2_gain, equip_3_gain, equip_4_gain,
                       equip_5_gain, equip_6_gain, equip_7_gain)
                    VALUES
                      (%s, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
                """, (student_id,))

                # 建立 Password（沿用你現有明文比對）
                cursor.execute("INSERT INTO Password (account, pwd) VALUES (%s, %s);", (account, password))

            self.conn.commit()
            return True
        except Exception as e:
            print("create_student error:", e)
            self.conn.rollback()
            return False
    
    # ta register
    def create_teacher(self, account: str, password: str, name: str = "") -> bool:
        """
        建立新教師：
        - Teacher(account, teacher_name)
        - Password(account, pwd)
        全部成功才 commit；任一失敗 rollback。
        """
        try:
            with self.conn.cursor() as cursor:
                # 檢查 Teacher 或 Password 是否已存在相同帳號
                cursor.execute("SELECT 1 FROM Teacher WHERE account=%s LIMIT 1;", (account,))
                if cursor.fetchone():
                    return False
                cursor.execute("SELECT 1 FROM Password WHERE account=%s LIMIT 1;", (account,))
                if cursor.fetchone():
                    return False

                # 新增 Teacher
                cursor.execute(
                    "INSERT INTO Teacher (teacher_name, account) VALUES (%s, %s);",
                    (name or "", account)
                )

                # 新增 Password
                cursor.execute("INSERT INTO Password (account, pwd) VALUES (%s, %s);", (account, password))

            self.conn.commit()
            return True
        except Exception as e:
            print("create_teacher error:", e)
            self.conn.rollback()
            return False
    def get_teacher_id(self, account: str):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT teacher_id FROM Teacher WHERE account=%s;", (account,))
            result = cursor.fetchone()
            return result[0] if result else None


def class_code_to_class_id(db: SQL, class_code: str):
    try:
        with db.conn.cursor() as cursor:
            cursor.execute("SELECT class_id FROM Class WHERE class_name=%s LIMIT 1;", (class_code,))
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        print("class_code_to_class_id error:", e)
        return None



@app.before_request
def before_request():
    if request.path not in ["/", "/branch", "/login/stu", "/login/ta", "/verifying", "/test_reset", "/update_password", "/register/stu", "/register/ta"] \
        and len(request.path.split('.')) == 1:
        if session.get('account') is None:
            return redirect("/branch")

# @app.after_request
# def add_header(response):
#     if request.path.startswith('/static/'):
#         response.cache_control.public = True
#         response.cache_control.max_age = 60 * 60 * 24 * 30  # 30 天
#         response.headers['Connection'] = 'keep-alive'
#     return response

@app.route('/redirect')
def my_redirect():
    r_type = request.args.get('r_type')
    print(r_type)
    if r_type == "equip":
        if session.get('pre_page_equip'):
            return json.dumps({
                "status": "success",
                "url": session.get('pre_page_equip')
            })
    elif r_type == "lgame":
        if session.get('pre_page_lgame'):
            return json.dumps({
                "status": "success",
                "url": session.get('pre_page_lgame')
            })

    return json.dumps({
        "status": "error",
        "url": ""
    })
    
# def add_new_stu():
#     db_cursor = SQL()
#     for i in range(1, 41):
#         account = 30200+i
#         class_id = 2
#         password = account
#         print(account, class_id, password)
#         db_cursor.init_stu_info(account = account, class_id = class_id, password = password)
#     db_cursor.conn.commit()

@app.route('/test_reset')
def test_reset():
    db_cursor = SQL()
    sql = "UPDATE Stu_info SET level=0, acc_score=0, equip_now=0, equip_1_gain=0, equip_2_gain=0, equip_3_gain=0, equip_4_gain=0, equip_5_gain=0, equip_6_gain=0, equip_7_gain=0 WHERE student_id=1;"
    db_cursor.runsql(sql)
    db_cursor.conn.commit()
    return "reset success", 200

# @app.route('/update_password')
# def update_password():
#     import random
#     import string
#     import csv
#     table = list()
#     characters = string.ascii_letters + string.digits
#     db_cursor = SQL()
#     for c in range(1, 3):
#         for i in range(1, 41):
#             account = f"30{c}{i:02}"
#             password = ''.join(random.choice(characters) for i in range(8))
#             table.append([account, password])
#             sql = f"UPDATE Password SET pwd='{password}' WHERE account='{account}';"
#             db_cursor.runsql(sql)
    
#     with open('pwd.csv', 'w', newline='', encoding='utf-8') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerows(table)
#     db_cursor.conn.commit()

#     return "update success", 200

@app.route('/')
@app.route('/taigi_game')
def entrance():
    return render_template('entrance.html')

@app.route('/branch')
def branch():
    return render_template('branch.html')

@app.route('/login/stu')
def stu_login():
    session['identity'] = "Student"
    return render_template('student_login.html')

@app.route('/login/ta')
def ta_login():
    session['identity'] = "Teacher"
    return render_template('teacher_login.html')

@app.route('/verifying', methods=['POST'])
def verifying():
    db_cursor = SQL()
    try:
        obj = request.get_json()
        account = obj['account']
        pwd = obj['pwd']
        valid_account = db_cursor.validate_account(session['identity'], account)
        if valid_account: 
            valid_pwd = db_cursor.validate_password(account, pwd)
        else:
            valid_pwd = False

        if valid_account and valid_pwd:
            session['loggin'] = True
            session['account'] = account

            if session['identity'] == "Student":
                student_id = db_cursor.get_student_id(account)
                name = db_cursor.get_name(session['identity'], account)
                session['stu_id'] = student_id
                print(session['loggin'], session['account'], session['stu_id'], name)
                if name == "":
                    return json.dumps({
                        "status": "success",
                        "url": "/login/name"
                    })
                else:
                    return json.dumps({
                        "status": "success",
                        "url": "/home/stu"
                    })
            if session['identity'] == "Teacher":
                print(session['loggin'], session['account'])
                return json.dumps({
                    "status": "success",
                    "url": "/home/ta"
                })
        else:
            return json.dumps({
                "status": "error"
            })
    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error"
        })

@app.route('/login/name')
def login_name():
    return render_template('login_name.html')

@app.route('/login/name', methods=['POST'])
def login_name_post():
    db_cursor = SQL()
    obj = request.get_json()
    name = obj['name']
    db_cursor.set_name(session['identity'], session['account'], name)
    return json.dumps({
        "status": "success",
        "url": "/home/stu"
    })

@app.route('/home/stu')
def stu_home():
    session['pre_page_equip'] = request.url
    return render_template('student_home.html')

@app.route('/stu/game')
def stu_game():
    session['pre_page_equip'] = request.url
    session['pre_page_lgame'] = request.url
    return render_template('student_game.html')

@app.route('/stu/practice')
def stu_practice():
    session['pre_page_equip'] = request.url
    return render_template('student_practice.html')

@app.route('/stu/leaderboard')
def stu_leaderboard():
    session['pre_page_equip'] = request.url
    return render_template('student_leaderboard.html')

@app.route('/leaderboard_class_query', methods=['GET'])
def leaderboard_class_query():
    db_cursor = SQL()
    stu_account = session['account']
    print(stu_account)
    result = db_cursor.get_class_leaderboard(stu_account[0:3])
    
    return json.dumps({
        "status": "success",
        "data": result,
        "target_idx": stu_account
    })

@app.route('/leaderboard_school_query', methods=['GET'])
def leaderboard_school_query():
    db_cursor = SQL()
    stu_account = session['account']
    print(stu_account)
    result = db_cursor.get_school_leaderboard()

    return json.dumps({
        "status": "success",
        "data": result,
        "target_idx": stu_account
    })

@app.route('/poster/catch_egg')
def stu_poster_catch():
    session['pre_page_equip'] = request.url
    session['pre_page_lgame'] = request.url
    return render_template('student_poster_catch.html')

@app.route('/poster/map')
def stu_poster_map():
    session['pre_page_equip'] = request.url
    session['pre_page_lgame'] = request.url
    return render_template('student_poster_map.html')

@app.route('/poster/fruit_cutter')
def stu_poster_fruit():
    session['pre_page_equip'] = request.url
    session['pre_page_lgame'] = request.url
    return render_template('student_poster_fruit.html')

@app.route('/poster/flipping_card')
def stu_poster_card():
    session['pre_page_equip'] = request.url
    session['pre_page_lgame'] = request.url
    return render_template('student_poster_card.html')

@app.route('/home/ta')
def ta_home():
    return render_template('teacher_home.html')

@app.route('/ta/template')
def ta_template():
    return render_template('teacher_template.html')

@app.route('/ta/leaderboard')
def ta_leaderboard():
    return render_template('teacher_leaderboard.html')

@app.route('/leaderboard_ta_query', methods=['POST'])
def leaderboard_ta_query():
    db_cursor = SQL()
    class_name = request.form['input_id']
    error_msg = ""
    target_idx = [9999999]
    print(class_name)
    if class_name.strip() == "":
        result = []
        error_msg = ""
    else:
        try:
            result = db_cursor.get_class_leaderboard(class_name)
            if len(result) == 0:
                error_msg = "*輸入錯誤，無此班級*"
        except:
            result = []
            error_msg = "*輸入錯誤，無此班級*"
    
    return render_template('teacher_leaderboard_result.html', data = result, target_idx = target_idx, error_msg = error_msg)

@app.route("/template/course/search", methods=['POST'])
def template_course_search():
    obj = request.get_json()
    game_name = obj["game_name"]
    class_name = session['account'][0:3]
    print(class_name, game_name)

    db_cursor = SQL()
    results = db_cursor.get_course("")
    course_id = db_cursor.get_classgame(class_name, game_name)
    return json.dumps({
        "status": "success",
        "results": results,
        "course_id": course_id
    })

@app.route("/template/course/update", methods=['POST'])
def template_course_update():
    obj = request.get_json()
    game_name = obj["game_name"]
    course_id = obj["course_id"]
    class_name = session['account'][0:3]
    print(class_name, game_name, course_id)

    db_cursor = SQL()
    db_cursor.update_classgame(class_name, game_name, course_id)
    db_cursor.conn.commit()
    return json.dumps({
        "status": "success"
    })

@app.route('/template/catch_egg')
def ta_template_catch():
    return render_template('teacher_template_catch.html')

@app.route('/template/map')
def ta_template_map():
    return render_template('teacher_template_map.html')

@app.route('/template/fruit_cutter')
def ta_template_fruit():
    return render_template('teacher_template_fruit.html')

@app.route('/template/flipping_card')
def ta_template_card():
    return render_template('teacher_template_card.html')

# game1

@app.route('/game/flipping_card_tutorial')
def card_game_tutorial():
    session['pre_page_equip'] = request.url
    course_id = request.args.get('course_id')
    print(course_id)
    return render_template('game_card_tutorial.html', course_id=course_id)

@app.route('/game/flipping_card')
def card_game():
    course_id = request.args.get('course_id')
    print(course_id)
    db_cursor = SQL()
    course_word = db_cursor.get_course_vocab(course_id, '')
    
    while len(course_word) < 8:
        course_word.extend(course_word)

    random.shuffle(course_word)
    course_word = course_word[:8]
    print(course_word)
    choose_course = {
        "gameneed": list(), 
    }
    for word in course_word:
        choose_course["gameneed"].append(word["TWword"]+"<br>"+word["TLPA"])
    return render_template('game_card.html', course = choose_course)

# game2

@app.route('/game/catch_egg_tutorial')
def catch_egg_tutorial():
    session['pre_page_equip'] = request.url
    course_id = request.args.get('course_id')
    print(course_id)
    return render_template('game_catch_egg_tutorial.html', course_id=course_id)

@app.route('/game/catch_egg')
def catch_egg():
    course_id = request.args.get('course_id')
    print(course_id)
    db_cursor = SQL()
    course_word = db_cursor.get_course_vocab(course_id, '')

    # while len(course_word) < 8:
    #     course_word.extend(course_word)

    random.shuffle(course_word)
    course_word = course_word[:8]
    print(course_word)
    choose_course = {
        "gameneed": list(), 
    }
    for word in course_word:
        choose_course["gameneed"].append(word["TWword"]+"<br>"+word["TLPA"])
    return render_template('game_catch_egg.html', course = choose_course)

# game3

@app.route('/game/fruit_cutter_tutorial')
def fruit_game_tutorial():
    session['pre_page_equip'] = request.url
    course_id = request.args.get('course_id')
    print(course_id)
    return render_template('game_fruit_cutter_tutorial.html', course_id=course_id)

@app.route('/game/fruit_cutter')
def fruit_game():
    course_id = request.args.get('course_id')
    print(course_id)
    db_cursor = SQL()
    course_word = db_cursor.get_course_vocab(course_id, '')

    while len(course_word) < 8:
        course_word.extend(course_word)

    random.shuffle(course_word)
    course_word = course_word[:8]
    print(course_word)

    choose_course = {
        "gameneed": list(), 
    }
    for word in course_word:
        choose_course["gameneed"].append(word["TWword"]+"<br>"+word["TLPA"])
    
    return render_template('game_fruit_cutter.html', course = choose_course)

# game4

@app.route('/game/map_tutorial')
def map_game_tutorial():
    session['pre_page_equip'] = request.url
    course_id = request.args.get('course_id')
    print(course_id)
    return render_template('game_map_tutorial.html', course_id=course_id)

@app.route('/game/map')
def map_game():
    course_id = request.args.get('course_id')
    print(course_id)
    db_cursor = SQL()
    course_word = db_cursor.get_course_vocab(course_id, '')

    while len(course_word) < 6:
        course_word.extend(course_word)

    random.shuffle(course_word)
    course_word = course_word[:6]
    print(course_word)

    choose_course = {
        "gameneed": list(), 
    }
    for word in course_word:
        choose_course["gameneed"].append(word["TWword"]+"<br>"+word["TLPA"])

    return render_template('game_map.html', course = choose_course)

@app.route('/game/fruit_cutter/game_result', methods = ['POST'])
@app.route('/game/flipping_card/game_result', methods = ['POST'])
@app.route('/game/map/game_result', methods = ['POST'])
@app.route('/game/catch_egg/game_result', methods = ['POST'])
@app.route('/game_result', methods = ['POST'])
def display_game_result_post():
    session["result_lst"] = request.get_json()["data"]
    print(session["result_lst"])
    return json.dumps({'status':"success"})

@app.route('/game/fruit_cutter/game_result', methods = ['GET'])
@app.route('/game/flipping_card/game_result', methods = ['GET'])
@app.route('/game/map/game_result', methods = ['GET'])
@app.route('/game/catch_egg/game_result', methods = ['GET'])
@app.route('/game_result', methods = ['GET'])
def display_game_result():
    if session.get('result_lst'):
        return render_template('game_result_page.html', data = session["result_lst"])
    else:
        return render_template('game_result_page.html', data = []) 

@app.route('/score_upload', methods = ['GET', 'POST'])
def score_uploading():
    db_cursor = SQL()
    def score_to_level(score):
        level = 0
        if score >= 50000:
            level = 5
        elif score >= 20000:
            level = 4
        elif score >= 12500:
            level = 3
        elif score >= 7500:
            level = 2
        elif score >= 2500:
            level = 1
        return level
    def check_weapon_available(score):
        weapon = 0
    
        if score >= 90000:
            weapon = 7
        elif score >= 80000:
            weapon = 6
        elif score >= 70000:
            weapon = 5
        elif score >= 60000:
            weapon = 4
        elif score >= 42500:
            weapon = 3
        elif score >= 35000:
            weapon = 2
        elif score >= 27500:
            weapon = 1
        
        return weapon

    print(session.get('account'))
    print(session.get('stu_id'))
    print(session.get('loggin'))
    score = request.form.get('score')
    upgrade = False
    if session.get('loggin') == None:
        redirect("/login/stu")
    else:
        stu_id = session.get('stu_id')
        
        prev_level, prev_score = db_cursor.get_stu_level_score(stu_id=stu_id)
        equipment_id_now = db_cursor.get_stu_equip_now(stu_id)
        equipment_info = db_cursor.get_stu_equip_gain_info(stu_id)
        
        weapon_gain_flag = False
        print(prev_score)
        print(score)
        new_score = prev_score + int(score)
        print(new_score)
        new_level = score_to_level(new_score)
        available_equipment = check_weapon_available(new_score)

        if available_equipment != 0 :
            for i in range(0, available_equipment):
                if equipment_info[i] == 0:
                    weapon_gain_flag = True
                    db_cursor.update_equipment_gain(stu_id, i+1)

        upload_status = db_cursor.upload_score(stu_id, new_score, new_level)
        
        if upload_status:
            if new_level > prev_level:
                upgrade = True
            return json.dumps({'status':upload_status, 'upgrade':upgrade, 'level':new_level, 'weapon_gain': weapon_gain_flag, 'weapon': available_equipment, 'wear_now':equipment_id_now})

@app.route('/wearing', methods = ['GET', 'POST'])
def wearing():
    db_cursor = SQL()
    equip_id = request.form.get('equip_id')
    if session.get('loggin') == None:
        redirect("/login/stu")
    else:
        stu_id = session.get('stu_id')
        status = db_cursor.update_wear_now(equip_id, stu_id)
        
        return json.dumps({'status':status})
    # print(session["account"])
    # print(session["loggin"])
    # return render_template('student_game.html')

@app.route("/save_audio", methods=['GET','POST'])
def save_audio():
    global ffmpeg_path
    audio_data = request.files["data"]
    session['now'] = datetime.now()
    date = session['now'].strftime("%Y%m%d")
    timestamp = session['now'].strftime("%H%M%S")
    print(date, timestamp)
    record_temp_path = os.path.join(APP_TEMP, "recording.wav")
    record_path = os.path.join(APP_TEMP, "{}_{}.wav".format(date, timestamp))
    with open(record_temp_path, 'wb') as audio:
        audio_data.save(audio)

    print("received audio file size:", os.path.getsize(record_temp_path))
    
    # os.system("{} -loglevel error -y -i {} -ar 16000 -ac 1 {}".format(ffmpeg_path, record_temp_path, record_path))
    os.system("{} -loglevel error -y -f webm -i {} -ar 16000 -ac 1 {}".format(
        ffmpeg_path, record_temp_path, record_path))


    response = {"suc": "success"}
    return json.dumps(response)

@app.route("/predict", methods=['GET'])
def predict():
    model = "tai_app"
    date = session['now'].strftime("%Y%m%d")
    timestamp = session['now'].strftime("%H%M%S")
    print(date, timestamp)
    record_path = os.path.join(APP_TEMP, "{}_{}.wav".format(date, timestamp))

    print("predict got:", record_path)
    if not os.path.exists(record_path):
        print("!!! audio file not found:", record_path)
    else:
        print("audio file exists, size:", os.path.getsize(record_path))

    res = taiwanese_recognize(record_path)
    
    response = {"recognition": res}
    # return json.dumps(response)
    print("type of response:", type(response))
    print(response)

    return jsonify(response)   

##############################
#         ta_course          #
##############################
ta_course_db_cursor = None
@app.route('/ta/course')
def ta_course():
    global ta_course_db_cursor
    ta_course_db_cursor = SQL()
    return render_template('ta_course.html')

@app.route("/ta/course/search", methods=['POST'])
def ta_course_search():
    global ta_course_db_cursor
    obj = request.get_json()
    search_name = obj["search_name"]
    print(search_name)
    results = ta_course_db_cursor.get_course(search_name)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/update", methods=['POST'])
def ta_course_update():
    global ta_course_db_cursor
    obj = request.get_json()
    course_id = obj["course_id"]
    update_name = obj["update_name"]
    print(course_id, update_name)
    results = ta_course_db_cursor.update_course(course_id, update_name)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/insert", methods=['POST'])
def ta_course_insert():
    global ta_course_db_cursor
    obj = request.get_json()
    insert_name = obj["insert_name"]
    print(insert_name)
    results = ta_course_db_cursor.insert_course(insert_name)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/delete", methods=['POST'])
def ta_course_delete():
    global ta_course_db_cursor
    obj = request.get_json()
    delete_id = obj["delete_id"]
    print(delete_id)
    results = ta_course_db_cursor.delete_course(delete_id)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/update/modifyts", methods=['POST'])
def ta_course_update_modifyts():
    global ta_course_db_cursor
    obj = request.get_json()
    course_id = obj["course_id"]
    print(course_id)
    results = ta_course_db_cursor.update_modifyts(course_id)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/commit")
def ta_course_commit():
    global ta_course_db_cursor
    ta_course_db_cursor.conn.commit()
    ta_course_db_cursor.conn.close()
    
    return "", 200

##############################
#      ta_course_vocab       #
##############################
ta_course_vocab_db_cursor = None
@app.route('/ta/course/vocab')
def ta_course_vocab():
    global ta_course_vocab_db_cursor
    ta_course_vocab_db_cursor = SQL()
    return render_template('ta_course_vocab.html')

@app.route("/ta/course/vocab/search", methods=['POST'])
def ta_course_vocab_search():
    global ta_course_vocab_db_cursor
    obj = request.get_json()
    course_id = obj["course_id"]
    search_word = obj["search_word"]
    print(course_id, search_word)
    results = ta_course_vocab_db_cursor.get_course_vocab(course_id, search_word)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/vocab/update", methods=['POST'])
def ta_course_vocab_update():
    global ta_course_vocab_db_cursor
    obj = request.get_json()
    course_id = obj["course_id"]
    word_id = obj["word_id"]
    update_CHword = obj["update_CHword"]
    update_TWword = obj["update_TWword"]
    update_TLPA = obj["update_TLPA"]
    print(course_id, word_id, update_CHword, update_TWword, update_TLPA)
    results = ta_course_vocab_db_cursor.update_course_vocab(course_id, word_id, update_CHword, update_TWword, update_TLPA)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/vocab/insert", methods=['POST'])
def ta_course_vocab_insert():
    global ta_course_vocab_db_cursor
    obj = request.get_json()
    course_id = obj["course_id"]
    insert_CHword = obj["insert_CHword"]
    insert_TWword = obj["insert_TWword"]
    insert_TLPA = obj["insert_TLPA"]
    print(course_id, insert_CHword, insert_TWword, insert_TLPA)
    results = ta_course_vocab_db_cursor.insert_course_vocab(course_id, insert_CHword, insert_TWword, insert_TLPA)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/vocab/delete", methods=['POST'])
def ta_course_vocab_delete():
    global ta_course_vocab_db_cursor
    obj = request.get_json()
    course_id = obj["course_id"]
    delete_id = obj["delete_id"]
    print(delete_id)
    results = ta_course_vocab_db_cursor.delete_course_vocab(course_id, delete_id)

    return json.dumps({
        "status": "success",
        "results": results
    })

@app.route("/ta/course/vocab/translate", methods=['POST'])
def ta_course_vocab_translate():
    # text = "黃柏楊"
    _json = request.get_json()
    word_tw = _json['TW']
    word_tlpa = tlpa_trans(word_tw) 
    
    return json.dumps({"tlpa": word_tlpa})

# @app.route("/ta/course/vocab/trylisten", methods=['POST'])
# def ta_course_vocab_trylisten():
#     obj = request.get_json()
#     name = tts(obj["TLPA"])
    
#     return json.dumps({"name": name})

def safe_filename_from_han(name: str, max_len: int = 80) -> str:
    """把台語漢字變成安全檔名（保留中文；去掉 Windows 禁字元；空白→_；限制長度）"""
    name = (name or "").strip()
    name = re.sub(r'[\\/:*?"<>|]+', '', name)  # 去掉禁字元
    name = re.sub(r'\s+', '_', name).strip('_')  # 空白換底線
    return (name or "audio")[:max_len]

@app.post("/ta/course/vocab/trylisten")
def ta_course_vocab_trylisten():
    """
    需求：
    - 前端送 { TLPA: "<台羅>", name_hint: "<台語漢字>" }
    - 若 static/audio/<name_hint>.wav 已存在：不重產，直接回舊檔名
    - 若不存在：用 TLPA 合成並存成 <name_hint>.wav
    回傳：
    - {"name": "<實際檔名（不含副檔名）>"}，前端用 /static/audio/<name>.wav 播放
    """
    obj = request.get_json(force=True)
    tlpa = (obj.get("TLPA") or "").strip()
    if not tlpa:
        return jsonify({"error": "TLPA required"}), 400

    name_hint = (obj.get("name_hint") or "").strip()
    save_name = safe_filename_from_han(name_hint)

    # 這行會：若檔案已存在 → 直接回舊名；否則 → 合成並存檔
    final_name = tts(tlpa, save_name=save_name)

    return jsonify({"name": final_name})


@app.route("/ta/course/vocab/commit", methods=['POST'])
def ta_course_vocab_commit():
    global ta_course_vocab_db_cursor
    _json = request.get_json()
    words = _json['words']
    for word in words:
        print(word["TWword"], word["TLPA"])
        # tts(word["TLPA"], word["TWword"])

    ta_course_vocab_db_cursor.conn.commit()
    ta_course_vocab_db_cursor.conn.close()
    
    return "", 200

##############################
#         stu_equip          #
##############################

@app.route('/stu/equipment')
def stu_equipment():
    return render_template('stu_equip.html')

@app.route('/stu/equipment/get', methods = ['GET'])
def stu_equipment_get():
    db_cursor = SQL()
    print(session.get('stu_id'))
    print(session.get('loggin'))
    if session.get('loggin') == None:
        redirect("/login/stu")
    else:
        stu_id = session.get('stu_id')
        
        level, score = db_cursor.get_stu_level_score(stu_id=stu_id)
        equipment_id_now = db_cursor.get_stu_equip_now(stu_id)
        equipment_info = db_cursor.get_stu_equip_gain_info(stu_id)
        equipment_info = list(equipment_info)
        equipment_info.insert(0, 1)
        
        print(level, score)
        print(equipment_id_now)
        print(equipment_info)

        return json.dumps({
            "score": score,
            "level": level,
            "equip_cur": equipment_id_now,
            "equip_list": equipment_info
        })

@app.route('/stu/equipment/update', methods = ['POST'])
def stu_equipment_update():
    db_cursor = SQL()
    print(session.get('stu_id'))
    print(session.get('loggin'))
    if session.get('loggin') == None:
        redirect("/login/stu")
    else:
        stu_id = session.get('stu_id')
        obj = request.get_json()
        status = db_cursor.update_wear_now(obj["select_equip_id"], stu_id)
        

        return json.dumps({'status':status})

# student register
@app.get('/register/stu')
def stu_register_page():
    session['identity'] = "Student"
    return render_template('student_register.html')


@app.post('/register/stu')
def stu_register_api():
    db = SQL()
    try:
        obj = request.get_json(force=True) if request.is_json else request.form

        grade   = str(obj.get('grade', '')).strip()   # "1" | "2" | "3"..."6"
        clazz   = str(obj.get('clazz', '')).strip()   # "01".."15"
        seat_no = str(obj.get('seat_no', '')).strip() # "1".."40"
        pwd     = str(obj.get('pwd', '')).strip()
        name    = str(obj.get('name', '')).strip()

        # 檢查
        if grade not in {"1","2","3","4","5","6"}:
            return jsonify({"status": "error", "message": "年級需為 1~6"}), 400
        if not (clazz.isdigit() and len(clazz) == 2 and 1 <= int(clazz) <= 99):
            return jsonify({"status": "error", "message": "班別需為兩位數（01~99）"}), 400
        if not seat_no.isdigit() or not (1 <= int(seat_no) <= 40):
            return jsonify({"status": "error", "message": "座號需為 1~40"}), 400
        if not pwd:
            return jsonify({"status": "error", "message": "密碼不可為空"}), 400

        # 組帳號：G + CC + SS
        account = f"{grade}{int(clazz):02d}{int(seat_no):02d}"  # 30216 這種格式
        class_code = f"{grade}{int(clazz):02d}"                 # 302

        # 由 class_code 找 class_id（必要）
        class_id = class_code_to_class_id(db, class_code)
        if class_id is None:
            return jsonify({"status": "error", "message": f"找不到班級代碼 {class_code} 對應的 class_id"}), 400

        # 建立學生（沿用你現有的 create_student）
        ok = db.create_student(account=account, class_id=class_id, password=pwd, name=name)
        if not ok:
            return jsonify({"status": "error", "message": "帳號已存在或資料庫錯誤"}), 400

        # 登入 session
        session['identity'] = "Student"
        session['loggin'] = True
        session['account'] = account
        try:
            session['stu_id'] = db.get_student_id(account)
        except Exception:
            session['stu_id'] = None

        url = "/home/stu" if name else "/login/name"
        return jsonify({"status": "success", "url": url, "account": account})
    except Exception as e:
        print("stu_register_api error:", e)
        return jsonify({"status": "error", "message": "系統暫時無法註冊"}), 500

# teacher register
@app.get('/register/ta')
def teacher_register_page():
    session['identity'] = "Teacher"
    return render_template('teacher_register.html')

@app.post('/register/ta')
def teacher_register_api():
    db = SQL()
    try:
        obj  = request.get_json(force=True) if request.is_json else request.form
        grade = str(obj.get('grade', '')).strip()   # "1"|"2"|"3"..."6"
        clazz = str(obj.get('clazz', '')).strip()   # "01".."99"
        name  = str(obj.get('name', '')).strip()
        pwd   = str(obj.get('pwd', '')).strip()

        # 檢查
        if grade not in {"1","2","3","4","5","6"}:
            return jsonify({"status": "error", "message": "年級需為 1~6"}), 400
        if not (clazz.isdigit() and len(clazz) == 2 and 1 <= int(clazz) <= 99):
            return jsonify({"status": "error", "message": "班別需為兩位數（01~99）"}), 400
        if not name:
            return jsonify({"status": "error", "message": "姓名不可為空"}), 400
        if not pwd:
            return jsonify({"status": "error", "message": "密碼不可為空"}), 400

        # 帳號規則：G + CC + 00  （ex: 3年02班 → 30200）
        account = f"{grade}{int(clazz):02d}00"

        # 若該班已經有老師帳號，回錯誤
        with db.conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM Teacher WHERE account=%s LIMIT 1;", (account,))
            if cursor.fetchone():
                return jsonify({"status": "error", "message": f"此班級 ({grade}{clazz}) 已建立老師帳號"}), 400

        # 建立老師
        ok = db.create_teacher(account=account, password=pwd, name=name)
        if not ok:
            return jsonify({"status": "error", "message": "帳號已存在或資料庫錯誤"}), 400

        # 登入 session
        session['identity'] = "Teacher"
        session['loggin'] = True
        session['account'] = account
        try:
            session['teacher_id'] = db.get_teacher_id(account)
        except Exception:
            session['teacher_id'] = None

        return jsonify({"status": "success", "url": "/home/ta", "account": account})
    except Exception as e:
        print("teacher_register_api error:", e)
        return jsonify({"status": "error", "message": "系統暫時無法註冊"}), 500





##############################
#          app init          #
##############################
ffmpeg_path = "ffmpeg"
if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 8889, debug = True, threaded = True, use_reloader=False, ssl_context = 'adhoc')
