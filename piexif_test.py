import os
import time
import datetime
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import piexif 
from fractions import Fraction 

# ==============================================================================
# カメラパラメータテスト用スクリプト【Exif全部乗せ版】
# - 書き込める限りのサンプルExifデータを書き込むデモ
# - 仮想環境で最新のpiexifライブラリを使用することを想定
# ==============================================================================

def get_next_filename(directory: str) -> str:
    """連番のファイル名を取得（.png）"""
    os.makedirs(directory, exist_ok=True)
    existing_files = [f for f in os.listdir(directory) if f.endswith('.png')]
    if not existing_files:
        return os.path.join(directory, "000.png")
    max_num = max([int(os.path.splitext(f)[0]) for f in existing_files if f.split('.')[0].isdigit()])
    return os.path.join(directory, f"{max_num + 1:03d}.png")

def add_full_exif_data(filename: str, settings: dict, metadata: dict):
    """画像に可能な限りのExif情報を書き込む"""
    print("Exif情報の生成を開始します...")
    try:
        # --- 0th IFD (メイン情報) ---
        # 機器情報、画像説明、著作権など
        zeroth_ifd = {
            piexif.ImageIFD.Make: b"Raspberry Pi",
            piexif.ImageIFD.Model: b"Camera Module V3",
            piexif.ImageIFD.Software: b"MMJ Custom Script v4.0",
            piexif.ImageIFD.ImageDescription: "Exif書き込みテスト用のサンプル画像です。".encode('utf-8'),
            piexif.ImageIFD.Artist: "Gardens".encode('utf-8'),
            piexif.ImageIFD.Copyright: f"(C) {datetime.datetime.now().year} Gardens. All rights reserved.".encode('utf-8'),
            piexif.ImageIFD.DateTime: datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
        }

        # --- Exif IFD (撮影情報) ---
        # F値、ISO感度、シャッタースピードなど詳細な撮影データ
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
            piexif.ExifIFD.DateTimeDigitized: datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
            piexif.ExifIFD.LensModel: b"Raspberry Pi HQ Lens",
            piexif.ExifIFD.FNumber: (20, 10),  # F/2.0
            piexif.ExifIFD.ExposureProgram: 2,  # 2: Normal program
            piexif.ExifIFD.ISOSpeedRatings: settings.get("AGain", 1.0) * 100,
            piexif.ExifIFD.ExposureTime: (1, int(1000000 / settings.get("Exp", 10000))), # 1/n sec
            piexif.ExifIFD.FocalLength: (35, 1), # 35mm
            piexif.ExifIFD.WhiteBalance: 0, # 0: Auto
        }
        
        # ユーザーコメント欄には、これまで通り実際のパラメータを書き込む
        simple_metadata = {k: metadata.get(k) for k in ["ExposureTime", "AnalogueGain", "ColourTemperature", "Lux"]}
        comment = f"Settings: {str(settings)} | Actual: {str(simple_metadata)}"
        exif_ifd[piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(comment, encoding="unicode")


        # --- GPS IFD (位置情報) ---
        # 緯度・経度・高度などの位置データ（サンプルとして習志野市の座標）
        lat_deg, lat_min, lat_sec = 35, 41, 1  # 35° 41' 1" N
        lon_deg, lon_min, lon_sec = 140, 1, 25 # 140° 1' 25" E
        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 2, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef: b'N',
            piexif.GPSIFD.GPSLatitude: ((lat_deg, 1), (lat_min, 1), (lat_sec, 1)),
            piexif.GPSIFD.GPSLongitudeRef: b'E',
            piexif.GPSIFD.GPSLongitude: ((lon_deg, 1), (lon_min, 1), (lon_sec, 1)),
            piexif.GPSIFD.GPSAltitudeRef: 0,
            piexif.GPSIFD.GPSAltitude: (15, 1), # 標高15m
        }

        # 各辞書をまとめて、バイトデータに変換
        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd}
        exif_bytes = piexif.dump(exif_dict)
        
        # 画像にExifを挿入
        piexif.insert(exif_bytes, filename)
        print(f"🎉 全種類のExif情報を {filename} に書き込みました。")

    except Exception as e:
        print(f"\nExif情報の書き込み中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def main():
    # パラメータ設定 (適宜変更してください)
    CAM_NBR = 1
    BASE_SAVE_DIR = "/home/gardens/Desktop"
    IMAGE_WIDTH, IMAGE_HEIGHT = 1920, 1080
    LED_PIN, LED_LEVEL = 18, 100
    SHUTTER_SPEED, ANALOGUE_GAIN = 50000, 1.0
    CONTRAST, SATURATION, SHARPNESS = 1.0, 1.0, 1.0
    user_settings = {"Exp": SHUTTER_SPEED, "AGain": ANALOGUE_GAIN}

    # 撮影ロジック (変更なし)
    picam2, pwm = None, None
    try:
        save_dir_name = f"cam{CAM_NBR}_test"
        final_save_dir = os.path.join(BASE_SAVE_DIR, save_dir_name)
        save_filepath = get_next_filename(final_save_dir)
        print(f"===== Exif全部乗せテストを開始します =====")
        print(f"保存ファイルパス: {save_filepath}")

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        pwm = GPIO.PWM(LED_PIN, 10000)
        pwm.start(0)
        
        picam2 = Picamera2(camera_num=CAM_NBR)
        config = picam2.create_still_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)})
        picam2.configure(config)
        
        controls = {"ExposureTime": SHUTTER_SPEED, "AnalogueGain": ANALOGUE_GAIN,
                    "Contrast": CONTRAST, "Saturation": SATURATION, "Sharpness": SHARPNESS}
        picam2.set_controls(controls)
        
        picam2.start(); time.sleep(1)
        pwm.ChangeDutyCycle(LED_LEVEL); time.sleep(1)
        
        metadata = picam2.capture_file(save_filepath)
        print(f"撮影完了！ 画像を {save_filepath} に保存しました。")

        add_full_exif_data(save_filepath, user_settings, metadata)

    except Exception as e:
        print(f"\nメイン処理でエラーが発生しました: {e}"); import traceback; traceback.print_exc()
    finally:
        print("リソースを解放しています...")
        if picam2 and picam2.started: picam2.stop()
        if pwm: pwm.stop()
        GPIO.cleanup(LED_PIN)
        print("テストを終了します。")

if __name__ == "__main__":
    main()