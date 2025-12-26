# app/__init__.py
from flask import Flask, session, request, redirect, url_for
import os
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 確保 temp 資料夾存在
    if not os.path.exists(app.config['TEMP_FOLDER']):
        os.makedirs(app.config['TEMP_FOLDER'])

    # 註冊 Blueprints
    from app.routes.auth import bp_auth
    from app.routes.teacher import bp_teacher
    from app.routes.student import bp_student
    from app.routes.main import bp_main # [新建] 處理 index 和 taigi_game

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_teacher)
    app.register_blueprint(bp_student)
    app.register_blueprint(bp_main)

    # 權限檢查 Hook (建議可以抽離成獨立的 middleware 或 decorator，但暫時放在這也行)
    init_auth_check(app)

    return app

def init_auth_check(app):
    @app.before_request
    def before_request():
        whitelist = [
            "/", "/branch", "/login", "/register", "/verifying", "/api/schools",
            "/static", "/favicon.ico", "/taigi_game"
        ]
        # 優化判斷邏輯：檢查是否完全匹配或是靜態資源
        path = request.path
        
        # 如果是 static 資源，通常不需要跑 python 迴圈檢查，web server (nginx) 會擋，
        # 但如果是開發環境，可以用簡單邏輯判斷
        if path.startswith("/static"):
            return

        is_whitelisted = any(path.startswith(w) for w in whitelist)

        # 這裡原本的邏輯
        if not is_whitelisted and session.get('account') is None:
            # 這裡要注意，避免重導向迴圈，最好確保 /branch 在白名單且 redirect 正確
            return redirect("/branch")