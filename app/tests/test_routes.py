from unittest.mock import patch, MagicMock
from flask import session
import io

# === 基礎頁面測試 ===

def test_home_page(client):
    """測試首頁是否正常"""
    response = client.get('/')
    assert response.status_code == 200

def test_login_page_loads(client):
    """測試登入頁面是否可訪問"""
    response = client.get('/login/stu')
    assert response.status_code == 200
    assert b"student_login.html" in response.data or b"login" in response.data.lower()

def test_protected_route_redirects(client):
    """測試未登入訪問學生首頁應導向登入"""
    response = client.get('/home/stu', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path != '/home/stu'

def test_student_login_session(client):
    """模擬學生登入後的狀態"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
        sess['account'] = 'test_student@example.com'
    response = client.get('/home/stu')
    assert response.status_code == 200

# === 老師相關測試 ===

def test_teacher_login_page_loads(client):
    """測試老師登入頁面是否可訪問"""
    response = client.get('/login/ta')
    assert response.status_code == 200
    # [修正] 改為檢查頁面內容特有的 CSS 檔名，而非模板檔名
    assert b"login_page_ta.css" in response.data

def test_teacher_protected_route_redirects(client):
    """測試未登入訪問老師首頁應導向登入"""
    response = client.get('/home/ta', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path != '/home/ta'

def test_teacher_login_session(client):
    """模擬老師登入後的狀態"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'
        sess['account'] = 'test_teacher@example.com'
        sess['teacher_id'] = 1
    response = client.get('/home/ta')
    assert response.status_code == 200

# === API 與 功能邏輯測試 (使用 Mock 模擬 DB) ===

@patch('app.routes.student.SQL')
def test_student_course_search_api(MockSQL, client):
    """測試學生搜尋課程 API"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
    
    mock_db_instance = MockSQL.return_value
    mock_db_instance.get_course.return_value = [{"id": 1, "name": "台語初級"}]
    
    response = client.post('/stu/course/search', json={"search_name": "台語"})
    
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['results'][0]['name'] == "台語初級"

@patch('app.routes.teacher.SQL')
def test_create_class_api(MockSQL, client):
    """測試老師建立班級 API"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'
        sess['teacher_id'] = 1
        sess['school_id'] = 100
        
    mock_db_instance = MockSQL.return_value
    mock_db_instance.create_new_class.return_value = {"status": True, "class_code": "ABC12345", "msg": "Success"}
    
    response = client.post('/api/create_class', json={"class_name": "測試班級"})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['class_code'] == "ABC12345"

@patch('app.routes.auth.SQL')
def test_verifying_login_logic(MockSQL, client):
    """測試驗證登入 API"""
    mock_db_instance = MockSQL.return_value
    mock_db_instance.get_student_school_and_class_by_account.return_value = (1, 101)
    mock_db_instance.validate_password.return_value = True
    mock_db_instance.get_student_id.return_value = 55
    mock_db_instance.get_name.return_value = "王小明"

    with client.session_transaction() as sess:
        sess['identity'] = 'Student'

    response = client.post('/verifying', json={"account": "stu@test.com", "pwd": "123"})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['url'] == '/home/stu'

def test_api_schools(client):
    """測試學校列表 API 是否回傳 JSON"""
    with patch('app.routes.auth.SQL') as MockSQL:
        mock_db_instance = MockSQL.return_value
        mock_db_instance.list_schools.return_value = [(1, 'S001', '測試國小')]
        
        response = client.get('/api/schools')
        assert response.status_code == 200
        assert response.is_json
        data = response.get_json()
        assert len(data['schools']) == 1

def test_404_page(client):
    """測試不存在的頁面"""
    response = client.get('/this_page_definitely_does_not_exist')
    assert response.status_code == 404

# === [已存在] 學生分數與裝備測試 ===

@patch('app.routes.student.SQL')
def test_student_score_upload_logic(MockSQL, client):
    """測試分數上傳與等級升級邏輯"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
        sess['stu_id'] = 123
    
    mock_db = MockSQL.return_value
    mock_db.get_stu_level_score.return_value = (0, 2000)
    mock_db.get_stu_equip_now.return_value = 1
    mock_db.get_stu_equip_gain_info.return_value = [1, 0, 0, 0, 0, 0, 0] 
    mock_db.upload_score.return_value = "success"

    response = client.post('/score_upload', data={"score": 5000})

    assert response.status_code == 200
    data = response.get_json()
    assert data['level'] == 1
    assert data['status'] == "success"
    mock_db.upload_score.assert_called_with(123, 7000, 1)

@patch('app.routes.student.SQL')
def test_student_level_up_max(MockSQL, client):
    """測試直接升到最高等 (Level 5) 與獲得武器"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
        sess['stu_id'] = 123
        
    mock_db = MockSQL.return_value
    mock_db.get_stu_level_score.return_value = (0, 0)
    mock_db.get_stu_equip_now.return_value = 1
    mock_db.get_stu_equip_gain_info.return_value = [0]*7
    mock_db.upload_score.return_value = "success"
    
    response = client.post('/score_upload', data={"score": 90000})
    data = response.get_json()

    assert data['level'] == 5 
    assert data['weapon'] == 7 
    assert data['weapon_gain'] == True

@patch('app.routes.student.SQL')
def test_student_equipment_update(MockSQL, client):
    """測試更換裝備 API"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
        sess['stu_id'] = 123
        
    mock_db = MockSQL.return_value
    mock_db.update_wear_now.return_value = "success"
    
    response = client.post('/stu/equipment/update', json={"select_equip_id": 2})
    
    assert response.status_code == 200
    assert response.get_json()['status'] == "success"

def test_game_result_session_flow(client):
    """測試遊戲結果暫存與讀取 (Session)"""
    game_data = [{"word": "apple", "correct": True}]
    response_post = client.post('/game_result', json={"data": game_data})
    assert response_post.status_code == 200
    
    with client.session_transaction() as sess:
        assert sess['result_lst'] == game_data
        
    response_get = client.get('/game_result')
    assert response_get.status_code == 200
    assert b"game_result.css" in response_get.data

@patch('app.routes.teacher.SQL')
def test_teacher_create_class_edge_cases(MockSQL, client):
    """測試老師建立班級 - 異常狀況"""
    response = client.post('/api/create_class', json={"class_name": "Hack Class"})
    assert response.status_code == 403 

    with client.session_transaction() as sess:
        sess['identity'] = 'Teacher'
        sess['teacher_id'] = 1
        sess['school_id'] = 100
        
    mock_db = MockSQL.return_value
    mock_db.create_new_class.return_value = {"status": False, "msg": "Database Error"}
    
    response = client.post('/api/create_class', json={"class_name": "Error Class"})
    assert response.status_code == 200 
    assert response.get_json()['status'] == 'error'

# === [已存在] 學生玩遊戲與教師更改課程測試 ===

@patch('app.routes.student.SQL')
def test_student_play_game_success(MockSQL, client):
    """測試學生進入遊戲頁面 (成功載入課程單字)"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
        sess['account'] = 'test_stu@example.com'
    
    mock_db = MockSQL.return_value
    mock_db.get_student_school_and_class_by_account.return_value = (1, 101)
    mock_db.get_classgame.return_value = 5
    mock_db.get_course_vocab.return_value = [
        {"TWword": "蘋果", "TLPA": "phing-ko"},
        {"TWword": "香蕉", "TLPA": "kin-tsio"}
    ] * 4 

    response = client.get('/game/flipping_card')
    assert response.status_code == 200
    assert b"phing-ko" in response.data

@patch('app.routes.student.SQL')
def test_student_play_game_no_course(MockSQL, client):
    """測試學生進入遊戲但班級未設定課程"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
        sess['account'] = 'test_stu@example.com'
    
    mock_db = MockSQL.return_value
    mock_db.get_student_school_and_class_by_account.return_value = (1, 101)
    mock_db.get_classgame.return_value = None

    response = client.get('/game/flipping_card')
    assert response.status_code == 400

@patch('app.routes.teacher.SQL')
def test_teacher_update_course_name(MockSQL, client):
    """測試老師修改課程名稱"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'
        sess['teacher_id'] = 1
    
    mock_db = MockSQL.return_value
    mock_db.update_course.return_value = "success"

    response = client.post('/ta/course/update', json={
        "course_id": 10,
        "update_name": "新課程名稱"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "success"
    mock_db.update_course.assert_called_with(10, "新課程名稱")

@patch('app.routes.teacher.SQL')
def test_teacher_update_class_game_mapping(MockSQL, client):
    """測試老師設定班級遊戲對應的課程"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'
        sess['teacher_id'] = 1

    mock_db = MockSQL.return_value
    mock_db.update_classgame.return_value = True

    payload = {
        "class_id": 101,
        "game_name": "game2",
        "course_id": 5
    }
    response = client.post('/template/course/update', json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "success"
    mock_db.update_classgame.assert_called_with(101, "game2", 5)

# === [補齊缺漏] Auth 註冊相關測試 ===

@patch('app.routes.auth.SQL')
def test_register_student_api(MockSQL, client):
    """[新增] 測試學生註冊"""
    mock_db = MockSQL.return_value
    # 模擬邀請碼有效
    mock_db.validate_invite_code.return_value = (101, 1) # class_id, school_id
    # 模擬建立成功
    mock_db.create_student.return_value = True
    mock_db.get_student_id.return_value = 99

    payload = {
        "code": "INVITE123",
        "account": "new_stu@test.com",
        "pwd": "123",
        "name": "New Student",
        "grade": "1",
        "clazz": "2",
        "seat_no": "5"
    }
    response = client.post('/register/stu', json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "success"
    assert data['url'] == "/home/stu"

@patch('app.routes.auth.SQL')
def test_register_teacher_api(MockSQL, client):
    """[新增] 測試老師註冊"""
    mock_db = MockSQL.return_value
    mock_db.ensure_school_by_name.return_value = 1 # school_id
    mock_db.create_teacher_only.return_value = {"status": True}
    mock_db.get_teacher_id.return_value = 88

    payload = {
        "account": "new_ta@test.com",
        "pwd": "123",
        "name": "New Teacher",
        "school": "Test School"
    }
    response = client.post('/register/ta', json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "success"
    assert data['url'] == "/home/ta"

# === [補齊缺漏] 學生其他功能 ===

@patch('app.routes.student.SQL')
def test_student_set_name(MockSQL, client):
    """[新增] 測試學生初次登入設定名稱"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
        sess['account'] = 'stu@test.com'

    mock_db = MockSQL.return_value
    mock_db.set_name.return_value = True

    response = client.post('/login/name', json={"name": "My Name"})
    
    assert response.status_code == 200
    assert response.get_json()['status'] == "success"

@patch('app.routes.student.SQL')
def test_student_leaderboard_apis(MockSQL, client):
    """[新增] 測試學生排行榜 (班級與校級)"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student' # [修正] 加入 identity 以通過權限檢查
        sess['account'] = 'stu@test.com'

    mock_db = MockSQL.return_value
    # 模擬取得班級 ID
    mock_db.get_student_school_and_class_by_account.return_value = (1, 101)
    
    # 測試班級排行
    mock_db.get_class_leaderboard.return_value = [{"name": "A", "score": 100}]
    resp1 = client.get('/leaderboard_class_query')
    assert resp1.status_code == 200
    assert len(resp1.get_json()['data']) == 1

    # 測試全校排行
    mock_db.get_school_leaderboard.return_value = [{"name": "B", "score": 200}]
    resp2 = client.get('/leaderboard_school_query')
    assert resp2.status_code == 200
    assert len(resp2.get_json()['data']) == 1

@patch('app.routes.student.SQL')
def test_student_equipment_get(MockSQL, client):
    """[新增] 測試取得裝備資訊"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student' # [修正] 加入 identity 以通過權限檢查
        sess['stu_id'] = 123

    mock_db = MockSQL.return_value
    mock_db.get_stu_level_score.return_value = (5, 10000)
    mock_db.get_stu_equip_now.return_value = 1
    mock_db.get_stu_equip_gain_info.return_value = [1, 0, 0, 0, 0, 0, 0]

    response = client.get('/stu/equipment/get')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['level'] == 5
    assert data['equip_cur'] == 1
    # 確認回傳的 equip_list 長度正確 (程式碼中 insert(0,1) 後長度應為 8)
    assert len(data['equip_list']) == 8

# === [補齊缺漏] 老師課程與單字管理 CRUD ===

@patch('app.routes.teacher.SQL')
def test_teacher_course_crud(MockSQL, client):
    """[新增] 測試老師課程管理 (新增、刪除)"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'

    mock_db = MockSQL.return_value
    
    # 1. 新增課程
    mock_db.insert_course.return_value = "success"
    resp_insert = client.post('/ta/course/insert', json={"insert_name": "New Course"})
    assert resp_insert.status_code == 200
    assert resp_insert.get_json()['status'] == "success"
    mock_db.insert_course.assert_called_with("New Course")

    # 2. 刪除課程
    mock_db.delete_course.return_value = "success"
    resp_del = client.post('/ta/course/delete', json={"delete_id": 99})
    assert resp_del.status_code == 200
    mock_db.delete_course.assert_called_with(99)

    # 3. 模板課程搜尋
    mock_db.get_course.return_value = []
    mock_db.get_teacher_classes.return_value = []
    resp_search = client.post('/template/course/search', json={})
    assert resp_search.status_code == 200
    assert "classes" in resp_search.get_json()

@patch('app.routes.teacher.SQL')
def test_teacher_vocab_crud(MockSQL, client):
    """[新增] 測試老師單字管理 (CRUD)"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'

    mock_db = MockSQL.return_value
    
    # 搜尋單字
    mock_db.get_course_vocab.return_value = []
    client.post('/ta/course/vocab/search', json={"course_id": 1})
    
    # 新增單字
    mock_db.insert_course_vocab.return_value = "success"
    client.post('/ta/course/vocab/insert', json={
        "course_id": 1, "insert_CHword": "貓", "insert_TWword": "Niau", "insert_TLPA": "niau"
    })
    mock_db.insert_course_vocab.assert_called()

    # 更新單字
    mock_db.update_course_vocab.return_value = "success"
    client.post('/ta/course/vocab/update', json={
        "course_id": 1, "word_id": 10, "update_CHword": "狗"
    })
    mock_db.update_course_vocab.assert_called()

    # 刪除單字
    mock_db.delete_course_vocab.return_value = "success"
    client.post('/ta/course/vocab/delete', json={"course_id": 1, "delete_id": 10})
    mock_db.delete_course_vocab.assert_called()

# === [補齊缺漏] 剩餘輔助與服務路由 ===

@patch('app.routes.teacher.SQL')
def test_teacher_leaderboard_query(MockSQL, client):
    """[補齊] 測試老師查詢班級排行榜"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'
    
    mock_db = MockSQL.return_value
    mock_db.get_class_leaderboard_by_keyword.return_value = [{"name": "Class A", "score": 100}]
    
    response = client.post('/leaderboard_ta_query', data={"input_id": "Class A"})
    assert response.status_code == 200
    # 確認有渲染出搜尋結果
    assert b"Class A" in response.data

@patch('app.routes.student.SQL')
def test_redirect_utility(MockSQL, client):
    """[補齊] 測試重導向工具路由"""
    with client.session_transaction() as sess:
        sess['pre_page_equip'] = "/stu/equipment"
        
    response = client.get('/redirect?r_type=equip')
    assert response.status_code == 200
    assert response.get_json()['url'] == "/stu/equipment"

@patch('app.routes.teacher.SQL')
def test_teacher_course_modify_timestamp(MockSQL, client):
    """[補齊] 測試老師更新課程時間戳"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'
        
    mock_db = MockSQL.return_value
    mock_db.update_modifyts.return_value = "success"
    
    response = client.post('/ta/course/update/modifyts', json={"course_id": 1})
    assert response.status_code == 200
    assert response.get_json()['status'] == "success"

@patch('app.routes.student.os.system')
@patch('app.routes.student.taiwanese_recognize')
def test_audio_services(mock_recognize, mock_system, client):
    """[補齊] 測試錄音上傳與辨識 API"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Student'
    
    # 1. 測試 /save_audio (需模擬檔案上傳)
    data = {'data': (io.BytesIO(b"dummy wav data"), 'test.wav')}
    
    # Mock open 防止寫入檔案
    with patch('builtins.open', MagicMock()):
        response = client.post('/save_audio', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert response.get_json()['suc'] == "success"
    
    # 2. 測試 /predict (需模擬檔案存在)
    with patch('app.routes.student.os.path.exists') as mock_exists:
        mock_exists.return_value = True
        mock_recognize.return_value = "Recognized Text"
        
        response_pred = client.get('/predict')
        assert response_pred.status_code == 200
        assert response_pred.get_json()['recognition'] == "Recognized Text"

@patch('app.routes.teacher.tlpa_trans')
@patch('app.routes.teacher.tts')
def test_teacher_vocab_services(mock_tts, mock_trans, client):
    """[補齊] 測試老師單字翻譯與試聽 API"""
    with client.session_transaction() as sess:
        sess['loggin'] = True
        sess['identity'] = 'Teacher'
        
    # 1. 翻譯功能
    mock_trans.return_value = "Li-ho"
    resp_trans = client.post('/ta/course/vocab/translate', json={"TW": "你好"})
    assert resp_trans.status_code == 200
    assert resp_trans.get_json()['tlpa'] == "Li-ho"
    
    # 2. 試聽 (TTS)
    mock_tts.return_value = "audio_123"
    resp_tts = client.post('/ta/course/vocab/trylisten', json={"TLPA": "Li-ho", "name_hint": "hello"})
    assert resp_tts.status_code == 200
    assert resp_tts.get_json()['name'] == "audio_123"