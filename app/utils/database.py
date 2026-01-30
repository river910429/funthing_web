# coding=utf-8
import pymysql
import os
import random
import string
import secrets
from datetime import datetime

class SQL(): 
    def __init__(self, mode="stu"):
        self.db_settings = {
            "host": "140.116.245.150",
            "port": 3306,
            "user": "funthing_teach_web_root",
            "password": "Funthing_teach_web_01",
            "db": "funthing_teach_old_ver",
            "charset": "utf8"
        }
        try:
            self.conn = pymysql.connect(**self.db_settings)
        except Exception as e:
            print("DB Connection Error:", e)
    
    def __del__(self):
        try:
            self.conn.close()
        except:
            pass

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

    # === 驗證與帳號相關 ===
    def validate_account(self, identity, account, school_id):
        with self.conn.cursor() as cursor:
            table = "Student" if identity == "Student" else "Teacher"
            cursor.execute(f"SELECT 1 FROM {table} WHERE account=%s AND school_id=%s LIMIT 1;", (account, school_id))
        return cursor.fetchone() is not None

    def validate_password(self, identity, account, pwd, school_id):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM Password WHERE identity=%s AND account=%s AND school_id=%s AND pwd=%s LIMIT 1;",
                (identity, account, school_id, pwd)
            )
            return cursor.fetchone() is not None

    def get_name(self, identity, account):
        with self.conn.cursor() as cursor:
            try:
                if identity == "Student":
                    cursor.execute("SELECT student_name FROM Student WHERE account=%s", (account,))
                    result = cursor.fetchone()
                    return result[0] if result else ""
                # Teacher
                cursor.execute("SELECT teacher_name FROM Teacher WHERE account=%s", (account,))
                result = cursor.fetchone()
                return result[0] if result else ""
            except Exception as e:
                return ""
    
    # [新增] 透過帳號反查老師的 school_id (用於登入時不輸入學校的情況)
    def get_teacher_school_id(self, account):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT school_id FROM Teacher WHERE account=%s LIMIT 1;", (account,))
            row = cursor.fetchone()
            return row[0] if row else None

    # === 註冊與建立相關 ===

    def list_schools(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT school_id, school_code, school_name FROM School ORDER BY school_name ASC;")
            return cursor.fetchall()

    def ensure_school_by_name(self, school_name: str) -> int | None:
        def _gen_school_code() -> str:
            suffix = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            return f"AUTO-{suffix}"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT school_id FROM School WHERE school_name=%s LIMIT 1;", (school_name,))
                row = cursor.fetchone()
                if row: return row[0]

                for _ in range(10):
                    code = _gen_school_code()
                    cursor.execute("SELECT 1 FROM School WHERE school_code=%s LIMIT 1;", (code,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO School (school_code, school_name) VALUES (%s, %s);", (code, school_name))
                        self.conn.commit()
                        cursor.execute("SELECT LAST_INSERT_ID();")
                        return cursor.fetchone()[0]
                self.conn.rollback()
                return None
        except Exception as e:
            print("ensure_school_by_name error:", e)
            self.conn.rollback()
            return None

    def generate_unique_class_code(self):
        while True:
            # 產生 6 碼代碼
            alphabet = string.ascii_uppercase + string.digits
            safe_chars = [c for c in alphabet if c not in 'IO01l'] 
            code = ''.join(secrets.choice(safe_chars) for i in range(6))
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM Class WHERE class_code=%s LIMIT 1;", (code,))
                if not cursor.fetchone():
                    return code

    def validate_invite_code(self, code: str):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT class_id, school_id FROM Class WHERE class_code=%s LIMIT 1;", (code,))
            row = cursor.fetchone()
            return (row[0], row[1]) if row else (None, None)

    # [老師註冊] 僅建立帳號
    def create_teacher_only(self, account: str, password: str, name: str, school_id: int):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM Teacher WHERE account=%s LIMIT 1;", (account,))
                if cursor.fetchone():
                    return {"status": False, "msg": "Email 已被註冊"}

                cursor.execute("INSERT INTO Teacher (teacher_name, account, school_id) VALUES (%s, %s, %s);", (name, account, school_id))
                
                cursor.execute("INSERT INTO Password (account, identity, school_id, pwd) VALUES (%s, %s, %s, %s);", (account, "Teacher", school_id, password))
            
            self.conn.commit()
            return {"status": True}
        except Exception as e:
            print("create_teacher_only error:", e)
            self.conn.rollback()
            return {"status": False, "msg": str(e)}

    # [建立班級] 老師後台使用
    def create_new_class(self, teacher_id: int, school_id: int, class_name: str):
        try:
            class_code = self.generate_unique_class_code()
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Class (school_id, teacher_id, class_name, class_code)
                    VALUES (%s, %s, %s, %s);
                """, (school_id, teacher_id, class_name, class_code))
            self.conn.commit()
            return {"status": True, "class_code": class_code, "class_name": class_name}
        except Exception as e:
            print("create_new_class error:", e)
            self.conn.rollback()
            return {"status": False, "msg": "建立班級失敗"}

    # [查詢] 取得老師的所有班級
    def get_teacher_classes(self, teacher_id: int):
        with self.conn.cursor() as cursor:
            sql = """
                SELECT class_id, class_name, class_code 
                FROM Class 
                WHERE teacher_id = %s 
                ORDER BY class_id DESC;
            """
            cursor.execute(sql, (teacher_id,))
            result = cursor.fetchall()
            
            data = []
            for row in result:
                data.append({
                    "id": row[0],
                    "name": row[1],
                    "code": row[2],
                    "created_at": "" 
                })
            return data

    # [查詢] 排行榜 - 根據班級名稱關鍵字
    def get_class_leaderboard_by_keyword(self, keyword):
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
            JOIN Class    AS c  ON s2.class_id = c.class_id
            CROSS JOIN (SELECT @rownum := 0, @rank := 0, @prev_score := NULL) vars
            WHERE c.class_name LIKE %s
            ORDER BY s1.acc_score DESC, s2.student_name ASC
        ) t
        ORDER BY r ASC, acc_score DESC, student_name ASC;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (f"%{keyword}%",))
            return cursor.fetchall()

    # ==============================
    #      ta_course (課程管理)
    # ==============================
    def get_course(self, search_name):
        with self.conn.cursor() as cursor:
            # 使用參數化查詢 %s
            sql = """
                SELECT c.course_id, c.course_name, COUNT(w.word_id), c.ts 
                FROM Course AS c 
                LEFT JOIN Word AS w ON c.course_id = w.course_id 
                WHERE c.course_name LIKE %s 
                GROUP BY c.course_id 
                ORDER BY c.ts DESC;
            """
            cursor.execute(sql, (f"%{search_name}%",))
            data = cursor.fetchall()

        result = list()
        for i, item in enumerate(data):
            temp = {
                "id": item[0],
                "number": i,
                "name": item[1],
                "words": item[2],
                "lastmodify": item[3].strftime("%Y-%m-%d") if item[3] else ""
            }
            result.append(temp)
        return result

    def update_course(self, course_id, update_name):
        with self.conn.cursor() as cursor:
            cursor.execute("UPDATE Course SET course_name=%s WHERE course_id=%s;", (update_name, course_id))
        return self.get_course("")
    
    def insert_course(self, insert_name):
        with self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO Course (course_name) VALUES (%s);", (insert_name,))
        return self.get_course("")

    def delete_course(self, delete_id):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM Course WHERE course_id=%s;", (delete_id,))
        return self.get_course("")

    def update_modifyts(self, course_id):
        with self.conn.cursor() as cursor:
            cursor.execute("UPDATE Course SET ts=NOW() WHERE course_id=%s;", (course_id,))
        return True

    # [學生註冊]
    def create_student(self, account: str, class_id: int, password: str, name: str, school_id: int, seat_no: str, grade_class_str: str) -> bool:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM Student WHERE account=%s LIMIT 1;", (account,))
                if cursor.fetchone(): return False

                # [修改] 使用者希望名字可以重複，且不強制加上座號前綴
                # 原本邏輯: full_display_name = f"{seat_no}-{name}"
                full_display_name = name 
                
                cursor.execute("INSERT INTO Student (account, class_id, student_name, school_id) VALUES (%s, %s, %s, %s);", 
                               (account, class_id, full_display_name, school_id))
                
                cursor.execute("SELECT LAST_INSERT_ID();")
                student_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO Stu_info (student_id, level, acc_score, equip_now, 
                    equip_1_gain, equip_2_gain, equip_3_gain, equip_4_gain, equip_5_gain, equip_6_gain, equip_7_gain)
                    VALUES (%s, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
                """, (student_id,))

                cursor.execute("INSERT INTO Password (account, identity, school_id, pwd) VALUES (%s, %s, %s, %s);", 
                               (account, "Student", school_id, password))

            self.conn.commit()
            return True
        except Exception as e:
            print("create_student error:", e)
            self.conn.rollback()
            return False
        
    # [修改] 更新班級的遊戲課程設定 (Class 表格中的 game1...game6 欄位)
    def update_classgame(self, class_id, game_name, course_id):
        # [修正] 加入 game5, game6
        allowed_games = ['game1', 'game2', 'game3', 'game4', 'game5', 'game6']
        
        if game_name not in allowed_games:
            return False
            
        try:
            with self.conn.cursor() as cursor:
                # 動態組 SQL，但 game_name 已過濾，course_id 使用參數化
                sql = f"UPDATE Class SET {game_name} = %s WHERE class_id = %s"
                cursor.execute(sql, (course_id, class_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"update_classgame error: {e}")
            return False

    # === Helper Methods ===
    def get_teacher_id(self, account: str):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT teacher_id FROM Teacher WHERE account=%s;", (account,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_student_id(self, account: str):
        with self.conn.cursor() as cursor:
            cursor.execute("select Student_id from Student where account = %s", (account,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_student_school_and_class_by_account(self, account: str):
        with self.conn.cursor() as c:
            c.execute("SELECT school_id, class_id FROM Student WHERE account=%s LIMIT 1;", (account,))
            row = c.fetchone()
            return (row[0], row[1]) if row else (None, None)
    
    # 學生相關 - 裝備與分數查詢 (補上)
    def get_stu_level_score(self, stu_id):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT level, acc_score FROM Stu_info WHERE student_id = %s", (stu_id,))
            result = cursor.fetchone()
            return (result[0], result[1]) if result else (0, 0)

    def get_stu_equip_now(self, stu_id):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT equip_now FROM Stu_info WHERE student_id = %s", (stu_id,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_stu_equip_gain_info(self, stu_id):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT equip_1_gain, equip_2_gain, equip_3_gain, equip_4_gain, 
                       equip_5_gain, equip_6_gain, equip_7_gain 
                FROM Stu_info WHERE student_id = %s
            """, (stu_id,))
            return cursor.fetchone()

    def update_wear_now(self, equip_id, stu_id):
        with self.conn.cursor() as cursor:
            cursor.execute("UPDATE Stu_info SET equip_now=%s WHERE student_id=%s", (equip_id, stu_id))
            self.conn.commit()
            return True

    def update_equipment_gain(self, stu_id, equipment_index):
        field = f"equip_{equipment_index}_gain"
        with self.conn.cursor() as cursor:
            cursor.execute(f"UPDATE Stu_info SET {field}=1 WHERE student_id=%s", (stu_id,))
            self.conn.commit()
            return True

    def upload_score(self, stu_id, score, level):
        with self.conn.cursor() as cursor:
            cursor.execute("UPDATE Stu_info SET acc_score=%s, level=%s WHERE student_id=%s", (score, level, stu_id))
            self.conn.commit()
            return True

    def get_classgame(self, school_id, class_id, game_name):
        # [修正] 加入 game5, game6 到檢查清單
        if game_name not in ['game1', 'game2', 'game3', 'game4', 'game5', 'game6']: 
            return None
            
        with self.conn.cursor() as cursor:
            # 因為上面已經做過白名單檢查，這裡用 f-string 帶入 game_name 是安全的
            cursor.execute(f"SELECT {game_name} FROM Class WHERE school_id=%s AND class_id=%s LIMIT 1;", (school_id, class_id))
            row = cursor.fetchone()
            return row[0] if row else None
            
    def get_course_vocab(self, course_id, search_word=""):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Word WHERE course_id = %s AND ch_word LIKE %s ORDER BY ts DESC;", (course_id, f"%{search_word}%"))
            data = cursor.fetchall()
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

    def update_course_vocab(self, course_id, word_id, ch_word, tw_word, tlpa):
        # 更新單字
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Word 
                SET ch_word=%s, tw_word=%s, tlpa=%s 
                WHERE word_id=%s;
            """, (ch_word, tw_word, tlpa, word_id))
        self.conn.commit() # 記得 commit
        # 回傳更新後的列表以便前端刷新
        return self.get_course_vocab(course_id, "")

    def insert_course_vocab(self, course_id, ch_word, tw_word, tlpa):
        # 新增單字
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Word (course_id, ch_word, tw_word, tlpa) 
                VALUES (%s, %s, %s, %s);
            """, (course_id, ch_word, tw_word, tlpa))
        self.conn.commit()
        return self.get_course_vocab(course_id, "")

    def delete_course_vocab(self, course_id, delete_id):
        # 刪除單字
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM Word WHERE word_id=%s;", (delete_id,))
        self.conn.commit()
        return self.get_course_vocab(course_id, "")    

    def get_class_leaderboard(self, class_id):
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
            WHERE s2.class_id = %s
            ORDER BY s1.acc_score DESC, s2.student_name ASC
        ) t
        ORDER BY r ASC, acc_score DESC, student_name ASC;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (class_id,))
            return cursor.fetchall()
            
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
            return cursor.fetchall()

    def school_code_or_name_to_id(self, school: str):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT school_id FROM School WHERE school_code=%s LIMIT 1;", (school,))
                row = cursor.fetchone()
                if row: return row[0]
                cursor.execute("SELECT school_id FROM School WHERE school_name=%s LIMIT 1;", (school,))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            return None