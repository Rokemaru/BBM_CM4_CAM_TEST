import gpiod
import time
from datetime import datetime

# --- 設定 ---
CHIP_NAME = "gpiochip4"
INPUT_PIN = 7
# ----------------

print(f"GPIO{INPUT_PIN}の信号監視を開始します（ポーリング方式）。")
print("別のラズパイからHIGH信号が来るとメッセージを表示します。")
print("プログラムを終了するには Ctrl+C を押してください。")

line = None
# 信号の前の状態を覚えておくための変数（最初はLOW=0としておく）
previous_state = 0

try:
    with gpiod.Chip(CHIP_NAME) as chip:
        line = chip.get_line(INPUT_PIN)
        
        # ピンを単純な「入力モード」として要求する
        line.request(
            consumer="polling_receiver",
            type=gpiod.LINE_REQ_DIR_IN
        )
        
        while True:
            # 現在のピンの状態を読み取る (0=LOW, 1=HIGH)
            current_state = line.get_value()
            
            # もし、前の状態がLOW(0)で、今の状態がHIGH(1)に変わった瞬間なら
            if current_state == 1 and previous_state == 0:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"信号を検知しました！ (LOW -> HIGH) ({timestamp})")

            # 現在の状態を「前の状態」として保存する
            previous_state = current_state
            
            # CPUを使いすぎないように、ごく短い時間だけ待つ
            time.sleep(0.05)

except KeyboardInterrupt:
    print("\nプログラムを終了します。")
except Exception as e:
    print(f"エラーが発生しました: {e}")

finally:
    print("プログラムが完全に終了しました。")