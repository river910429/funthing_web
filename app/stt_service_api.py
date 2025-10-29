# # -*- coding: utf-8 -*
# import re, json
# import socket
# import struct

# def askForService(token:str, port:int, lang:str, model:str, data:bytes) -> dict:
#     '''
#     DO NOT MODIFY THIS PART
#     '''
#     HOST = "140.116.245.157"
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         sock.connect((HOST, port))
#         msg_dict = {"token": token, "source": "P", "lang": lang, "model": model,"data_len": len(data)}
#         msg = json.dumps(msg_dict).encode('utf-8')
#         msg = struct.pack(">I", len(msg)) + msg  # add msg len
#         sock.sendall(msg)  # send message to server
#         sock.sendall(data)  # send audio data to server

#         # receive result
#         received_all = ''
#         while 1:
#             received = str(sock.recv(1024), "utf-8")
#             if len(received) == 0:
#                 sock.close()
#                 break
#             received_all += received
#     finally:
#         sock.close()

#     # json expecting property name enclosed in double quotes
#     return json.loads(received_all.replace("'", '"'))


# def recognize_request(file_pth: str):
#     '''
#     Mi2S ASR API
#     lang: 
#         mandarin(中文), taiwanese(台語)
#     '''
#     token = "@@@funthing@@@"
#     port = 2802
#     audio = open(file_pth, 'rb').read()  # read wav in binary mode
#     lang = "taiwanese"
#     model = "funthing2"
#     result = askForService(token, port, lang, model, audio)
#     print(result["msg"])
#     return result

# # def taiwanese_recognize(filepath: str):
# #     try:
# #         result = recognize_request(filepath)["rec_result"]
# #         result = [re.sub("[A-Za-z0-9_<>* ]", "", r) for r in result]
# #         result = [r for r in result if len(r)]
# #         return result
# #     except:
# #         return ["ERROR"]
# def taiwanese_recognize(filepath: str):
#     try:
#         result_dict = recognize_request(filepath)
#         print("ASR 原始結果:", result_dict)
#         result = result_dict.get("rec_result", [])
#         # 檢查是不是list
#         if not isinstance(result, list):
#             print("錯誤：ASR回傳 rec_result 不是 list")
#             return ["ERROR"]
#         result = [re.sub("[A-Za-z0-9_<>* ]", "", str(r)) for r in result]
#         result = [r for r in result if len(r)]
#         return result if result else ["ERROR"]
#     except Exception as e:
#         print("辨識例外：", e)
#         return ["ERROR"]

    
# if __name__ == "__main__":
#     result = taiwanese_recognize("temp/20250626_143914.wav")
#     print(result)


# # -*- coding: utf-8 -*-
# import re
# import json
# import base64
# import requests

# def askForService(token:str, host:str, port:int, lang:str, model:str, data:bytes) -> dict:
#     '''
#     改為 HTTP POST 版本
#     '''
#     url = f"http://{host}:{port}/asr"
#     audio_data = base64.b64encode(data).decode("utf-8")

#     # 語言與 service_id 可根據你的 API 文檔調整
#     lang_map = {
#         "mandarin": "華語",
#         "taiwanese": "台語",
#         "bilingual": "華台雙語",
#     }
#     service_id_map = {
#         "華語": "A017",
#         "台語": "A035",
#         "華台雙語": "A019",
#     }

#     api_lang = lang_map.get(lang, lang)
#     service_id = service_id_map.get(api_lang, "A035")  # 預設台語

#     payload = {
#         "token": token,
#         "audio_data": audio_data,
#         "audio_format": "wav",
#         "service_id": service_id,
#         "segment": False,
#         "correction": False,
#         "streaming_id": None,
#     }

#     resp = requests.post(url, json=payload)
#     try:
#         return resp.json()
#     except Exception as e:
#         print("HTTP回傳非JSON或解析錯誤", e, resp.text)
#         return {"rec_result": ["ERROR"], "msg": "HTTP/JSON Error"}

# def recognize_request(file_pth: str):
#     '''
#     HTTP POST 取代 socket
#     '''
#     token = "btRkfZr5Ndy2tkpnRfZ3b9ER9ndEC6rxYEg5Vu8XCCuK85KRDKw9cFhcYQ3VdXBQ"
#     host  = "140.116.245.149"
#     port  = 2802
#     lang  = "taiwanese"
#     model = "funthing2"  # 其實這邊沒用到，可保留
#     with open(file_pth, 'rb') as f:
#         audio = f.read()
#     result = askForService(token, host, port, lang, model, audio)
#     print(result.get("msg", ""))
#     return result

# def taiwanese_recognize(filepath: str):
#     try:
#         result_dict = recognize_request(filepath)
#         print("ASR 原始結果:", result_dict)
#         result = result_dict.get("words_list", [])  # HTTP 版本結果 key 不同
#         if not isinstance(result, list):
#             print("錯誤：ASR回傳 words_list 不是 list")
#             return ["ERROR"]
#         result = [re.sub("[A-Za-z0-9_<>* ]", "", str(r)) for r in result]
#         result = [r for r in result if len(r)]
#         return result if result else ["ERROR"]
#     except Exception as e:
#         print("辨識例外：", e)
#         return ["ERROR"]

# if __name__ == "__main__":
#     result = taiwanese_recognize("temp/20250626_143914.wav")
#     print(result)

