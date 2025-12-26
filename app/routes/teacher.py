# routes/teacher.py
# from flask import Blueprint, render_template, request, session, jsonify, redirect
# from database import SQL
# import os
# import sys
# import re

# # [修正] 簡潔版路徑設定：將上一層目錄 (根目錄) 加入 sys.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # 嘗試引入翻譯與語音服務
# try:
#     from ttp_service_api import process as tlpa_trans
#     from hts_service_api import tts
# except ImportError:
#     # 避免本地開發因缺檔而 crash
#     def tlpa_trans(word): return f"[Mock TLPA] {word}"
#     def tts(tlpa, save_name=None): return save_name or "test_audio"

# bp_teacher = Blueprint('teacher', __name__)

# # 檢查登入狀態的裝飾器 (可選)
# def login_required(f):
#     def wrapper(*args, **kwargs):
#         if not session.get('loggin') or session.get('identity') != 'Teacher':
#             return redirect('/branch')
#         return f(*args, **kwargs)
#     wrapper.__name__ = f.__name__
#     return wrapper


# @bp_teacher.route('/home/ta')
# @login_required
# def ta_home():
#     return render_template('teacher_home.html')

# @bp_teacher.route('/ta/template')
# @login_required
# def ta_template():
#     return render_template('teacher_template.html')

# # [新增] 班級管理頁面路由
# @bp_teacher.route('/ta/class_management')
# @login_required
# def ta_class_management():
#     db = SQL()
#     teacher_id = session.get('teacher_id')
#     # 獲取該老師的所有班級資料
#     classes = db.get_teacher_classes(teacher_id)
#     return render_template('teacher_class_management.html', classes=classes)

# # [新增] 建立班級 API
# @bp_teacher.route('/api/create_class', methods=['POST'])
# def api_create_class():
#     if session.get('identity') != 'Teacher' or not session.get('teacher_id'):
#         return jsonify({"status": "error", "message": "請先登入"}), 403
        
#     db = SQL()
#     obj = request.get_json(force=True)
#     class_name = obj.get('class_name', '新班級')
    
#     teacher_id = session['teacher_id']
#     school_id = session['school_id']
    
#     result = db.create_new_class(teacher_id, school_id, class_name)
#     if result["status"]:
#         return jsonify({"status": "success", "class_code": result["class_code"]})
#     else:
#         return jsonify({"status": "error", "message": result["msg"]})

# # 註：排行榜與課程管理的路由也可以依此方式遷移進來
# # [新增] 排行榜頁面
# @bp_teacher.route('/ta/leaderboard')
# @login_required
# def ta_leaderboard():
#     return render_template('teacher_leaderboard.html')

# # [新增] 排行榜查詢 (Form Post)
# @bp_teacher.route('/leaderboard_ta_query', methods=['POST'])
# @login_required
# def leaderboard_ta_query():
#     db = SQL()
#     # 前端 input name="input_id" (輸入班級名稱關鍵字)
#     class_name_kw = request.form.get('input_id', '').strip()
    
#     data = []
#     error_msg = ""
#     target_idx = [9999999] # 保留原有的邏輯，用於模板中的標示

#     if not class_name_kw:
#         data = []
#     else:
#         try:
#             # 改用關鍵字搜尋 Class Name
#             data = db.get_class_leaderboard_by_keyword(class_name_kw)
#             if not data:
#                 error_msg = "*查無此班級或尚無資料*"
#         except Exception as e:
#             print(e)
#             data = []
#             error_msg = "*系統查詢錯誤*"
    
#     return render_template('teacher_leaderboard_result.html', data=data, target_idx=target_idx, error_msg=error_msg)

# # ==============================
# #      Game Template (遊戲模板設定)
# # ==============================

# # 1. 頁面路由：接蛋遊戲 (Catch Egg)
# @bp_teacher.route('/template/catch_egg')
# @login_required
# def ta_template_catch():
#     return render_template('teacher_template_catch.html')

# # (若有其他遊戲頁面，請依此類推搬移，例如 map, fruit_cutter 等)
# @bp_teacher.route('/template/map')
# @login_required
# def ta_template_map():
#     return render_template('teacher_template_map.html')

# @bp_teacher.route('/template/fruit_cutter')
# @login_required
# def ta_template_fruit():
#     return render_template('teacher_template_fruit.html')

# @bp_teacher.route('/template/flipping_card')
# @login_required
# def ta_template_card():
#     return render_template('teacher_template_card.html')

# # 2. API：查詢課程與班級 (這是關鍵修改)
# @bp_teacher.route("/template/course/search", methods=['POST'])
# @login_required
# def template_course_search():
#     db = SQL()
#     teacher_id = session.get('teacher_id')
    
