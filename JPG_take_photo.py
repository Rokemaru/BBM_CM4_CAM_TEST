import os
import time
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import piexif 
from fractions import Fraction 

# ==============================================================================
# カメラパラメータテスト用スクリプト【最終完成版】
# - 保存形式をPNGからJPGに変更し、piexifエラーを解消
# ==============================================================================

def get_next_filename(directory: str) -> str:
    """指定されたディレクトリ内で、次の連番ファイル名を取得する"""
    os.makedirs(directory, exist_ok=True)
    # ★★ 変更点 ★★: 拡張子を.jpgに変更
    existing_files = [f for f in os.listdir(directory) if f.endswith('.jpg')]
    
    if not existing_files:
        # ★★ 変更点 ★★: 拡張子を.jpgに変更
        return os.path.join(directory, "000.jpg")
    
    max_num = -1
    for f in existing_files:
        try:
            num = int(os.path.splitext(f)[0])
            if num > max_num:
                max_num = num
        except ValueError:
            continue
            
    next_num = max_num + 1
    # ★★ 変更点 ★★: 拡張子を.jpgに変更
    return os.path.join(directory, f"{next_num:03d}.jpg")

def add_exif_data(filename: str, settings: dict, metadata: dict):
    """撮影した画像にExif情報を書き込む"""
    try:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

        if "ExposureTime" in metadata:
            exp_s = Fraction(metadata["ExposureTime"], 1000000).limit_denominator()
            exif_dict["Exif"][piexif.ExifIFD.ExposureTime] = (exp_s.numerator, exp_s.denominator)
        
        if "AnalogueGain" in metadata:
            iso = int(100 * metadata["AnalogueGain"])
            exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings] = iso

        simple_metadata = {
            "Exp": metadata.get("ExposureTime"),
            "AGain": metadata.get("AnalogueGain"),
            "ColourTemp": metadata.get("ColourTemperature"),
            "Lux": round(metadata.get("Lux", 0), 2)
        }
        comment = f"Settings: {str(settings)} | Actual: {str(simple_metadata)}"

        exif_dict["Exif"][piexif.ExifIFD.UserComment] = comment.encode("ascii", "ignore")
        
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
        print(f"Exif情報を {filename} に書き込みました。")

    except Exception as e:
        print(f"\nExif情報の書き込み中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def main():
    """テストを実行するメイン関数"""

    # ▼▼▼ パラメータ設定 ▼▼▼
    # ==========================================================================
    CAM_NBR = 1
    BASE_SAVE_DIR = "/home/gardens/Desktop"
    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 1080
    
    TUNING_FILE_PATH = "/home/gardens/Desktop/MMJ_CAM_MIS/imx219_80d.json"

    SHUTTER_SPEED = 50000
    LED_PIN = 18
    LED_LEVEL = 100
    
    ANALOGUE_GAIN = 1.0
    CONTRAST = 1.0
    SATURATION = 1.0
    SHARPNESS = 1.0
    COLOUR_GAINS = None
    
    user_settings = {
        "Exp": SHUTTER_SPEED, "AGain": ANALOGUE_GAIN, "Cont": CONTRAST,
        "Sat": SATURATION, "Sharp": SHARPNESS, "CGains": COLOUR_GAINS
    }
    # ==========================================================================
    
    picam2 = None
    pwm = None

    try:
        if CAM_NBR == 0:
            save_dir_name = "cam0_arducam_test"
        else:
            save_dir_name = "cam1_v2_test"
        
        final_save_dir = os.path.join(BASE_SAVE_DIR, save_dir_name)
        save_filepath = get_next_filename(final_save_dir)
        
        print(f"===== カメラパラメータテスト(最終完成版)を開始します =====")
        print(f"カメラ番号: {CAM_NBR}")
        print(f"保存ファイルパス: {save_filepath}")

        print("LEDを初期化しています...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        pwm = GPIO.PWM(LED_PIN, 10000)
        pwm.start(0)
        
        print("カメラを初期化しています...")
        tuning = None
        if CAM_NBR == 0 and TUNING_FILE_PATH and os.path.exists(TUNING_FILE_PATH):
            print(f"チューニングファイルを適用: {TUNING_FILE_PATH}")
            tuning = Picamera2.load_tuning_file(TUNING_FILE_PATH)
        
        picam2 = Picamera2(camera_num=CAM_NBR, tuning=tuning)
        
        config = picam2.create_still_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)})
        picam2.configure(config)
        
        controls = {}
        if SHUTTER_SPEED is not None: controls["ExposureTime"] = SHUTTER_SPEED
        if ANALOGUE_GAIN is not None: controls["AnalogueGain"] = ANALOGUE_GAIN
        if CONTRAST is not None: controls["Contrast"] = CONTRAST
        if SATURATION is not None: controls["Saturation"] = SATURATION
        if SHARPNESS is not None: controls["Sharpness"] = SHARPNESS
        if COLOUR_GAINS is not None: controls["ColourGains"] = COLOUR_GAINS

        if controls:
            print("カメラパラメータを設定します:", controls)
            picam2.set_controls(controls)
        
        picam2.start()
        time.sleep(1)

        print(f"LEDを {LED_LEVEL}% で点灯します...")
        pwm.ChangeDutyCycle(LED_LEVEL)
        time.sleep(1)
        
        print("撮影中...")
        metadata = picam2.capture_file(save_filepath)
        print(f"撮影完了！ 画像を {save_filepath} に保存しました。")
        print(f"取得したメタデータ: {metadata}")

        add_exif_data(save_filepath, user_settings, metadata)

    except Exception as e:
        print(f"\nメイン処理でエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("リソースを解放しています...")
        if picam2:
            if picam2.started:
                picam2.stop()
            picam2.close()
            print("カメラを解放しました。")
        
        if pwm:
            pwm.stop()
        
        GPIO.cleanup(LED_PIN)
        print(f"LED(GPIOピン {LED_PIN})を解放しました。")
        
        print("===== テストを終了します =====")

if __name__ == "__main__":
    main()