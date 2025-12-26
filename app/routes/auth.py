# routes/auth.py
# from flask import Blueprint, render_template, request, session, jsonify, redirect
# from database import SQL

# bp_auth = Blueprint('auth', __name__)

# # --- Pages ---
# @bp_auth.route('/branch')
# def branch():
#     return render_template('branch.html')

# @bp_auth.route('/login/stu')
# def stu_login():
#     session['identity'] = "Student"
#     return render_template('student_login.html')

# @bp_auth.route('/login/ta')
# def ta_login():
#     session['identity'] = "Teacher"
#     return render_template('teacher_login.html')

# @bp_auth.route('/register/stu')
# def stu_register_page():
#     session['identity'] = "Student"
#     return render_template('student_register.html')

# @bp_auth.route('/register/ta')
# def teacher_register_page():
#     session['identity'] = "Teacher"
#     return render_template('teacher_register.html')

# # --- APIs ---
# @bp_auth.route('/api/schools')
# def api_schools():
#     try:
#         db = SQL()
#         rows = db.list_schools()
#         data = [{"id": r[0], "code": r[1], "name": r[2]} for r in rows]
#         return jsonify({"status": "success", "schools": data})
#     except Exception as e:
#         print(f"API Schools Error: {e}")
#         return jsonify({"status": "error", "message": "無法載入學校列表"})

# @bp_auth.route('/verifying', methods=['POST'])
# def verifying():
#     db = SQL()
#     try:
#         obj = request.get_json(force=True)
#         account = obj.get('account')
#         pwd     = obj.get('pwd')
        
#         # [修改] 學生登入不再需要代碼
#         # code_input = obj.get('code', '').strip().upper()

#         identity = session.get('identity')
#         if not identity:
#             print("Verifying Error: Session identity is missing.")
#             return jsonify({"status": "error", "message": "頁面已過期，請重新整理後再登入"}), 400

#         school_id = None

#         if identity == "Teacher":
#             # 老師：直接用 Email 查 school_id
#             school_id = db.get_teacher_school_id(account)
#             if not school_id:
#                  return jsonify({"status":"error","message":"帳號不存在"}), 400
#         else:
#             # [修改] 學生：直接用 Account (Email) 查 school_id 與 class_id
#             # 使用 database.py 中的 helper function
#             res = db.get_student_school_and_class_by_account(account)
#             # res 為 (school_id, class_id) 或 (None, None)
            
#             if not res or not res[0]:
#                  return jsonify({"status":"error","message":"帳號不存在"}), 400
            
#             school_id = res[0]

#         # 驗證密碼
#         valid_pwd = db.validate_password(identity, account, pwd, school_id)

#         if valid_pwd:
#             session.permanent = True 
#             session['loggin']    = True
#             session['account']   = account
#             session['school_id'] = school_id
            
#             if identity == "Student":
#                 student_id = db.get_student_id(account)
#                 name = db.get_name(identity, account)
#                 session['stu_id'] = student_id
#                 url = "/login/name" if not name else "/home/stu"
#             else:
#                 session['teacher_id'] = db.get_teacher_id(account)
#                 url = "/home/ta"
#             return jsonify({"status":"success","url":url})
#         else:
#             return jsonify({"status":"error","message":"帳號或密碼錯誤"})
            
#     except Exception as e:
#         print(f"Verifying System Error: {e}")
#         return jsonify({"status":"error", "message": f"系統錯誤: {str(e)}"}), 500

# @bp_auth.route('/register/ta', methods=['POST'])
# def teacher_register_api():
#     db = SQL()
#     try:
#         obj = request.get_json(force=True)
#         account = str(obj.get('account', '')).strip()
#         pwd     = str(obj.get('pwd', '')).strip()
#         name    = str(obj.get('name', '')).strip()
#         school  = str(obj.get('school', '')).strip()

#         if not account or '@' not in account:
#             return jsonify({"status":"error","message":"請輸入有效的 Email"}), 400

#         sid = db.ensure_school_by_name(school)
#         if not sid:
#             return jsonify({"status":"error","message":"學校資料處理失敗"}), 500

#         # [修正] 使用 create_teacher_only
#         result = db.create_teacher_only(account=account, password=pwd, name=name, school_id=sid)
        
#         if result["status"]:
#             session['identity']  = "Teacher"
#             session['loggin']    = True
#             session['account']   = account
#             session['school_id'] = sid
#             session['teacher_id'] = db.get_teacher_id(account)
#             return jsonify({"status": "success", "url": "/home/ta", "message": "註冊成功！"})
#         else:
#             return jsonify({"status": "error", "message": result["msg"]}), 400
#     except Exception as e:
#         print("Reg Error:", e)
#         return jsonify({"status": "error", "message": f"系統錯誤: {str(e)}"}), 500

# @bp_auth.route('/register/stu', methods=['POST'])
# def stu_register_api():
#     db = SQL()
#     try:
#         obj = request.get_json(force=True)
#         invite_code = str(obj.get('code', '')).strip().upper()
#         account     = str(obj.get('account', '')).strip()
#         pwd         = str(obj.get('pwd', '')).strip()
#         name        = str(obj.get('name', '')).strip()
#         grade       = str(obj.get('grade', '')).strip()
#         clazz       = str(obj.get('clazz', '')).strip()
#         seat_no     = str(obj.get('seat_no', '')).strip()
        
#         if not invite_code: return jsonify({"status": "error", "message": "請輸入班級代碼"}), 400
        
#         class_id, school_id = db.validate_invite_code(invite_code)
#         if not class_id: return jsonify({"status": "error", "message": "無效的班級代碼"}), 400
            
#         if not account or '@' not in account: return jsonify({"status": "error", "message": "請輸入有效的 Email"}), 400

