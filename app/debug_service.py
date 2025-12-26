import sys
import os
import traceback

print("=== 開始診斷服務引入狀態 ===")
print(f"當前工作目錄 (CWD): {os.getcwd()}")
print(f"系統路徑 (sys.path):")
for p in sys.path:
    print(f"  - {p}")

print("\n--- 測試 1: 引入 tts_service_api ---")
try:
    import tts_service_api
    print("✅ tts_service_api 引入成功")
    if hasattr(tts_service_api, 'tts'):
        print("   -> tts 函式存在")
    else:
        print("   ❌ 警告: 找不到 tts 函式")
except Exception:
    print("❌ tts_service_api 引入失敗")
    traceback.print_exc()

print("\n--- 測試 2: 引入 stt_service_api ---")
try:
    import stt_service_api
    print("✅ stt_service_api 引入成功")
except Exception:
    print("❌ stt_service_api 引入失敗")
    traceback.print_exc()

print("\n--- 測試 3: 引入 ttp_service_api ---")
try:
    import ttp_service_api
    print("✅ ttp_service_api 引入成功")
except Exception:
    print("❌ ttp_service_api 引入失敗")
    traceback.print_exc()

print("\n=== 診斷結束 ===")