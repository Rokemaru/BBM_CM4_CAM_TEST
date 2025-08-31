import gpiod
import time

# --- 設定 ---
CHIP_NAME = "gpiochip4" # 古いモデルのラズパイでは "gpiochip0"
OUTPUT_PIN = 4
# ----------------

print(f"GPIO{OUTPUT_PIN}からHIGH信号の送信を開始します。")
print("Ctrl+Cで終了します。終了時に信号はLOWに戻ります。")

try:
    # GPIOチップの制御を取得
    with gpiod.Chip(CHIP_NAME) as chip:
        # 特定のGPIOライン（ピン）を取得
        line = chip.get_line(OUTPUT_PIN)
        
        # ピンを「出力」、初期値を「HIGH(1)」として設定を要求
        line.request(
            consumer="sender",
            type=gpiod.LineReq.OUTPUT,
            default_vals=[1] # 起動時にピンをHIGHにする
        )
        
        # HIGH信号を維持するためにスクリプトを起動し続ける
        while True:
            time.sleep(1)

except KeyboardInterrupt:
    print(f"\nプログラムを終了します。GPIO{OUTPUT_PIN}をLOWに設定しました。")
    # with構文により、プログラム終了時にピンは自動的に解放され、信号は止まります。
except Exception as e:
    print(f"エラーが発生しました: {e}")