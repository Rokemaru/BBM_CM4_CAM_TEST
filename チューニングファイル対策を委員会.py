# test_operator_equivalent.py
import os
import time
import RPi.GPIO as GPIO
from PIL import Image
from picamera2 import Picamera2
import syslog

# ==============================================================================
# Mission_Operator.pyのtake_imaging_operatorの機能を完全に再現
# パラメータはpollenミッションを想定して固定値で設定
# ==============================================================================

# --- ① 本来は引数で渡されるパラメータを、ここで固定値として定義 ---
cam_nbr = 0
tuning_file = "/home/gardens/MMJ_CAM_MIS/imx219_80d.json" # Mission.pyで指定されているパス
wide = 1640
heigh = 1232
shutter_speed = 30000
analogue_gain = 1.0
auto_white_balance = False  # 手動ホワイトバランス
red_Gains = 1.8
blue_Gains = 1.5
contrast = 1.0
sharpness = 1.0
saturation = 1.0
cam_times = 5               # 5枚撮影するテスト
interval_time = 2.0         # 撮影間隔2秒
led_level = 50              # LED光量50%

# --- Mission_Prameter.pyから持ってきたLED関連の定数 ---
LED_PIN = 18
LED_PWM_FREQUENCY = 10000

# --- テスト用の設定 ---
output_dir = "operator_test_output"
os.makedirs(output_dir, exist_ok=True)
print(f"--- 'take_imaging_operator'の単独動作テストを開始します ---")
print(f"画像は ./{output_dir}/ に保存されます。")
syslog.openlog("StandaloneCameraTest")

# ==============================================================================
# ↓↓↓ ここから下は take_imaging_operator の中身とほぼ同じロジック ↓↓↓
# ==============================================================================

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
pwm = GPIO.PWM(LED_PIN, LED_PWM_FREQUENCY)
pwm.start(0)

picam2 = None
saved_file_paths = []

try:
    # --- カメラ初期化 ---
    print(f"カメラ {cam_nbr} をチューニングファイルありで初期化中...")
    syslog.syslog("Initializing camera with tuning file.")
    if not os.path.exists(tuning_file):
        raise FileNotFoundError(f"致命的エラー: チューニングファイルが見つかりません: {tuning_file}")
    picam2 = Picamera2(tuning=tuning_file, camera_num=cam_nbr)

    # --- カメラコンフィグ設定 ---
    camera_config = picam2.create_still_configuration(main={"size": (wide, heigh)})
    picam2.configure(camera_config)
    picam2.start()

    # --- カメラコントロール設定 ---
    ctrl = {
        "ExposureTime": shutter_speed,
        "AnalogueGain": analogue_gain,
        "AwbEnable": auto_white_balance,
        "Contrast": contrast,
        "Saturation": saturation,
        "Sharpness": sharpness,
    }
    if not auto_white_balance:
        ctrl["ColourGains"] = (red_Gains, blue_Gains)

    print("カメラ安定化のため1秒待機...")
    time.sleep(1.0)
    picam2.set_controls(ctrl)
    print("コントロール設定完了。")

    # --- 撮影ループ ---
    print(f"撮影開始: {cam_times}枚")
    pwm.ChangeDutyCycle(led_level)
    print(f"LED点灯: {led_level}%")
    time.sleep(1.0)  # LED安定化待ち

    for i in range(cam_times):
        # 以前提案した「おまじない」も再現
        picam2.set_controls(ctrl)
        time.sleep(0.2)

        shot_start_time = time.monotonic()
        raw_array = picam2.capture_array("main")
        shot_end_time = time.monotonic()

        if raw_array is not None and raw_array.size > 0:
            elapsed = shot_end_time - shot_start_time
            print(f"({i + 1}/{cam_times}) 撮影成功 (処理時間: {elapsed:.3f}s)")

            save_path = os.path.join(output_dir, f"test_image_{i:02d}.png")
            Image.fromarray(raw_array).save(save_path, "PNG")
            saved_file_paths.append(save_path)
        else:
            print(f"({i + 1}/{cam_times}) 撮影失敗: データが空です。")

        if i < cam_times - 1:
            wait_time = interval_time - (shot_end_time - shot_start_time)
            if wait_time > 0:
                print(f"  -> 次の撮影まで {wait_time:.3f}秒 待機...")
                time.sleep(wait_time)

except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")
    syslog.syslog(f"ERROR: {e}")
finally:
    # --- クリーンアップ処理 ---
    print("リソースをクリーンアップします...")
    if picam2 and picam2.started:
        picam2.stop()
    if picam2:
        picam2.close()
    
    pwm.stop()
    GPIO.cleanup(LED_PIN)
    print("--- テスト完了 ---")
