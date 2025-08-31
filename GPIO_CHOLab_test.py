import gpiod
import time
from datetime import datetime

# --- 設定 ---
CHIP_NAME = "gpiochip4" 
GPIO_TRIGGER_PIN = 7
# ----------------

def signal_detected():
    """信号を検知したら、現在時刻と共にメッセージを表示する"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"信号を検知しました！ ({timestamp})")

# --- メインの処理 ---
try:
    with gpiod.Chip(CHIP_NAME) as chip:
        line = chip.get_line(GPIO_TRIGGER_PIN)
        
        # ▼▼▼▼▼【ここを旧バージョン用に修正しました】▼▼▼▼▼
        # flagsの指定を削除し、古い定数名を使用
        line.request(
            consumer="print_trigger",
            type=gpiod.LINE_REQ_EV_RISING_EDGE
        )
        # ▲▲▲▲▲【ここまで】▲▲▲▲▲
        
        print(f"GPIO{GPIO_TRIGGER_PIN} での信号待機を開始しました。")
        print("High信号が入力されるとメッセージを表示します。(Ctrl+Cで終了)")
        
        while True:
            if line.event_wait(sec=None):
                event = line.event_read()
                signal_detected()
                time.sleep(0.5)

except KeyboardInterrupt:
    print("\nプログラムを終了します。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
    