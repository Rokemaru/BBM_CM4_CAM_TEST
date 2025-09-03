import os
import time
from picamera2 import Picamera2
from PIL import Image
import RPi.GPIO as GPIO

# --- 以前解析したパラメータ設定 ---
# この値を変更することで、撮影条件をカスタマイズできます。
CAM_NBR = 0
TUNING_FILE = "/home/gardens/MMJ_CAM_MIS/imx219_80d.json" # このパスは環境に合わせてください
WIDE = 3280
HEIGH = 2464
CAM_TIMES = 21
INTERVAL_TIME = 1.5  # 秒
LED_LEVEL = 100      # 0から100のパーセント

# LED設定
LED_PIN = 18 # BCMピン番号
LED_PWM_FREQUENCY = 10000 # 10KHz

# 保存先フォルダ名
OUTPUT_FOLDER = "simple_capture_output"

# --- ここからがメインの処理です ---
picam2 = None
pwm = None

try:
    # 1. 保存先フォルダを作成
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"画像は '{OUTPUT_FOLDER}' フォルダに保存されます。")

    # 2. LEDの準備
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    pwm = GPIO.PWM(LED_PIN, LED_PWM_FREQUENCY)
    pwm.start(0)

    # 3. カメラの初期化と設定
    print(f"カメラ{CAM_NBR}を初期化しています...")
    # チューニングファイルの存在確認
    if not os.path.exists(TUNING_FILE):
        print(f"警告: チューニングファイルが見つかりません: {TUNING_FILE}")
        print("-> デフォルト設定でカメラを初期化します。")
        picam2 = Picamera2(camera_num=CAM_NBR)
    else:
        print(f"-> チューニングファイル {TUNING_FILE} を読み込みます。")
        picam2 = Picamera2(tuning=TUNING_FILE, camera_num=CAM_NBR)

    # 解像度の設定
    config = picam2.create_still_configuration(main={"size": (WIDE, HEIGH)})
    picam2.configure(config)

    # オート画質モードのコントロールを設定
    # シャッタースピードとゲインは自動調整に任せます
    controls = {
        "AwbEnable": True,  # ホワイトバランス自動
        "Contrast": 1.0,
        "Sharpness": 1,
        "Saturation": 1.0,
    }
    
    # 4. カメラの起動
    picam2.start()
    print("カメラを起動しました。設定を適用します...")
    time.sleep(1.5)  # カメラの安定化を待つ
    picam2.set_controls(controls)
    print("設定適用完了。")


    # 5. 撮影ループ
    print(f"\n--- 撮影を開始します ({CAM_TIMES}回) ---")
    
    # 撮影前にLEDを点灯
    print(f"LEDを {LED_LEVEL}% の明るさで点灯します。")
    pwm.ChangeDutyCycle(LED_LEVEL)
    time.sleep(1.0) # LEDの安定化を待つ

    for i in range(CAM_TIMES):
        shot_start_time = time.monotonic()
        
        # ファイル名を決定 (例: image_000.png, image_001.png ...)
        save_path = os.path.join(OUTPUT_FOLDER, f"image_{i:03d}.png")
        
        print(f"({i + 1}/{CAM_TIMES}) 撮影中 -> {save_path}")

        # メモリに画像をキャプチャ
        image_array = picam2.capture_array("main")
        
        # PILを使ってPNG形式で保存
        Image.fromarray(image_array).save(save_path, "PNG")

        shot_end_time = time.monotonic()
        elapsed_time = shot_end_time - shot_start_time
        print(f"  撮影と保存完了 (処理時間: {elapsed_time:.2f}秒)")

        # 次の撮影までの待機
        wait_time = INTERVAL_TIME - elapsed_time
        if i < CAM_TIMES - 1 and wait_time > 0:
            print(f"  次の撮影まで {wait_time:.2f}秒 待機します...")
            time.sleep(wait_time)

    print("\n--- 全ての撮影が完了しました ---")

except Exception as e:
    print(f"\nエラーが発生しました: {e}")

finally:
    # 6. 後片付け
    print("リソースを解放しています...")
    if picam2 and picam2.started:
        picam2.stop()
        print("  カメラを停止しました。")
    if picam2:
        picam2.close()
        print("  カメラを解放しました。")
    if pwm:
        pwm.stop()
        print("  LED PWMを停止しました。")
    
    GPIO.cleanup()
    print("  GPIOをクリーンアップしました。")
    print("プログラムを終了します。")