#     # 1. 取得所有課程 (供下拉選單用)
#     # 這裡假設前端傳來的參數是空的或用於篩選課程名稱，若不需要篩選可傳空字串
#     obj = request.get_json(silent=True) or {}
#     # search_name = obj.get("search_name", "") # 如果需要篩選課程
    
#     courses = db.get_course("") # 取得所有課程列表
    
#     # 2. 取得老師的班級列表 (新增功能)
#     classes = db.get_teacher_classes(teacher_id)

#     return jsonify({
#         "status": "success",
#         "results": courses,   # 課程列表
#         "classes": classes    # 班級列表
#     })

# # 3. API：更新設定
# @bp_teacher.route("/template/course/update", methods=['POST'])
# @login_required
# def template_course_update():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
    
#     game_name = obj.get("game_name") # 例如 "game2"
#     course_id = obj.get("course_id") # 選中的課程 ID
#     class_id  = obj.get("class_id")  # 選中的班級 ID (新增)

#     if not all([game_name, course_id, class_id]):
#         return jsonify({"status": "error", "message": "資料不完整"})

#     # 呼叫資料庫更新
#     success = db.update_classgame(class_id, game_name, course_id)

#     if success:
#         return jsonify({"status": "success"})
#     else:
#         return jsonify({"status": "error", "message": "更新失敗"})

# # ==============================



# # ==============================
# #      ta_course (課程管理)
# # ==============================

# @bp_teacher.route('/ta/course')
# @login_required
# def ta_course():
#     # 這裡不再需要 global ta_course_db_cursor，改由各 API 獨立連線
#     return render_template('ta_course.html')

# @bp_teacher.route("/ta/course/search", methods=['POST'])
# @login_required
# def ta_course_search():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
#     search_name = obj.get("search_name", "")
    
#     # 請確保 database.py 中的 SQL 類別有實作 get_course 方法
#     results = db.get_course(search_name)

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# @bp_teacher.route("/ta/course/update", methods=['POST'])
# @login_required
# def ta_course_update():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
#     course_id = obj.get("course_id")
#     update_name = obj.get("update_name")
    
#     # 執行更新並確保 Commit
#     # 請確保 database.py 中的 SQL 類別有實作 update_course 方法
#     results = db.update_course(course_id, update_name)
#     if hasattr(db, 'conn'):
#         db.conn.commit()

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# @bp_teacher.route("/ta/course/insert", methods=['POST'])
# @login_required
# def ta_course_insert():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
#     insert_name = obj.get("insert_name")
    
#     # 執行新增並確保 Commit
#     # 請確保 database.py 中的 SQL 類別有實作 insert_course 方法
#     results = db.insert_course(insert_name)
#     if hasattr(db, 'conn'):
#         db.conn.commit()

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# @bp_teacher.route("/ta/course/delete", methods=['POST'])
# @login_required
# def ta_course_delete():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
#     delete_id = obj.get("delete_id")
    
#     # 執行刪除並確保 Commit
#     # 請確保 database.py 中的 SQL 類別有實作 delete_course 方法
#     results = db.delete_course(delete_id)
#     if hasattr(db, 'conn'):
#         db.conn.commit()

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# @bp_teacher.route("/ta/course/update/modifyts", methods=['POST'])
# @login_required
# def ta_course_update_modifyts():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
#     course_id = obj.get("course_id")
    
#     # 請確保 database.py 中的 SQL 類別有實作 update_modifyts 方法
#     results = db.update_modifyts(course_id)
#     if hasattr(db, 'conn'):
#         db.conn.commit()

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# # ==============================
# #      ta_course_vocab (單字管理)
# # ==============================

# @bp_teacher.route('/ta/course/vocab')
# @login_required
# def ta_course_vocab():
#     return render_template('ta_course_vocab.html')

# @bp_teacher.route("/ta/course/vocab/search", methods=['POST'])
# @login_required
# def ta_course_vocab_search():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
#     course_id = obj.get("course_id")
#     search_word = obj.get("search_word", "")
    
#     results = db.get_course_vocab(course_id, search_word)

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# @bp_teacher.route("/ta/course/vocab/update", methods=['POST'])
# @login_required
# def ta_course_vocab_update():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
    
#     course_id = obj.get("course_id")
#     word_id = obj.get("word_id")
#     update_CHword = obj.get("update_CHword")
#     update_TWword = obj.get("update_TWword")
#     update_TLPA = obj.get("update_TLPA")
    
#     results = db.update_course_vocab(course_id, word_id, update_CHword, update_TWword, update_TLPA)

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# @bp_teacher.route("/ta/course/vocab/insert", methods=['POST'])
# @login_required
# def ta_course_vocab_insert():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
    
#     course_id = obj.get("course_id")
#     insert_CHword = obj.get("insert_CHword")
#     insert_TWword = obj.get("insert_TWword")
#     insert_TLPA = obj.get("insert_TLPA")
    
