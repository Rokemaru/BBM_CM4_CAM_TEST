import gpiod
import time

# --- 設定 ---
CHIP_NAME = "gpiochip4"
OUTPUT_PIN = 4
# ----------------

print(f"GPIO{OUTPUT_PIN}の送信プログラムを開始します。")

try:
    # 1. GPIOハードウェアへの接続を開始 (扉を開ける)
    with gpiod.Chip(CHIP_NAME) as chip:
        line = chip.get_line(OUTPUT_PIN)
        line.request(
            consumer="sender_final",
            type=gpiod.LINE_REQ_DIR_OUT
        )

        # 2. 接続した「内側」で、メインの処理と後片付けを行う
        try:
            print(f"-> HIGH信号を出力中... (終了するには Ctrl+C)")
            line.set_value(1) # 点灯
            
            # プログラムを動かし続けるためのループ
            while True:
                time.sleep(1)
        
        finally:
            # 3. Ctrl+Cで中断されても、扉が閉まる「前」に必ずここが実行される
            print("\n後片付け処理：ピンを確実にLOWに戻します。")
            line.set_value(0) # 消灯

except KeyboardInterrupt:
    # ユーザーがCtrl+Cを押したことを知らせるメッセージ
    print("\nプログラムを正常に終了しました。")
except Exception as e:
    print(f"エラーが発生しました: {e}")