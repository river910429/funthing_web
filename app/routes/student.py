# routes/student.py
# from flask import Blueprint, render_template, request, session, jsonify, redirect
# from database import SQL
# import os
# import sys
# import random
# import json
# import traceback
# from datetime import datetime

# # [修正] 簡潔版路徑設定：將上一層目錄 (根目錄) 加入 sys.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# # 如果有這些外部服務的檔案，請確保它們在專案目錄中
# try:
#     from stt_service_api import taiwanese_recognize
#     from ttp_service_api import process as tlpa_trans
#     from hts_service_api import tts
#     print("[Info] Student services (STT/TTS) loaded.")
# except Exception as e:
#     # This block MUST be present to see the error
#     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#     print("[Error] Failed to load Student services:")
#     traceback.print_exc() 
#     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

# bp_student = Blueprint('student', __name__)

# # 配置 (需與 app.py 一致)
# APP_ROOT = os.path.join(os.getcwd())
# APP_TEMP = os.path.join(APP_ROOT, "temp")
# if not os.path.exists(APP_TEMP):
#     os.makedirs(APP_TEMP)
# ffmpeg_path = "ffmpeg" # 確保系統有安裝 ffmpeg

# # 檢查登入
# def login_required(f):
#     def wrapper(*args, **kwargs):
#         if not session.get('loggin') or session.get('identity') != 'Student':
#             return redirect('/login/stu')
#         return f(*args, **kwargs)
#     wrapper.__name__ = f.__name__
#     return wrapper

# # === 首頁與基礎 ===
# @bp_student.route('/home/stu')
# @login_required
# def stu_home():
#     session['pre_page_equip'] = request.url
#     return render_template('student_home.html')

# @bp_student.route('/login/name')
# def login_name():
#     # 學生初次登入如果沒有名字會導向這
#     return render_template('login_name.html')

# @bp_student.route('/login/name', methods=['POST'])
# def login_name_post():
#     db = SQL()
#     obj = request.get_json()
#     name = obj['name']
#     db.set_name(session['identity'], session['account'], name)
#     return jsonify({"status": "success", "url": "/home/stu"})

# @bp_student.route('/redirect')
# def my_redirect():
#     r_type = request.args.get('r_type')
#     if r_type == "equip" and session.get('pre_page_equip'):
#         return jsonify({"status": "success", "url": session.get('pre_page_equip')})
#     elif r_type == "lgame" and session.get('pre_page_lgame'):
#         return jsonify({"status": "success", "url": session.get('pre_page_lgame')})
#     return jsonify({"status": "error", "url": ""})

# # === 頁面路由 ===
# @bp_student.route('/stu/game')
# @login_required
# def stu_game():
#     session['pre_page_equip'] = request.url
#     session['pre_page_lgame'] = request.url
#     return render_template('student_game.html')

# @bp_student.route('/stu/practice')
# @login_required
# def stu_practice():
#     session['pre_page_equip'] = request.url
#     return render_template('student_practice.html')

# @bp_student.route('/stu/leaderboard')
# @login_required
# def stu_leaderboard():
#     session['pre_page_equip'] = request.url
#     return render_template('student_leaderboard.html')

# # 海報牆路由
# @bp_student.route('/poster/catch_egg')
# def stu_poster_catch(): return _poster_page('student_poster_catch.html')
# @bp_student.route('/poster/map')
# def stu_poster_map(): return _poster_page('student_poster_map.html')
# @bp_student.route('/poster/fruit_cutter')
# def stu_poster_fruit(): return _poster_page('student_poster_fruit.html')
# @bp_student.route('/poster/flipping_card')
# def stu_poster_card(): return _poster_page('student_poster_card.html')

# def _poster_page(template):
#     session['pre_page_equip'] = request.url
#     session['pre_page_lgame'] = request.url
#     return render_template(template)

# # === [新增] 學生專用課程查詢 API ===
# @bp_student.route('/stu/course/search', methods=['POST'])
# @login_required
# def stu_course_search():
#     db = SQL()
#     obj = request.get_json(silent=True) or {}
#     search_name = obj.get("search_name", "")
#     # 呼叫 database.py 中的 get_course 方法
#     courses = db.get_course(search_name)
    
#     return jsonify({
#         "status": "success",
#         "results": courses
#     })


# # === 排行榜 API ===
# @bp_student.route('/leaderboard_class_query', methods=['GET'])
# @login_required
# def leaderboard_class_query():
#     db = SQL()
#     account = session.get('account')
#     # 使用 account 查出 class_id
#     _, class_id = db.get_student_school_and_class_by_account(account)
    