#     results = db.insert_course_vocab(course_id, insert_CHword, insert_TWword, insert_TLPA)

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# @bp_teacher.route("/ta/course/vocab/delete", methods=['POST'])
# @login_required
# def ta_course_vocab_delete():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
    
#     course_id = obj.get("course_id")
#     delete_id = obj.get("delete_id")
    
#     results = db.delete_course_vocab(course_id, delete_id)

#     return jsonify({
#         "status": "success",
#         "results": results
#     })

# # 翻譯功能 (中文 -> 台羅/台語)
# @bp_teacher.route("/ta/course/vocab/translate", methods=['POST'])
# @login_required
# def ta_course_vocab_translate():
#     _json = request.get_json(silent=True) or {}
#     word_tw = _json.get('TW', '')
#     word_tlpa = tlpa_trans(word_tw) 
#     return jsonify({"tlpa": word_tlpa})

# # 試聽/合成語音功能
# @bp_teacher.route("/ta/course/vocab/trylisten", methods=['POST'])
# @login_required
# def ta_course_vocab_trylisten():
#     obj = request.get_json(force=True)
#     tlpa = (obj.get("TLPA") or "").strip()
#     name_hint = (obj.get("name_hint") or "audio").strip()
    
#     # 處理檔名安全
#     safe_name = re.sub(r'[\\/:*?"<>|]+', '', name_hint)
#     safe_name = re.sub(r'\s+', '_', safe_name).strip('_')
    
#     final_name = tts(tlpa, save_name=safe_name)
    
#     return jsonify({"name": final_name})

# # 提交確認 (如果原本邏輯有用到，保留為空接口回傳 200)
# @bp_teacher.route("/ta/course/vocab/commit", methods=['POST'])
# @login_required
# def ta_course_vocab_commit():
#     # 實際上 insert/update/delete 時我們已經 commit 了，這裡主要回應前端流程
#     return "", 200
from flask import Blueprint, render_template, request, session, jsonify, redirect
import re
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

# 嘗試引入服務
try:
    from app.services.ttp_service_api import process as tlpa_trans
    from app.services.hts_service_api import tts
except ImportError:
    def tlpa_trans(word): return f"[Mock TLPA] {word}"
    def tts(tlpa, save_name=None): return save_name or "test_audio"

bp_teacher = Blueprint('teacher', __name__)

def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('loggin') or session.get('identity') != 'Teacher':
            return redirect('/branch')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@bp_teacher.route('/home/ta')
@login_required
def ta_home():
    return render_template('teacher_home.html')

@bp_teacher.route('/ta/template')
@login_required
def ta_template():
    return render_template('teacher_template.html')

@bp_teacher.route('/ta/class_management')
@login_required
def ta_class_management():
    db = SQL()
    teacher_id = session.get('teacher_id')
    classes = db.get_teacher_classes(teacher_id)
    return render_template('teacher_class_management.html', classes=classes)

@bp_teacher.route('/api/create_class', methods=['POST'])
def api_create_class():
    if session.get('identity') != 'Teacher' or not session.get('teacher_id'):
        return jsonify({"status": "error", "message": "請先登入"}), 403
    db = SQL()
    obj = request.get_json(force=True)
    class_name = obj.get('class_name', '新班級')
    teacher_id = session['teacher_id']
    school_id = session['school_id']
    result = db.create_new_class(teacher_id, school_id, class_name)
    if result["status"]:
        return jsonify({"status": "success", "class_code": result["class_code"]})
    else:
        return jsonify({"status": "error", "message": result["msg"]})

@bp_teacher.route('/ta/leaderboard')
@login_required
def ta_leaderboard():
    return render_template('teacher_leaderboard.html')

@bp_teacher.route('/leaderboard_ta_query', methods=['POST'])
@login_required
def leaderboard_ta_query():
    db = SQL()
    class_name_kw = request.form.get('input_id', '').strip()
    data = []
    error_msg = ""
    target_idx = [9999999] 

    if not class_name_kw:
        data = []
    else:
        try:
            data = db.get_class_leaderboard_by_keyword(class_name_kw)
            if not data:
                error_msg = "*查無此班級或尚無資料*"
        except Exception as e:
            print(e)
            data = []
            error_msg = "*系統查詢錯誤*"
    
    return render_template('teacher_leaderboard_result.html', data=data, target_idx=target_idx, error_msg=error_msg)

# === Game Template ===
@bp_teacher.route('/template/catch_egg')
@login_required
def ta_template_catch(): return render_template('teacher_template_catch.html')

@bp_teacher.route('/template/map')
@login_required
def ta_template_map(): return render_template('teacher_template_map.html')

