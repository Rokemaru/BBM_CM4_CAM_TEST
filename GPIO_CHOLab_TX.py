import gpiod
import time

# --- 設定 ---
CHIP_NAME = "gpiochip4"
OUTPUT_PIN = 4
# ----------------

line = None
print(f"GPIO{OUTPUT_PIN}の送信プログラムを開始します。")

try:
    with gpiod.Chip(CHIP_NAME) as chip:
        line = chip.get_line(OUTPUT_PIN)
        
        # ピンを「出力モード」、初期値を「LOW(0)」として要求
        line.request(
            consumer="signal_sender",
            type=gpiod.LINE_REQ_DIR_OUT,
            default_vals=[0] # 開始時は必ずLOWにする
        )
        
        print("準備ができました。")
        
        while True:
            # ユーザーがエンターキーを押すのを待つ
            input("エンターキーを長押ししている間、HIGH信号を送信します。離すと止まります...")
            
            # キーが押されたらHIGHを出力
            print("-> HIGH信号を送信中...")
            line.set_value(1)
            
            # ユーザーがキーを離すのを待つ（実際には次のinputで待機）
            print("   キーが離されました。LOWに戻します。")
            line.set_value(0)


except KeyboardInterrupt:
    print("\nCtrl+Cが押されました。プログラムを終了します。")
except Exception as e:
    print(f"\nエラーが発生しました: {e}")

finally:
    # プログラムがどんな形で終了しても、必ずピンをLOWに戻す
    if line:
        print("後片付け処理：ピンを確実にLOWにします。")
        line.set_value(0)
    print("プログラムが完全に終了しました。")