#         grade_class_str = f"{grade}年{clazz}班"
#         ok = db.create_student(account, class_id, pwd, name, school_id, seat_no, grade_class_str)
        
#         if not ok: return jsonify({"status": "error", "message": "註冊失敗 (Email可能重複)"}), 400

#         session['identity'] = "Student"
#         session['loggin'] = True
#         session['account'] = account
#         session['school_id'] = school_id
#         session['stu_id'] = db.get_student_id(account)

#         return jsonify({"status": "success", "url": "/home/stu"})
#     except Exception as e:
#         print("Reg Stu Error:", e)
#         return jsonify({"status": "error", "message": f"系統錯誤: {str(e)}"}), 500
from flask import Blueprint, render_template, request, session, jsonify
import os

# [Refactor] 引用修正
try:
    from app.utils.database import SQL
except ImportError:
    import sys
    sys.path.append(os.getcwd())
    try:
        from funthing_teach_web.app.utils.database import SQL
    except:
        pass

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/branch')
def branch():
    return render_template('branch.html')

@bp_auth.route('/login/stu')
def stu_login():
    session['identity'] = "Student"
    return render_template('student_login.html')

@bp_auth.route('/login/ta')
def ta_login():
    session['identity'] = "Teacher"
    return render_template('teacher_login.html')

@bp_auth.route('/register/stu')
def stu_register_page():
    session['identity'] = "Student"
    return render_template('student_register.html')

@bp_auth.route('/register/ta')
def teacher_register_page():
    session['identity'] = "Teacher"
    return render_template('teacher_register.html')

@bp_auth.route('/api/schools')
def api_schools():
    try:
        db = SQL()
        rows = db.list_schools()
        data = [{"id": r[0], "code": r[1], "name": r[2]} for r in rows]
        return jsonify({"status": "success", "schools": data})
    except Exception as e:
        print(f"API Schools Error: {e}")
        return jsonify({"status": "error", "message": "無法載入學校列表"})

@bp_auth.route('/verifying', methods=['POST'])
def verifying():
    db = SQL()
    try:
        obj = request.get_json(force=True)
        account = obj.get('account')
        pwd = obj.get('pwd')
        identity = session.get('identity')
        
        if not identity:
            return jsonify({"status": "error", "message": "頁面已過期"}), 400

        school_id = None
        if identity == "Teacher":
            school_id = db.get_teacher_school_id(account)
            if not school_id:
                 return jsonify({"status":"error","message":"帳號不存在"}), 400
        else:
            res = db.get_student_school_and_class_by_account(account)
            if not res or not res[0]:
                 return jsonify({"status":"error","message":"帳號不存在"}), 400
            school_id = res[0]

        valid_pwd = db.validate_password(identity, account, pwd, school_id)

        if valid_pwd:
            session.permanent = True 
            session['loggin'] = True
            session['account'] = account
            session['school_id'] = school_id
            
            if identity == "Student":
                student_id = db.get_student_id(account)
                name = db.get_name(identity, account)
                session['stu_id'] = student_id
                url = "/login/name" if not name else "/home/stu"
            else:
                session['teacher_id'] = db.get_teacher_id(account)
                url = "/home/ta"
            return jsonify({"status":"success","url":url})
        else:
            return jsonify({"status":"error","message":"帳號或密碼錯誤"})
    except Exception as e:
        print(f"Verifying Error: {e}")
        return jsonify({"status":"error", "message": "系統錯誤"}), 500

@bp_auth.route('/register/ta', methods=['POST'])
def teacher_register_api():
    db = SQL()
    try:
        obj = request.get_json(force=True)
        account = str(obj.get('account', '')).strip()
        pwd = str(obj.get('pwd', '')).strip()
        name = str(obj.get('name', '')).strip()
        school = str(obj.get('school', '')).strip()

        if not account or '@' not in account:
            return jsonify({"status":"error","message":"請輸入有效的 Email"}), 400

        sid = db.ensure_school_by_name(school)
        if not sid:
            return jsonify({"status":"error","message":"學校資料處理失敗"}), 500

        result = db.create_teacher_only(account=account, password=pwd, name=name, school_id=sid)
        if result["status"]:
            session['identity'] = "Teacher"
            session['loggin'] = True
            session['account'] = account
            session['school_id'] = sid
            session['teacher_id'] = db.get_teacher_id(account)
            return jsonify({"status": "success", "url": "/home/ta"})
        else:
            return jsonify({"status": "error", "message": result["msg"]}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"系統錯誤: {str(e)}"}), 500

@bp_auth.route('/register/stu', methods=['POST'])
def stu_register_api():
    db = SQL()
    try:
        obj = request.get_json(force=True)
        invite_code = str(obj.get('code', '')).strip().upper()
        account = str(obj.get('account', '')).strip()
        
        if not invite_code: return jsonify({"status": "error", "message": "請輸入班級代碼"}), 400
        
        class_id, school_id = db.validate_invite_code(invite_code)
        if not class_id: return jsonify({"status": "error", "message": "無效的班級代碼"}), 400
            
        if not account or '@' not in account: return jsonify({"status": "error", "message": "請輸入有效的 Email"}), 400

        grade_class_str = f"{obj.get('grade')}年{obj.get('clazz')}班"
        ok = db.create_student(account, class_id, obj.get('pwd'), obj.get('name'), school_id, obj.get('seat_no'), grade_class_str)
        
        if not ok: return jsonify({"status": "error", "message": "註冊失敗 (Email可能重複)"}), 400

        session['identity'] = "Student"
        session['loggin'] = True
        session['account'] = account
        session['school_id'] = school_id
        session['stu_id'] = db.get_student_id(account)

        return jsonify({"status": "success", "url": "/home/stu"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"系統錯誤: {str(e)}"}), 500