@bp_teacher.route('/template/fruit_cutter')
@login_required
def ta_template_fruit(): return render_template('teacher_template_fruit.html')

@bp_teacher.route('/template/flipping_card')
@login_required
def ta_template_card(): return render_template('teacher_template_card.html')

@bp_teacher.route("/template/course/search", methods=['POST'])
@login_required
def template_course_search():
    db = SQL()
    teacher_id = session.get('teacher_id')
    courses = db.get_course("")
    classes = db.get_teacher_classes(teacher_id)
    return jsonify({"status": "success", "results": courses, "classes": classes})

@bp_teacher.route("/template/course/update", methods=['POST'])
@login_required
def template_course_update():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    if not all([obj.get("game_name"), obj.get("course_id"), obj.get("class_id")]):
        return jsonify({"status": "error", "message": "資料不完整"})
    success = db.update_classgame(obj.get("class_id"), obj.get("game_name"), obj.get("course_id"))
    return jsonify({"status": "success" if success else "error"})

# === Course Management ===
@bp_teacher.route('/ta/course')
@login_required
def ta_course(): return render_template('ta_course.html')

@bp_teacher.route("/ta/course/search", methods=['POST'])
@login_required
def ta_course_search():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.get_course(obj.get("search_name", ""))
    return jsonify({"status": "success", "results": results})

@bp_teacher.route("/ta/course/update", methods=['POST'])
@login_required
def ta_course_update():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.update_course(obj.get("course_id"), obj.get("update_name"))
    if hasattr(db, 'conn'): db.conn.commit()
    return jsonify({"status": "success", "results": results})

@bp_teacher.route("/ta/course/insert", methods=['POST'])
@login_required
def ta_course_insert():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.insert_course(obj.get("insert_name"))
    if hasattr(db, 'conn'): db.conn.commit()
    return jsonify({"status": "success", "results": results})

@bp_teacher.route("/ta/course/delete", methods=['POST'])
@login_required
def ta_course_delete():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.delete_course(obj.get("delete_id"))
    if hasattr(db, 'conn'): db.conn.commit()
    return jsonify({"status": "success", "results": results})

@bp_teacher.route("/ta/course/update/modifyts", methods=['POST'])
@login_required
def ta_course_update_modifyts():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.update_modifyts(obj.get("course_id"))
    if hasattr(db, 'conn'): db.conn.commit()
    return jsonify({"status": "success", "results": results})

# === Vocab Management ===
@bp_teacher.route('/ta/course/vocab')
@login_required
def ta_course_vocab(): return render_template('ta_course_vocab.html')

@bp_teacher.route("/ta/course/vocab/search", methods=['POST'])
@login_required
def ta_course_vocab_search():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.get_course_vocab(obj.get("course_id"), obj.get("search_word", ""))
    return jsonify({"status": "success", "results": results})

@bp_teacher.route("/ta/course/vocab/update", methods=['POST'])
@login_required
def ta_course_vocab_update():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.update_course_vocab(obj.get("course_id"), obj.get("word_id"), obj.get("update_CHword"), obj.get("update_TWword"), obj.get("update_TLPA"))
    return jsonify({"status": "success", "results": results})

@bp_teacher.route("/ta/course/vocab/insert", methods=['POST'])
@login_required
def ta_course_vocab_insert():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.insert_course_vocab(obj.get("course_id"), obj.get("insert_CHword"), obj.get("insert_TWword"), obj.get("insert_TLPA"))
    return jsonify({"status": "success", "results": results})

@bp_teacher.route("/ta/course/vocab/delete", methods=['POST'])
@login_required
def ta_course_vocab_delete():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    results = db.delete_course_vocab(obj.get("course_id"), obj.get("delete_id"))
    return jsonify({"status": "success", "results": results})

@bp_teacher.route("/ta/course/vocab/translate", methods=['POST'])
@login_required
def ta_course_vocab_translate():
    _json = request.get_json(silent=True) or {}
    word_tlpa = tlpa_trans(_json.get('TW', '')) 
    return jsonify({"tlpa": word_tlpa})

@bp_teacher.route("/ta/course/vocab/trylisten", methods=['POST'])
@login_required
def ta_course_vocab_trylisten():
    obj = request.get_json(force=True)
    tlpa = (obj.get("TLPA") or "").strip()
    name_hint = (obj.get("name_hint") or "audio").strip()
    safe_name = re.sub(r'[\\/:*?"<>|]+', '', name_hint)
    safe_name = re.sub(r'\s+', '_', safe_name).strip('_')
    final_name = tts(tlpa, save_name=safe_name)
    return jsonify({"name": final_name})

@bp_teacher.route("/ta/course/vocab/commit", methods=['POST'])
@login_required
def ta_course_vocab_commit():
    return "", 200