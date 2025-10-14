import threading
import subprocess
import time
import sys
import os
import pywebview

# Streamlit 應用程式的檔案名稱
STREAMLIT_APP = "app.py"
# Streamlit 服務器將運行的本地 URL
URL = 'http://127.0.0.1:8501'


# 1. 定義啟動 Streamlit 的函數
def start_streamlit():
    """在一個新的線程中啟動 Streamlit 服務器"""
    try:
        print("Starting Streamlit server...")

        # 這是 PyInstaller 打包後的環境
        if getattr(sys, 'frozen', False):
            # 在打包環境中，使用內部的 Python 執行 streamlit 模組
            # 注意: 這裡假設 'app.py' 會被 --add-data 參數正確包含
            cmd = [sys.executable, "-m", "streamlit", "run", STREAMLIT_APP, "--server.port", "8501",
                   "--server.headless", "true"]
        else:
            # 開發環境，直接調用系統的 streamlit
            cmd = ["streamlit", "run", STREAMLIT_APP, "--server.port", "8501", "--server.headless", "true"]

        # 使用 subprocess.Popen 啟動服務器，不阻塞主線程
        # 我們將進程存起來，以便關閉應用程式時停止它
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 將進程ID存入全局，方便後面關閉視窗時停止服務
        global streamlit_process
        streamlit_process = p

    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        pywebview.platforms.winforms.api.terminate_window()  # 發生錯誤時關閉視窗


# 2. 定義關閉應用程式時的處理函數
def on_closed():
    """當 Pywebview 視窗關閉時，停止 Streamlit 服務器"""
    global streamlit_process
    print("Pywebview window closed. Stopping Streamlit...")

    if 'streamlit_process' in globals() and streamlit_process:
        # 嘗試終止 Streamlit 進程
        if sys.platform == "win32":
            # Windows: 終止整個進程樹 (因為 streamlit run 可能創建多個進程)
            try:
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(streamlit_process.pid)], check=True)
            except:
                pass  # 忽略錯誤
        else:
            streamlit_process.terminate()
            streamlit_process.wait()

    print("Application fully closed.")


# 3. 主執行邏輯
if __name__ == '__main__':
    # 設置全域變數
    streamlit_process = None

    # 啟動 Streamlit 服務器在後台線程中
    t = threading.Thread(target=start_streamlit, daemon=True)
    t.start()

    # 等待服務器啟動 (重要步驟，確保瀏覽器可以連上)
    time.sleep(5)

    # 啟動 Pywebview 視窗
    # title: 視窗標題
    # url: 要嵌入的網址 (Streamlit 的本地地址)
    # width/height: 視窗大小
    # fullscreen: 是否全螢幕
    # minimized: 是否最小化啟動
    # confirm_close: 關閉視窗時彈出確認對話框
    pywebview.create_window(
        '3Q 全球贏家 - 專業回測',
        url=URL,
        width=1200,
        height=800
    )

    # 啟動 Pywebview GUI 主循環
    pywebview.start(
        on_closed=on_closed,  # 在視窗關閉時執行我們定義的清理函數
        http_server=False  # 不需要 pywebview 自己的 http server
    )