#     result = []
#     if class_id:
#         result = db.get_class_leaderboard(class_id)
    
#     return jsonify({
#         "status": "success",
#         "data": result,
#         "target_idx": account
#     })

# @bp_student.route('/leaderboard_school_query', methods=['GET'])
# @login_required
# def leaderboard_school_query():
#     db = SQL()
#     account = session.get('account')
#     result = db.get_school_leaderboard()
#     return jsonify({
#         "status": "success",
#         "data": result,
#         "target_idx": account
#     })

# # === 裝備系統 ===
# @bp_student.route('/stu/equipment')
# def stu_equipment():
#     return render_template('stu_equip.html')

# @bp_student.route('/stu/equipment/get', methods=['GET'])
# @login_required
# def stu_equipment_get():
#     db = SQL()
#     stu_id = session.get('stu_id')
#     level, score = db.get_stu_level_score(stu_id)
#     equip_now = db.get_stu_equip_now(stu_id)
#     equip_info = db.get_stu_equip_gain_info(stu_id)
    
#     # 整理列表，索引0固定為已擁有(預設裝備)
#     equip_list = list(equip_info)
#     equip_list.insert(0, 1)

#     return jsonify({
#         "score": score,
#         "level": level,
#         "equip_cur": equip_now,
#         "equip_list": equip_list
#     })

# @bp_student.route('/stu/equipment/update', methods=['POST'])
# @login_required
# def stu_equipment_update():
#     db = SQL()
#     stu_id = session.get('stu_id')
#     obj = request.get_json()
#     status = db.update_wear_now(obj["select_equip_id"], stu_id)
#     return jsonify({'status': status})

# @bp_student.route('/wearing', methods=['POST'])
# @login_required
# def wearing():
#     # 這是舊版或某些頁面可能用到的 Form Post 路由
#     db = SQL()
#     stu_id = session.get('stu_id')
#     equip_id = request.form.get('equip_id')
#     status = db.update_wear_now(equip_id, stu_id)
#     return jsonify({'status': status})


# # === 分數上傳與遊戲結果 ===
# @bp_student.route('/score_upload', methods=['POST'])
# @login_required
# def score_uploading():
#     db = SQL()
#     stu_id = session.get('stu_id')
#     score = int(request.form.get('score'))
    
#     prev_level, prev_score = db.get_stu_level_score(stu_id)
#     equip_now = db.get_stu_equip_now(stu_id)
#     equip_info = db.get_stu_equip_gain_info(stu_id)
    
#     new_score = prev_score + score
    
#     # 計算等級
#     new_level = 0
#     if new_score >= 50000: new_level = 5
#     elif new_score >= 20000: new_level = 4
#     elif new_score >= 12500: new_level = 3
#     elif new_score >= 7500: new_level = 2
#     elif new_score >= 2500: new_level = 1
    
#     # 計算新獲得武器
#     weapon_gain_count = 0
#     if new_score >= 90000: weapon_gain_count = 7
#     elif new_score >= 80000: weapon_gain_count = 6
#     elif new_score >= 70000: weapon_gain_count = 5
#     elif new_score >= 60000: weapon_gain_count = 4
#     elif new_score >= 42500: weapon_gain_count = 3
#     elif new_score >= 35000: weapon_gain_count = 2
#     elif new_score >= 27500: weapon_gain_count = 1
    
#     weapon_gain_flag = False
#     if weapon_gain_count > 0:
#         for i in range(weapon_gain_count):
#             if equip_info[i] == 0:
#                 weapon_gain_flag = True
#                 db.update_equipment_gain(stu_id, i+1)

#     status = db.upload_score(stu_id, new_score, new_level)
#     upgrade = (new_level > prev_level)
    
#     return jsonify({
#         'status': status, 
#         'upgrade': upgrade, 
#         'level': new_level, 
#         'weapon_gain': weapon_gain_flag, 
#         'weapon': weapon_gain_count, 
#         'wear_now': equip_now
#     })

# @bp_student.route('/game_result', methods=['POST'])
# @bp_student.route('/game/<path:game>/game_result', methods=['POST'])
# def display_game_result_post(game=None):
#     session["result_lst"] = request.get_json()["data"]
#     return jsonify({'status':"success"})

