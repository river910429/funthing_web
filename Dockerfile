FROM python:3.10-slim-bullseye

# 取消 Python 緩衝輸出
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y openssl ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 2. 建立 SSL 憑證 (自行簽署，僅供測試/內部使用)
RUN openssl req -x509 -newkey rsa:4096 -nodes \
    -out /cert.pem \
    -keyout /key.pem \
    -days 365 \
    -subj "/CN=localhost"

# 建立工作目錄
WORKDIR /usr/src/app

# 複製 requirements 並安裝
COPY requirements.txt ./

# [關鍵修正 1] 移除原本強制安裝 Werkzeug<3.0.0 的指令
# 現在完全依賴 requirements.txt 內的版本 (Flask==3.0.3, Werkzeug==3.0.3)
RUN pip install --upgrade pip --progress-bar off && \
    pip install --no-cache-dir --progress-bar off -r requirements.txt

# 複製整個專案
COPY . .

# 設定工作目錄
WORKDIR /usr/src/app

# [新增] 強制將工作目錄加入 PYTHONPATH，避免 Python 找不到模組
ENV PYTHONPATH=/usr/src/app

# 暴露埠
EXPOSE 8889

# 3. 啟動指令：
# [關鍵修正 2] 將 flask_app:app 改為 run:app
# [新增] ls -R 用於檢查目錄結構，確認 app/ 資料夾是否存在
CMD ["sh", "-c", "echo '--- Directory Structure Check ---' && ls -R && echo '-----------------------------' && gunicorn -w 4 -b 0.0.0.0:8889 --certfile=/cert.pem --keyfile=/key.pem run:app"]