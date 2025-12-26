# run.py (放在專案根目錄)
from app import create_app
# 根據環境變數載入不同設定，預設使用 Development
from app.config import DevelopmentConfig

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    # SSL 相關設定建議透過 config 或環境變數處理，不要寫死
    # 這裡為了範例保留你的參數
    app.run(
        host="0.0.0.0", 
        port=8889, 
        debug=True, 
        threaded=True, 
        use_reloader=False, 
        ssl_context='adhoc' # 或 ('certs/server.crt', 'certs/server.key')
    )