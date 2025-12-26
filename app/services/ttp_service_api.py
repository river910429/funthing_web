# # !/usr/bin/env python
# # _*_coding:utf-8_*_

# # 客戶端 ，用來呼叫service_Server.py
# import socket
# import sys
# import struct


# ### Don't touch
# def askForService(token, data):
# 	# HOST, PORT 記得修改
# 	global HOST
# 	global PORT
# 	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 	received = ""
# 	try:
# 		sock.connect((HOST, PORT))
# 		msg = bytes(token + "@@@" + data, "utf-8")
# 		msg = struct.pack(">I", len(msg)) + msg
# 		sock.sendall(msg)
# 		received = str(sock.recv(8192), "utf-8")
# 	finally:
# 		sock.close()
# 	return received


# ### Don't touch

# def process(data):
#     token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ3bW1rcy5jc2llLmVkdS50dyIsInNlcnZpY2VfaWQiOiIxNyIsIm5iZiI6MTU4MTY3MTM0Niwic2NvcGVzIjoiMCIsInVzZXJfaWQiOiI4NSIsImlzcyI6IkpXVCIsInZlciI6MC4xLCJpYXQiOjE1ODE2NzEzNDYsInN1YiI6IiIsImlkIjoyNjQsImV4cCI6MTczOTM1MTM0Nn0.SLC2x7zekyuBu9MVPeGUTCeLyYY_z-d8r8iPgE_cGpO7f8SIEnkv0XqGxw7iJPj8BJikVqr0uHjTXzkdxyv8XhLpHaeKFFlQjmiNtZ0BgmDkuiFOVmLYZtsML4qWCbZmXd7VgBuMPtZzLL0LuPoRjSPEe4bV8Z6DUsyXntPZnjc"
# 	# 可在此做預處理
	
# 	# 送出
#     result = askForService(token, data)
# 	# 可在此做後處理
	
#     return result


# global HOST
# global PORT
# HOST, PORT = "140.116.245.149", 27005
# if __name__ == "__main__":
# 	data = "烘碗機"
# 	# for i in range(1): print("Client : ", process(token, data))
# 	print(process(data))

# 不要用舊的，用新的
# ttp_service_api.py
# !/usr/bin/env python
# _*_coding:utf-8_*_

import requests

# API 設定
CONVERT_API_URL = "https://dev.taigiedu.com/backend/convert_taibun"

def process(sentence: str) -> str:
    """
    呼叫外部 API 進行台文轉換
    參數: sentence (中文/漢字)
    回傳: 台羅拼音
    """
    if not sentence:
        return ""

    # 準備請求資料
    payload = {
        "taibun_mode": "tbn2tl",  # 依照您的要求：漢字轉台羅
        "taibun_data": sentence
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # 發送 POST 請求 (設定 10 秒超時，避免卡住)
        response = requests.post(CONVERT_API_URL, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            # 根據您的範例，API 回傳的 text 就是轉換後的結果
            return response.text
        else:
            print(f"❌ [Convert API Error] Code: {response.status_code}, Msg: {response.text}")
            # 如果 API 失敗，回傳原文，避免網頁報錯 (500 Error)
            return sentence

    except Exception as e:
        print(f"⚠️ [Convert API Exception] {str(e)}")
        # 發生連線錯誤時，回傳原文
        return sentence

# 測試用：直接執行這個檔案可以看到結果
if __name__ == "__main__":
    test_str = "你好，我是台灣人"
    print(f"原文: {test_str}")
    print(f"結果: {process(test_str)}")