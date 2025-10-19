import os
import time
from picamera2 import Picamera2
from PIL import Image
import RPi.GPIO as GPIO

# --- 以前解析したパラメータ設定 ---
CAM_NBR = 0
TUNING_FILE = "/home/gardens/MMJ_SW_319_MMJ_CAM_MIS/imx219_80d.json" # このパスは環境に合わせてください
WIDE = 3280
HEIGH = 2464
CAM_TIMES = 3
INTERVAL_TIME = 1.5  # 秒
LED_LEVEL = 100      # 0から100のパーセント

# LED設定
LED_PIN = 18 # BCMピン番号
LED_PWM_FREQUENCY = 10000 # 10KHz

# 保存先フォルダ名
OUTPUT_FOLDER = "simple_capture_output_dem4_つけてないやつ"

# --- ここからがメインの処理です ---
picam2 = None
pwm = None

try:
    
     #--- カメラ接続確認 (既存コードより) ---
    #available_cameras = Picamera2.global_camera_info()
#     if not available_cameras:
#         print("FATAL ERROR: No cameras found. Mission aborted.")
#         #GPIO.cleanup()
#     if CAM_NBR >= len(available_cameras):
#         print(f"WARNING: Camera {CAM_NBR} is not available. (Found {len(available_cameras)} cameras)")
#         print("--> Fallback: Using default camera 0.")
#         CAM_NBR = 0    
    
    
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
    if not os.path.exists(TUNING_FILE):
        print(f"警告: チューニングファイルが見つかりません: {TUNING_FILE}")
        picam2 = Picamera2(camera_num=CAM_NBR)
    else:
        print(f"-> チューニングファイル {TUNING_FILE} を読み込みます。")
        picam2 = Picamera2(tuning=TUNING_FILE, camera_num=CAM_NBR)

    config = picam2.create_still_configuration(main={"size": (WIDE, HEIGH)})
    picam2.configure(config)

    controls = {
        "ExposureTime": 2400, # シャッタースピード（マイクロ秒）
        "AnalogueGain": 1.0, #アナログゲイン
        "AwbEnable": True,
        "Contrast": 1.0,
        "Sharpness": 1,
        "Saturation": 1.0,
    }
    
    # 4. カメラの起動
    picam2.start()
    print("カメラを起動しました。")
    time.sleep(1.5) # 安定化を待つ
    
    # ========================================================================
    # Mission_Operator.pyのロジックに合わせてここから変更
    # ========================================================================

    # 5. 撮影ループ (メモリに画像を保存)
    captured_arrays = [] # キャプチャした画像を一時的に保存するリスト
    print(f"\n--- Capture Phase Started ({CAM_TIMES} shots) ---")
    
    print(f"LEDを {LED_LEVEL}% の明るさで点灯します。")
    pwm.ChangeDutyCycle(LED_LEVEL)
    time.sleep(1.0) # LEDの安定化を待つ

    capture_start_time = time.monotonic()

    for i in range(CAM_TIMES):
        # ループの中で毎回コントロールを再設定する「おまじない」
        picam2.set_controls(controls)
        time.sleep(0.2)
        
        shot_start_time = time.monotonic()
        image_array = picam2.capture_array("main")
        shot_end_time = time.monotonic()

        captured_arrays.append(image_array)
        elapsed_time = shot_end_time - shot_start_time
        print(f"({i + 1}/{CAM_TIMES}) Captured to memory successfully. (Time: {elapsed_time:.3f}s)")
        
        # 次の撮影がある場合のみ待機
        if i < CAM_TIMES - 1:
            wait_time = INTERVAL_TIME - elapsed_time
            if wait_time > 0:
                print(f"  -> Waiting for next shot... (Interval: {wait_time:.3f} seconds)")
                time.sleep(wait_time)
            else:
                print(f"  -> Interval skipped (Capture time {elapsed_time:.3f}s > Interval {INTERVAL_TIME}s)")

    capture_end_time = time.monotonic()
    print(f"--- Capture Phase Finished. (Total time: {capture_end_time - capture_start_time:.3f}s) ---")
    
    # 6. LEDを消灯
    pwm.ChangeDutyCycle(0)
    print("LED OFF.")
    
    # 7. 保存ループ (メモリからファイルへ一括保存)
    if not captured_arrays:
        print("No images were captured. Nothing to save.")
    else:
        print(f"\n--- Save Phase Started ({len(captured_arrays)} images) ---")
        save_start_time = time.monotonic()

        for i, image_array in enumerate(captured_arrays):
            save_path = os.path.join(OUTPUT_FOLDER, f"image_{i:03d}.png")
            try:
                Image.fromarray(image_array).save(save_path, "PNG")
                print(f"Saved successfully: {os.path.basename(save_path)}")
            except Exception as e:
                print(f"SAVE FAILED for image {i}: {e}")
        
        save_end_time = time.monotonic()
        print(f"--- Save Phase Finished. (Total time: {save_end_time - save_start_time:.3f}s) ---")

except Exception as e:
    print(f"\nエラーが発生しました: {e}")

finally:
    # 8. 後片付け
    print("\nリソースを解放しています...")
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