# import requests

# API_URL = "https://microservices.ilovetogether.com/infer"

# TOKEN = "acab9db0e6f8198d6a32849e94e10f2b8c4d83b4876fc977b066bef2b9e527ef"

# def recognize_taiwanese_stt(filepath: str):
#     headers = {
#         "api-key": TOKEN,
#         "Authorization": f"Bearer {TOKEN}"
#     }

#     with open(filepath, "rb") as f:
#         files = {
#             "file": f   # 參數名通常為 file, audio, 或 audio_file。若有API文件請提供正確名稱
#         }
#         response = requests.post(API_URL, headers=headers, files=files)
    
#     try:
#         result = response.json()
#         print("辨識回應:", result)
#         # 根據API實際回傳格式取值，例如 "text"、"result"、"words_list"
#         return result.get("text", "辨識失敗或API回傳格式不符")
#     except Exception as e:
#         print("API回傳非JSON或解析錯誤", e, response.text)
#         return "ERROR"

# if __name__ == "__main__":
#     wav_path = "temp/20250626_143914.wav"
#     result = recognize_taiwanese_stt(wav_path)
#     print("辨識結果:", result)
from dotenv import load_dotenv
load_dotenv()


import sounddevice as sd
from scipy.io.wavfile import write
import base64
import requests

# 使用積木的轉換
import os
from keydnn.utilities import KeyResponse
from mi2s_microservices import mi2s_microservice  # 根據實際路徑修改

# 設定 token，可存在環境變數或直接指定
MICROSERVICE_API_TOKEN = os.getenv("MICROSERVICES_TAIBUN_TBN2ZH", "3dc1168efeb36aae3c5ac18f02c6fbc661f0a89ece10cb5f3134fe5f1c27b61d")

@mi2s_microservice(api_token=MICROSERVICE_API_TOKEN)
def call_taibun_converter(json_response):
    print("🧾 微服務回傳 JSON：", json_response)
    try:
        return json_response["message"]["answer"]
    except Exception:
        return "（無法取得轉換內容）"



def record_audio(filename="audio.wav", duration=5, samplerate=16000):
    print(f"開始錄音 {duration} 秒，請開始說話 ...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    write(filename, samplerate, audio)
    print(f"錄音完成，已存為 {filename}")

def taiwanese_recognize(file_path):
    url = 'http://140.116.245.149:5002/proxy'
    token = '2025@asr@tai'
    lang = 'TA and ZH Medical V1'

    with open(file_path, 'rb') as file:
        raw_audio = file.read()
    audio_data = base64.b64encode(raw_audio).decode()

    data = {
        'lang': lang,
        'token': token,
        'audio': audio_data
    }

    response = requests.post(url, data=data)
    try:
        result = response.json()
    except Exception:
        print("API 回應非 JSON 格式")
        print(response.text)
        return None

    if response.status_code == 200:
        sentence = result.get('sentence')
        print(f"辨識結果: {sentence}")

        # 呼叫第二階段：Microservice Taibun API
        taibun_result = call_taibun_converter(sentence)
        print(vars(taibun_result))
        if taibun_result._KeyResponse__status:
            print(f"台文轉換結果: {taibun_result._KeyResponse__message}")
            return taibun_result._KeyResponse__message
        else:
            print(f"台文轉換失敗: {taibun_result._KeyResponse__message}")
            return sentence


    else:
        print(result)
        print(f"錯誤信息: {result.get('error')}")
        return None

# def taiwanese_recognize(file_path):
#     url = 'http://140.116.245.149:5002/proxy'
#     token = '2025@asr@oops'
#     lang = 'TA and ZH Medical V1'

#     with open(file_path, 'rb') as file:
#         raw_audio = file.read()
#     audio_data = base64.b64encode(raw_audio).decode()

#     data = {
#         'lang': lang,
#         'token': token,
#         'audio': audio_data
#     }
#     response = requests.post(url, data=data)
#     try:
#         result = response.json()
#     except Exception:
#         print("API 回應非 JSON 格式")
#         print(response.text)
#         return None  # 加明確回傳

#     if response.status_code == 200:
#         sentence = result.get('sentence')
#         print(f"辨識結果: {sentence}")
#         return sentence  # <--- **這行就是最重要的補上**
#     else:
#         print(result)
#         print(f"錯誤信息: {result.get('error')}")
#         return None  # 失敗時也要 return


if __name__ == "__main__":
    # # 1. 錄音（如已有音檔可註解掉）
    # duration = 5
    # filename = "audio.wav"
    # record_audio(filename=filename, duration=duration, samplerate=16000)

    # # 2. 語音辨識
    # recognize_audio_proxy_api(filename)

    # 你也可以直接寫現有檔名
    # recognize_audio_proxy_api('你的檔名.wav')
    wav_path = "temp/20250725_132044.wav"
    result = taiwanese_recognize(wav_path)
    print("辨識結果:", result)

# if __name__ == "__main__":
#     print("✅ MICROSERVICES_HUB_URI:", os.getenv("MICROSERVICES_HUB_URI"))
#     print("✅ MICROSERVICES_TAIBUN_TBN2ZH:", MICROSERVICE_API_TOKEN)

#     sentence = "你好朋友"
#     test_result = call_taibun_converter(sentence)
#     print("轉換結果:", vars(test_result))