# @bp_student.route('/game_result', methods=['GET'])
# @bp_student.route('/game/<path:game>/game_result', methods=['GET'])
# def display_game_result(game=None):
#     data = session.get('result_lst', [])
#     return render_template('game_result_page.html', data=data)


# # === 遊戲邏輯與 Tutorial ===
# def _game_column_from_name(name):
#     mapping = {
#         "flipping_card": "game1",
#         "catch_egg": "game2",
#         "fruit_cutter": "game3",
#         "map": "game4",
#     }
#     return mapping.get(name)

# def _resolve_course_id(game_key):
#     # 若 URL 有帶參數優先
#     cid = request.args.get('course_id')
#     if cid and str(cid).isdigit(): return int(cid)
    
#     # 否則查資料庫
#     db = SQL()
#     account = session.get('account')
#     if not account: return None
#     sid, cid = db.get_student_school_and_class_by_account(account)
#     if not sid or not cid: return None
#     return db.get_classgame(sid, cid, game_key)

# # 遊戲路由產生器 (避免重複代碼)
# def _game_route(name, template, word_count=8, loop_words=False):
#     game_key = _game_column_from_name(name)
#     course_id = _resolve_course_id(game_key)
#     if not course_id:
#         return "尚未為本班級設定此遊戲課程，請通知老師。", 400
    
#     db = SQL()
#     words = db.get_course_vocab(course_id, '')
    
#     if loop_words and len(words) < word_count:
#         while len(words) < word_count:
#             words.extend(words)
            
#     random.shuffle(words)
#     words = words[:word_count]
    
#     game_data = {"gameneed": [w["TWword"]+"<br>"+w["TLPA"] for w in words]}
#     return render_template(template, course=game_data)

# def _tutorial_route(name, template):
#     session['pre_page_equip'] = request.url
#     game_key = _game_column_from_name(name)
#     course_id = _resolve_course_id(game_key)
#     if not course_id:
#         return "尚未為本班級設定此遊戲課程，請通知老師。", 400
#     return render_template(template, course_id=course_id)

# # 定義具體遊戲路由
# @bp_student.route('/game/flipping_card')
# def card_game(): return _game_route("flipping_card", 'game_card.html', 8, True)
# @bp_student.route('/game/flipping_card_tutorial')
# def card_tutorial(): return _tutorial_route("flipping_card", 'game_card_tutorial.html')

# @bp_student.route('/game/catch_egg')
# def egg_game(): return _game_route("catch_egg", 'game_catch_egg.html', 8)
# @bp_student.route('/game/catch_egg_tutorial')
# def egg_tutorial(): return _tutorial_route("catch_egg", 'game_catch_egg_tutorial.html')

# @bp_student.route('/game/fruit_cutter')
# def fruit_game(): return _game_route("fruit_cutter", 'game_fruit_cutter.html', 8, True)
# @bp_student.route('/game/fruit_cutter_tutorial')
# def fruit_tutorial(): return _tutorial_route("fruit_cutter", 'game_fruit_cutter_tutorial.html')

# @bp_student.route('/game/map')
# def map_game(): return _game_route("map", 'game_map.html', 6, True)
# @bp_student.route('/game/map_tutorial')
# def map_tutorial(): return _tutorial_route("map", 'game_map_tutorial.html')


# # === 語音與 AI ===
# @bp_student.route("/save_audio", methods=['POST'])
# def save_audio():
#     # 接收錄音檔
#     audio_data = request.files["data"]
#     session['now'] = datetime.now()
#     date = session['now'].strftime("%Y%m%d")
#     timestamp = session['now'].strftime("%H%M%S")
    
#     record_temp_path = os.path.join(APP_TEMP, "recording.wav")
#     record_path = os.path.join(APP_TEMP, f"{date}_{timestamp}.wav")
#     print("音檔位置：" + record_path)
    
#     with open(record_temp_path, 'wb') as audio:
#         audio_data.save(audio)
        
#     # 轉檔
#     os.system(f"{ffmpeg_path} -loglevel error -y -f webm -i {record_temp_path} -ar 16000 -ac 1 {record_path}")
#     return jsonify({"suc": "success"})

# @bp_student.route("/predict", methods=['GET'])
# def predict():
#     if 'now' not in session: return jsonify({"recognition": "Error: No Audio"})
#     date = session['now'].strftime("%Y%m%d")
#     timestamp = session['now'].strftime("%H%M%S")
#     record_path = os.path.join(APP_TEMP, f"{date}_{timestamp}.wav")
    
#     if not os.path.exists(record_path):
#         return jsonify({"recognition": "Error: File Not Found"})
        
