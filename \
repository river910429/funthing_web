
FROM python:3.9-slim

# 取消 Python 緩衝輸出，方便即時看 log
ENV PYTHONUNBUFFERED=1

# 建立工作目錄
WORKDIR /usr/src/app

# 先複製 requirements 並安裝
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個 app 資料夾
COPY app/ ./app/

# 切到 app 目錄
WORKDIR /usr/src/app/app

# 暴露 Flask 預設埠
EXPOSE 5000

# 啟動指令：用 Gunicorn 4 worker 執行 flask_app.py 裡的 app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "flask_app:app"]


