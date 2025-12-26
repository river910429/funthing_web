# tests/conftest.py
import pytest
from app import create_app
from app.config import TestingConfig

@pytest.fixture
def app():
    """建立一個測試用的 Flask App 實例"""
    app = create_app(TestingConfig)
    
    # 如果未來引入 SQLAlchemy, 可在此 create_all()
    
    yield app
    
    # 清理工作


@pytest.fixture
def client(app):
    """建立一個測試用的 Client，模擬瀏覽器行為"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """如果你有寫 flask command CLI，用這個測試"""
    return app.test_cli_runner()