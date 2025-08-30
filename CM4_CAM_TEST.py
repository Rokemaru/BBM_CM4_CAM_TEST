import os
import time
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import traceback

# ==============================================================================
# 多機能撮影スクリプト v2.0
# - 連続撮影（回数、間隔）に対応
# - 画質調整（コントラスト、彩度、シャープネス）に対応
# - カラーゲイン（ホワイトバランス）の手動設定に対応
# ==============================================================================

# ==============================================================================
# ▼▼▼ 基本設定 ▼▼▼
# ==============================================================================
CAM_NBR = 1
BASE_SAVE_DIR = "/home/gardens/Desktop/captures" # 保存先フォルダ
IMAGE_WIDTH = 1920  # 画像の幅 (ピクセル)
IMAGE_HEIGHT = 1080 # 画像の高さ (ピクセル)
TUNING_FILE_PATH = None # 必要であれば指定 "/path/to/tuning.json"

# --- 連続撮影の設定 ---
NUM_SHOTS = 5          # 撮影する枚数
INTERVAL_SEC = 2       # 撮影ごとの間隔 (秒)

# --- 撮影パラメータ ---
# 露出時間 (マイクロ秒)。1秒 = 1,000,000マイクロ秒
SHUTTER_SPEED = 50000
# アナログゲイン。センサーの感度。ISO 100相当が 1.0
ANALOGUE_GAIN = 1.0

# --- 画質調整パラメータ ---
# コントラスト (0.0 ~ 32.0, デフォルト: 1.0)
CONTRAST = 1.2
# 彩度 (0.0 ~ 32.0, デフォルト: 1.0)
SATURATION = 1.0
# シャープネス (0.0 ~ 16.0, デフォルト: 1.0)
SHARPNESS = 1.5

# --- ホワイトバランスとカラーゲインの設定 ---
# AWB(オートホワイトバランス)を有効にするか (True/False)
# Falseにしないと、下のColourGainsは適用されません。
AWB_ENABLE = True
# カラーゲインを手動で設定する場合 (AWB_ENABLEをFalseにする必要あり)
# (赤ゲイン, 青ゲイン) のタプルで指定。例: (2.0, 1.2)
COLOUR_GAINS = (1.0, 1.0)

# --- LED設定 ---
USE_LED = True
LED_PIN = 18           # LEDを接続しているGPIOピン番号 (BCMモード)
LED_LEVEL = 100        # LEDの光量 (0〜100のパーセント)
# ==============================================================================
# ▲▲▲ 設定ここまで ▲▲▲
# ==============================================================================


def get_next_filename(directory: str, extension: str) -> str:
    """指定されたディレクトリと拡張子で、次の連番ファイル名を取得する"""
    os.makedirs(directory, exist_ok=True)
    if not extension.startswith('.'): extension = '.' + extension
    
    existing_files = [f for f in os.listdir(directory) if f.lower().endswith(extension)]
    if not existing_files: return os.path.join(directory, f"000{extension}")
    
    max_num = -1
    for f in existing_files:
        try:
            num = int(os.path.splitext(f)[0])
            if num > max_num: max_num = num
        except ValueError: continue
            
    return os.path.join(directory, f"{max_num + 1:03d}{extension}")

def main():
    picam2 = None
    pwm = None

    try:
        # --- 撮影準備 ---
        print(f"📸 撮影を開始します (合計: {NUM_SHOTS}枚, 間隔: {INTERVAL_SEC}秒)")
        if CAM_NBR == 0: save_dir_name = "cam0_arducam"
        else: save_dir_name = "cam1_v2"
        
        final_save_dir = os.path.join(BASE_SAVE_DIR, save_dir_name, "png")

        picam2 = Picamera2(camera_num=CAM_NBR)
        config = picam2.create_still_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)})
        picam2.configure(config)
        
        # --- パラメータ設定 ---
        controls = {
            "ExposureTime": SHUTTER_SPEED,
            "AnalogueGain": ANALOGUE_GAIN,
            "Contrast": CONTRAST,
            "Saturation": SATURATION,
            "Sharpness": SHARPNESS,
            "AwbEnable": AWB_ENABLE,
        }
        # AWBが無効の時だけColourGainsを設定
        if not AWB_ENABLE:
            controls["ColourGains"] = COLOUR_GAINS
        
        picam2.set_controls(controls)
        print("カメラパラメータを設定しました:", controls)
        
        picam2.start()
        time.sleep(2) # 設定を反映させるために長めに待つ

        # LED点灯
        if USE_LED:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(LED_PIN, GPIO.OUT)
            pwm = GPIO.PWM(LED_PIN, 10000)
            pwm.start(LED_LEVEL)
            time.sleep(1)

        # --- 撮影ループ ---
        for i in range(NUM_SHOTS):
            shot_num = i + 1
            print(f"\n撮影中... ({shot_num}/{NUM_SHOTS}枚目)")
            
            png_filepath = get_next_filename(final_save_dir, ".png")
            
            picam2.capture_file(png_filepath)
            print(f"✅ 保存しました: {png_filepath}")

            # 最後の撮影でなければ、指定した時間待機
            if shot_num < NUM_SHOTS:
                print(f"次の撮影まで {INTERVAL_SEC} 秒待機します...")
                time.sleep(INTERVAL_SEC)

    except Exception as e:
        print(f"\n❌ メイン処理でエラーが発生しました: {e}")
        traceback.print_exc()

    finally:
        # --- 後片付け ---
        print("\nリソースを解放しています...")
        if picam2 and picam2.started: picam2.stop()
        if picam2: picam2.close()
        
        if USE_LED and 'pwm' in locals() and pwm is not None:
            pwm.stop()
            GPIO.cleanup(LED_PIN)
        print("テストを終了します。")

if __name__ == "__main__":
    main()