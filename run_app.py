# run_app.py
import subprocess
import sys
import os

# 確保應用程式名稱是你的主檔案名
APP_FILE = "app.py"

# 找到 Streamlit 執行檔的路徑
if getattr(sys, 'frozen', False):
    # 如果是 PyInstaller 打包後的環境
    # 這裡假設你的應用程式檔案 app.py 被包含在同一個目錄
    # 實際的 streamlit 執行檔路徑在 _MEIXXXXX/streamlit/__main__.py
    # 但我們不需要直接調用，只需要調用打包好的 Python 環境執行 streamlit

    # 由於打包後的環境比較複雜，我們使用 subprocess 調用打包在內部的 Python
    try:
        # 嘗試使用打包環境中的 python 執行 streamlit
        # 注意：在 --onefile 模式下，路徑問題非常複雜

        # 最簡化且最可能成功的方法是直接執行
        # "streamlit run app.py"
        # 但由於 app.py 可能不在根目錄，我們需要找到它

        # 為了簡化，我們直接調用 Streamlit 模組：
        command = [sys.executable, "-m", "streamlit", "run", APP_FILE]

        # 運行 Streamlit，並阻塞直到 Streamlit 服務結束
        print(f"Starting Streamlit server with command: {' '.join(command)}")
        subprocess.run(command)

    except Exception as e:
        print(f"Error launching Streamlit: {e}")
        input("Press Enter to close...") # 讓用戶看到錯誤訊息
else:
    # 非打包環境，直接用系統的 streamlit 執行
    os.system(f"streamlit run {APP_FILE}")