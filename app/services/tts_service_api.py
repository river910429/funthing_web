

# # tts_service_api.py
# # !/usr/bin/env python
# # _*_coding:utf-8_*_

# import os, socket, struct, time, hashlib, unicodedata, re, base64
# from dotenv import load_dotenv
# load_dotenv()

# # —— 你現有的工具 / 微服務裝飾器 ——
# from keydnn.utilities import KeyResponse
# from mi2s_microservices import mi2s_microservice  # 依你實際路徑

# AUDIO_DIR = os.path.join('static', 'audio')
# os.makedirs(AUDIO_DIR, exist_ok=True)

# # ========= 微服務客戶端（兩個）：中文→台羅、台羅→語音 =========
# # 1) 「中文/漢字 → 台羅（TLPA）」：把中文字串轉成教育部台羅（無數字、含變調）
# # 2) 「台羅（TLPA）→ 語音（WAV, base64）」：把 TLPA 丟給 TTS 微服務拿回 base64
# #    * 請把 api_token 換成你實際的『合成』服務 token
# @mi2s_microservice(api_token=os.environ("MICROSERVICES_TTS_TW"))
# def tlpa_tts_service(response_json:dict):
#     return response_json["message"]["answer"]

# # ========= 小工具 =========
# def _looks_like_chinese(text: str) -> bool:
#     return any('\u4e00' <= ch <= '\u9fff' for ch in text)

# def _write_atomic(path: str, data_bytes: bytes):
#     tmp = path + ".tmp"
#     with open(tmp, 'wb') as f:
#         f.write(data_bytes)
#     os.replace(tmp, path)

# def _looks_like_wav(filepath: str) -> bool:
#     try:
#         with open(filepath, 'rb') as f:
#             head = f.read(12)
#         return len(head) >= 12 and head[0:4] == b'RIFF' and head[8:12] == b'WAVE'
#     except Exception:
#         return False

# # ========= 舊的 socket 傳輸（當微服務不可用時的後備） =========
# def askForService(host, port, token, data, model, save_name="", mode="taiwanese_sandhi"):
#     if not save_name:
#         save_name = time.strftime("%Y%m%d%H%M%S", time.localtime())
#     msg = f"{token}@@@{data}@@@{model}@@@{mode}".encode("utf-8")
#     packet = struct.pack(">I", len(msg)) + msg

#     # 收流 → bytes
#     chunks = bytearray()
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         sock.connect((host, port))
#         sock.sendall(packet)
#         while True:
#             buf = sock.recv(8192)
#             if not buf:
#                 break
#             chunks.extend(buf)
#     finally:
#         sock.close()

#     out_path = os.path.join(AUDIO_DIR, save_name + ".wav")
#     _write_atomic(out_path, bytes(chunks))
#     return save_name

# # ========= 封裝：合成主流程（優先微服務；失敗退回 socket） =========
# def tts(data: str, save_name: str = "", model: str = "M12_sandhi"):
#     """
#     data:   中文/漢字 或 教育部台羅（無數字）
#     save_name: 要儲存的檔名（不含副檔名）；可用台語漢字
#     model:  聲線（依你的服務實際名稱，預設用 M12_sandhi）
#     """
#     if not save_name:
#         save_name = time.strftime("%Y%m%d%H%M%S", time.localtime())
#     out_path = os.path.join(AUDIO_DIR, save_name + ".wav")

#     # 2) 走「台羅→語音」微服務
#     used_microservice = False
#     try:
#         # 依你的服務要求帶入欄位（例如 text / tlpa / speaker / model ...）
#         b64 = tlpa_tts_service(tlpa=data, model=model)
#         if isinstance(b64, str) and b64.strip():
#             pcm = base64.b64decode(b64.strip())
#             _write_atomic(out_path, pcm)
#             used_microservice = True
#     except Exception:
#         used_microservice = False

#     # 3) 如果微服務失敗，就退回舊的 socket（保險起見）
#     if not used_microservice or not _looks_like_wav(out_path):
#         # 選 port：中文入口 10012 要用中文模式；台羅入口 10010 用變調模式
#         if _looks_like_chinese(data):
#             host, port, mode = "140.116.245.157", 10012, "hanji"  # ← 若你的 server 期望別的字串，請改
#         else:
#             host, port, mode = "140.116.245.157", 10010, "taiwanese_sandhi"
#         token = os.getenv("TTS_SOCKET_TOKEN", "mi2stts")

#         askForService(host, port, token, tlpa, model, save_name, mode=mode)