#     res = taiwanese_recognize(record_path)
#     return jsonify({"recognition": res})

# # 翻譯與試聽 (雖然這通常是老師用，但有時候學生介面也可能呼叫，先放這或共用)
# @bp_student.route("/ta/course/vocab/translate", methods=['POST'])
# def api_translate():
#     _json = request.get_json()
#     word_tlpa = tlpa_trans(_json['TW']) 
#     return jsonify({"tlpa": word_tlpa})

# @bp_student.route("/ta/course/vocab/trylisten", methods=['POST'])
# def api_trylisten():
#     obj = request.get_json(force=True)
#     tlpa = (obj.get("TLPA") or "").strip()
#     name_hint = (obj.get("name_hint") or "audio").strip()
#     # 簡易檔名處理
#     import re
#     safe_name = re.sub(r'[\\/:*?"<>|]+', '', name_hint)
#     safe_name = re.sub(r'\s+', '_', safe_name).strip('_')
    
#     final_name = tts(tlpa, save_name=safe_name)
#     return jsonify({"name": final_name})
from flask import Blueprint, render_template, request, session, jsonify, redirect, current_app
import os
import random
import traceback
from datetime import datetime

# [Refactor] 改用絕對路徑引用，假設 database.py 已移至 app/utils/
try:
    from app.utils.database import SQL
except ImportError:
    # Fallback if user hasn't moved the file yet, though not recommended
    import sys
    sys.path.append(os.getcwd())
    try:
        from funthing_teach_web.app.utils.database import SQL
    except:
        print("[Error] Cannot import database. Please ensure app/utils/database.py exists.")

# [Refactor] 服務 API 引用
try:
    from app.services.stt_service_api import taiwanese_recognize
    from app.services.ttp_service_api import process as tlpa_trans
    from app.services.hts_service_api import tts
    print("[Info] Student services (STT/TTS) loaded.")
except Exception as e:
    print("[Warning] Failed to load Student services (STT/TTS). Mocking might be needed.")
    # traceback.print_exc()

bp_student = Blueprint('student', __name__)

ffmpeg_path = "ffmpeg" 

# 權限檢查 Decorator
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('loggin') or session.get('identity') != 'Student':
            return redirect('/login/stu')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# === 首頁與基礎 ===
@bp_student.route('/home/stu')
@login_required
def stu_home():
    session['pre_page_equip'] = request.url
    return render_template('student_home.html')

@bp_student.route('/login/name')
def login_name():
    return render_template('login_name.html')

@bp_student.route('/login/name', methods=['POST'])
def login_name_post():
    db = SQL()
    obj = request.get_json()
    name = obj['name']
    db.set_name(session['identity'], session['account'], name)
    return jsonify({"status": "success", "url": "/home/stu"})

@bp_student.route('/redirect')
def my_redirect():
    r_type = request.args.get('r_type')
    if r_type == "equip" and session.get('pre_page_equip'):
        return jsonify({"status": "success", "url": session.get('pre_page_equip')})
    elif r_type == "lgame" and session.get('pre_page_lgame'):
        return jsonify({"status": "success", "url": session.get('pre_page_lgame')})
    return jsonify({"status": "error", "url": ""})

# === 頁面路由 ===
@bp_student.route('/stu/game')
@login_required
def stu_game():
    session['pre_page_equip'] = request.url
    session['pre_page_lgame'] = request.url
    return render_template('student_game.html')

@bp_student.route('/stu/practice')
@login_required
def stu_practice():
    session['pre_page_equip'] = request.url
    return render_template('student_practice.html')

@bp_student.route('/stu/leaderboard')
@login_required
def stu_leaderboard():
    session['pre_page_equip'] = request.url
    return render_template('student_leaderboard.html')

# 海報牆
@bp_student.route('/poster/catch_egg')
def stu_poster_catch(): return _poster_page('student_poster_catch.html')
@bp_student.route('/poster/map')
def stu_poster_map(): return _poster_page('student_poster_map.html')
@bp_student.route('/poster/fruit_cutter')
def stu_poster_fruit(): return _poster_page('student_poster_fruit.html')
@bp_student.route('/poster/flipping_card')
def stu_poster_card(): return _poster_page('student_poster_card.html')

def _poster_page(template):
    session['pre_page_equip'] = request.url
    session['pre_page_lgame'] = request.url
    return render_template(template)

