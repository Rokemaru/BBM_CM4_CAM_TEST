import gpiod
import time
from datetime import datetime

# --- 設定 ---
CHIP_NAME = "gpiochip4"
INPUT_PIN = 7
# ----------------

print(f"GPIO{INPUT_PIN}の信号監視を開始します（チャタリング防止機能付き）。")
print("別のラズパイからHIGH信号が来るとメッセージを表示します。")
print("プログラムを終了するには Ctrl+C を押してください。")

line = None
previous_state = 0

try:
    with gpiod.Chip(CHIP_NAME) as chip:
        line = chip.get_line(INPUT_PIN)
        
        line.request(
            consumer="polling_receiver",
            type=gpiod.LINE_REQ_DIR_IN
        )
        
        while True:
            current_state = line.get_value()
            
            # LOWからHIGHに変わった瞬間を検知
            if current_state == 1 and previous_state == 0:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"信号を検知しました！ (LOW -> HIGH) ({timestamp})")
                
                # ▼▼▼【ここが重要】チャタリング防止の待機▼▼▼
                # 一度検知したら、0.3秒間は次の検知を行わないことで、
                # 細かい振動（チャタリング）を無視する。
                time.sleep(0.3)

            previous_state = current_state
            
            time.sleep(0.05)

except KeyboardInterrupt:
    print("\nプログラムを終了します。")
except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    print("プログラムが完全に終了しました。")