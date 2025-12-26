# hts_service_api.py
# !/usr/bin/env python
# _*_coding:utf-8_*_

import os
import requests
import base64
from flask import current_app

# API 設定
TTS_API_URL = "https://dev.taigiedu.com/backend/synthesize_speech"

def get_audio_dir() -> str:
    """取得存放音檔的資料夾路徑 (static/audio)"""
    # 確保在 Flask 環境下能找到正確路徑
    if current_app:
        audio_dir = os.path.join(current_app.root_path, "static", "audio")
    else:
        # 如果是在單獨執行的腳本中
        audio_dir = os.path.join("static", "audio")
        
    os.makedirs(audio_dir, exist_ok=True)
    return audio_dir

def tts(data: str, save_name: str, model: str = "") -> str:
    """
    呼叫外部 API 進行語音合成
    
    Args:
        data (str): 要合成的文字 (台羅或漢字)
        save_name (str): 存檔檔名 (不含副檔名)
        model (str): (保留參數，為了相容舊程式碼介面，這裡用不到)
        
    Returns:
        str: 成功存檔的檔名 (save_name)
    """
    
    # 1. 準備檔案路徑
    audio_dir = get_audio_dir()
    out_path = os.path.join(audio_dir, f"{save_name}.wav")

    # 2. 檢查是否已經有這個檔案 (快取機制)
    # 如果檔案存在且大小大於 0，就直接回傳，省流量、省時間
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f"[TTS] File exists (Cache hit): {out_path}")
        return save_name

    print(f"[TTS] Requesting API for: {data}")

    # 3. 準備請求資料
    payload = {
        "tts_lang": "tb",  # 固定參數
        "tts_data": data   # 使用者傳入的文字
    }

    try:
        # 4. 發送 POST 請求
        response = requests.post(TTS_API_URL, json=payload, timeout=30)

        if response.status_code == 200:
            # 5. 處理回傳資料
            # 根據您的說明，API 回傳的 response.text 直接就是 base64 字串
            audio_base64 = response.text
            
            if not audio_base64:
                raise ValueError("API returned empty content")

            # 解碼 Base64
            audio_data = base64.b64decode(audio_base64)

            # 6. 寫入檔案
            with open(out_path, "wb") as audio_file:
                audio_file.write(audio_data)
            
            print(f"✅ [TTS] Saved to {out_path}")
            return save_name
        else:
            error_msg = f"❌ [TTS] API Error: Code {response.status_code}, Message: {response.text}"
            print(error_msg)
            raise RuntimeError(error_msg)

    except Exception as e:
        print(f"⚠️ [TTS] Exception: {str(e)}")
        # 這裡拋出錯誤，讓呼叫端知道失敗了
        raise e

# 讓您可以單獨執行這個檔案來測試
if __name__ == "__main__":
    # 模擬 Flask app context (為了測試 get_audio_dir)
    # 實際執行時請直接呼叫 tts()
    try:
        print("Testing TTS...")
        filename = tts("西瓜", "test_output2")
        print(f"Test success! File saved as: {filename}.wav")
    except Exception as err:
        print(f"Test failed: {err}")