# === 課程查詢 API ===
@bp_student.route('/stu/course/search', methods=['POST'])
@login_required
def stu_course_search():
    db = SQL()
    obj = request.get_json(silent=True) or {}
    search_name = obj.get("search_name", "")
    courses = db.get_course(search_name)
    return jsonify({"status": "success", "results": courses})

# === 排行榜 API ===
@bp_student.route('/leaderboard_class_query', methods=['GET'])
@login_required
def leaderboard_class_query():
    db = SQL()
    account = session.get('account')
    # 注意：需確保 database.py 實作了此方法
    # res = db.get_student_school_and_class_by_account(account)
    # 這裡假設你的 DB 邏輯與原本一致
    try:
        _, class_id = db.get_student_school_and_class_by_account(account)
        result = db.get_class_leaderboard(class_id) if class_id else []
    except:
        result = []
    
    return jsonify({"status": "success", "data": result, "target_idx": account})

@bp_student.route('/leaderboard_school_query', methods=['GET'])
@login_required
def leaderboard_school_query():
    db = SQL()
    account = session.get('account')
    result = db.get_school_leaderboard()
    return jsonify({"status": "success", "data": result, "target_idx": account})

# === 裝備系統 ===
@bp_student.route('/stu/equipment')
def stu_equipment():
    return render_template('stu_equip.html')

@bp_student.route('/stu/equipment/get', methods=['GET'])
@login_required
def stu_equipment_get():
    db = SQL()
    stu_id = session.get('stu_id')
    level, score = db.get_stu_level_score(stu_id)
    equip_now = db.get_stu_equip_now(stu_id)
    equip_info = db.get_stu_equip_gain_info(stu_id)
    
    equip_list = list(equip_info)
    equip_list.insert(0, 1)

    return jsonify({
        "score": score, "level": level, "equip_cur": equip_now, "equip_list": equip_list
    })

@bp_student.route('/stu/equipment/update', methods=['POST'])
@login_required
def stu_equipment_update():
    db = SQL()
    stu_id = session.get('stu_id')
    obj = request.get_json()
    status = db.update_wear_now(obj["select_equip_id"], stu_id)
    return jsonify({'status': status})

# === 分數上傳 ===
@bp_student.route('/score_upload', methods=['POST'])
@login_required
def score_uploading():
    db = SQL()
    stu_id = session.get('stu_id')
    score = int(request.form.get('score'))
    
    prev_level, prev_score = db.get_stu_level_score(stu_id)
    equip_now = db.get_stu_equip_now(stu_id)
    equip_info = db.get_stu_equip_gain_info(stu_id)
    
    new_score = prev_score + score
    
    new_level = 0
    if new_score >= 50000: new_level = 5
    elif new_score >= 20000: new_level = 4
    elif new_score >= 12500: new_level = 3
    elif new_score >= 7500: new_level = 2
    elif new_score >= 2500: new_level = 1
    
    weapon_gain_count = 0
    if new_score >= 90000: weapon_gain_count = 7
    elif new_score >= 80000: weapon_gain_count = 6
    elif new_score >= 70000: weapon_gain_count = 5
    elif new_score >= 60000: weapon_gain_count = 4
    elif new_score >= 42500: weapon_gain_count = 3
    elif new_score >= 35000: weapon_gain_count = 2
    elif new_score >= 27500: weapon_gain_count = 1
    
    weapon_gain_flag = False
    if weapon_gain_count > 0:
        for i in range(weapon_gain_count):
            if equip_info[i] == 0:
                weapon_gain_flag = True
                db.update_equipment_gain(stu_id, i+1)

    status = db.upload_score(stu_id, new_score, new_level)
    upgrade = (new_level > prev_level)
    
    return jsonify({
        'status': status, 'upgrade': upgrade, 'level': new_level, 
        'weapon_gain': weapon_gain_flag, 'weapon': weapon_gain_count, 'wear_now': equip_now
    })

@bp_student.route('/game_result', methods=['POST'])
@bp_student.route('/game/<path:game>/game_result', methods=['POST'])
def display_game_result_post(game=None):
    session["result_lst"] = request.get_json()["data"]
    return jsonify({'status':"success"})

@bp_student.route('/game_result', methods=['GET'])
@bp_student.route('/game/<path:game>/game_result', methods=['GET'])
def display_game_result(game=None):
    data = session.get('result_lst', [])
    return render_template('game_result_page.html', data=data)

# === 遊戲與 Tutorial ===
def _game_column_from_name(name):
    mapping = {
        "flipping_card": "game1", "catch_egg": "game2",
        "fruit_cutter": "game3", "map": "game4",
        "pronunciation": "game5",
    }
    return mapping.get(name)

