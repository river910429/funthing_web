# app/config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # 設定上傳或暫存路徑
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TEMP_FOLDER = os.path.join(os.getcwd(), "temp")

class DevelopmentConfig(Config):
    DEBUG = True
    SSL_CONTEXT = 'adhoc' # 或指定具體路徑

class ProductionConfig(Config):
    DEBUG = False
    # 在這裡設定正式環境的 SSL路徑

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # 如果有資料庫，建議使用記憶體資料庫或測試專用庫
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 
    WTF_CSRF_ENABLED = False  # 測試時通常關閉 CSRF 保護以簡化測試