#         # 若仍不是 WAV，輸出錯誤頭幫你 debug
#         if not _looks_like_wav(out_path):
#             try:
#                 with open(out_path, 'rb') as f:
#                     head = f.read(512)
#                 preview = ""
#                 try:
#                     preview = head.decode('utf-8', errors='replace')
#                 except Exception:
#                     preview = head.hex()
#                 with open(out_path + ".err.txt", "w", encoding="utf-8") as ef:
#                     ef.write(preview)
#             except Exception:
#                 pass
#             raise RuntimeError(f"TTS response is not a WAV file. See {out_path}.err.txt")

#     return save_name

# if __name__ == "__main__":
#     # 範例：
#     # 1) 中文輸入：會先走『漢字→台羅』微服務，再走『台羅→語音』微服務
#     tts("你好", save_name="你好", model="M12_sandhi")
#     # 2) 直接 TLPA：會直接走『台羅→語音』微服務
#     # tts("lí-hó", save_name="你好", model="M12_sandhi")
# tts_service_api.py
# tts_service_api.py
# !/usr/bin/env python
# _*_coding:utf-8_*_

import os
import socket
import json
import base64
import re
import io
import struct
from flask import current_app

# ======= 9993 微服務設定 =======
SERVER, PORT = "140.116.245.147", 9993
END_OF_TRANSMISSION = "EOT"
SPEAKER = "1"          # 語者 ID
TOKEN = "mi2stts"      # token
PIPELINE_CODE = "10012"  # 協定碼
MODE = "tw_tl"         # 台羅輸入模式
SPEED = "0.7"          # 語速


# ======= 工具 =======
def get_audio_dir() -> str:
    audio_dir = os.path.join(current_app.root_path, "static", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    return audio_dir

def write_atomic(path: str, data: bytes):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)

def ensure_wav_bytes(raw: bytes, sr: int = 16000, channels: int = 1, sampwidth: int = 2) -> bytes:
    """如果 raw 不是 RIFF/WAVE，就當成 PCM s16le 包成 WAV。"""
    if len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WAVE":
        return raw
    byte_rate = sr * channels * sampwidth
    block_align = channels * sampwidth
    datasize = len(raw)
    riffsize = 36 + datasize
    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", riffsize))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))            # fmt chunk size
    buf.write(struct.pack("<H", 1))             # PCM
    buf.write(struct.pack("<H", channels))
    buf.write(struct.pack("<I", sr))
    buf.write(struct.pack("<I", byte_rate))
    buf.write(struct.pack("<H", block_align))
    buf.write(struct.pack("<H", sampwidth * 8)) # bits per sample
    buf.write(b"data")
    buf.write(struct.pack("<I", datasize))
    buf.write(raw)
    return buf.getvalue()


# ======= 呼叫 9993 微服務 =======
def synthesize_tailou_speech(tlpa: str, speaker: str = SPEAKER, speed: str = SPEED) -> bytes:
    """把 TLPA 丟進微服務，回音訊 bytes"""
    if not tlpa.strip():
        raise ValueError("TLPA must not be empty.")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER, PORT))
        payload = f"{PIPELINE_CODE}@@@{TOKEN}@@@{MODE}@@@{speaker}@@@{tlpa}@@@{speed}"
        sock.sendall(payload.encode("utf-8") + END_OF_TRANSMISSION.encode("utf-8"))

        resp = bytearray()
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            resp.extend(chunk)
    finally:
        sock.close()

    # 嘗試解讀為 JSON
    try:
        obj = json.loads(resp.decode("utf-8", errors="strict"))
        if not obj.get("status", False):
            raise RuntimeError(f"TTS microservice error: {obj}")
        b64 = obj.get("bytes", "")
        b64 = re.sub(r"^data:audio/[^;]+;base64,", "", b64.strip(), flags=re.I)
        return base64.b64decode(b64)
    except Exception:
        # 若不是 JSON，當作原始音訊
        return bytes(resp)


# ======= 對外主函式 =======
def tts(tlpa: str, save_name: str) -> str:
    """
    tlpa: 台羅拼音字串
    save_name: 希望的檔名（不含副檔名）
    回傳：實際存檔名（不含副檔名）
    """
    audio_dir = get_audio_dir()
    out_path = os.path.join(audio_dir, f"{save_name}.wav")

    # 已有檔案就直接用，不再新增
    if os.path.exists(out_path):
        return save_name

    raw_audio = synthesize_tailou_speech(tlpa, speaker=SPEAKER, speed=SPEED)
    wav_bytes = ensure_wav_bytes(raw_audio)
    write_atomic(out_path, wav_bytes)

    return save_name


if __name__ == "__main__":
    print(tts("lí-hó", save_name="你好"))