def _resolve_course_id(game_key):
    cid = request.args.get('course_id')
    if cid and str(cid).isdigit(): return int(cid)
    
    db = SQL()
    account = session.get('account')
    if not account: return None
    try:
        sid, cid = db.get_student_school_and_class_by_account(account)
        if not sid or not cid: return None
        return db.get_classgame(sid, cid, game_key)
    except:
        return None

def _game_route(name, template, word_count=8, loop_words=False):
    game_key = _game_column_from_name(name)
    course_id = _resolve_course_id(game_key)
    if not course_id:
        return "尚未為本班級設定此遊戲課程，請通知老師。", 400
    
    db = SQL()
    words = db.get_course_vocab(course_id, '')
    
    if loop_words and len(words) < word_count:
        while len(words) < word_count:
            words.extend(words)
            
    random.shuffle(words)
    words = words[:word_count]
    
    game_data = {"gameneed": [w["TWword"]+"<br>"+w["TLPA"] for w in words]}
    return render_template(template, course=game_data)

def _tutorial_route(name, template):
    session['pre_page_equip'] = request.url
    game_key = _game_column_from_name(name)
    course_id = _resolve_course_id(game_key)
    if not course_id:
        return "尚未為本班級設定此遊戲課程，請通知老師。", 400
    return render_template(template, course_id=course_id)

@bp_student.route('/game/flipping_card')
def card_game(): return _game_route("flipping_card", 'game_card.html', 8, True)
@bp_student.route('/game/flipping_card_tutorial')
def card_tutorial(): return _tutorial_route("flipping_card", 'game_card_tutorial.html')

@bp_student.route('/game/catch_egg')
def egg_game(): return _game_route("catch_egg", 'game_catch_egg.html', 8)
@bp_student.route('/game/catch_egg_tutorial')
def egg_tutorial(): return _tutorial_route("catch_egg", 'game_catch_egg_tutorial.html')

@bp_student.route('/game/fruit_cutter')
def fruit_game(): return _game_route("fruit_cutter", 'game_fruit_cutter.html', 8, True)
@bp_student.route('/game/fruit_cutter_tutorial')
def fruit_tutorial(): return _tutorial_route("fruit_cutter", 'game_fruit_cutter_tutorial.html')

@bp_student.route('/game/map')
def map_game(): return _game_route("map", 'game_map.html', 6, True)
@bp_student.route('/game/map_tutorial')
def map_tutorial(): return _tutorial_route("map", 'game_map_tutorial.html')

@bp_student.route('/game/pronunciation')
def pronunciation_game(): return _game_route("pronunciation",'game_pronunciation.html', 8, True)
@bp_student.route('/game/pronunciation_tutorial')
def pronunciation_tutorial(): return _tutorial_route("pronunciation",'game_pronunciation_tutorial.html' )

# === 語音功能 ===
@bp_student.route("/save_audio", methods=['POST'])
def save_audio():
    audio_data = request.files["data"]
    session['now'] = datetime.now()
    date = session['now'].strftime("%Y%m%d")
    timestamp = session['now'].strftime("%H%M%S")
    
    # 使用 current_app.config 取得路徑
    APP_TEMP = current_app.config['TEMP_FOLDER']
    
    record_temp_path = os.path.join(APP_TEMP, "recording.wav")
    record_path = os.path.join(APP_TEMP, f"{date}_{timestamp}.wav")
    
    with open(record_temp_path, 'wb') as audio:
        audio_data.save(audio)
        
    os.system(f"{ffmpeg_path} -loglevel error -y -f webm -i {record_temp_path} -ar 16000 -ac 1 {record_path}")
    return jsonify({"suc": "success"})

@bp_student.route("/predict", methods=['GET'])
def predict():
    if 'now' not in session: return jsonify({"recognition": "Error: No Audio"})
    date = session['now'].strftime("%Y%m%d")
    timestamp = session['now'].strftime("%H%M%S")
    APP_TEMP = current_app.config['TEMP_FOLDER']
    record_path = os.path.join(APP_TEMP, f"{date}_{timestamp}.wav")
    
    if not os.path.exists(record_path):
        return jsonify({"recognition": "Error: File Not Found"})
        
    try:
        res = taiwanese_recognize(record_path)
    except:
        res = "Mock Recognition Result" # Fallback if service not running
    return jsonify({"recognition": res})