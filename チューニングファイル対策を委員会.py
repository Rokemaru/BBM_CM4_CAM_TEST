# test_tuning.py
from picamera2 import Picamera2
import time
import os

# --- テスト用の固定パラメータ ---
# pollen_take_imaging_modeで実際に使われている値を設定します
tuning_file = "/home/gardens/MMJ_CAM_MIS/imx219_80d.json"
camera_num = 0  # pollenミッションはカメラ0を使用
wide = 3280
heigh = 2464
shutter_speed = 20000  # 例: 20000マイクロ秒
analogue_gain = 1.0    # 例: 1.0

# --- 1. チューニングファイルを指定して撮影 ---
picam2_with_tuning = None
print("--- 1. チューニングファイルありのテストを開始 ---")

# ファイルの存在を最初に確認
if not os.path.exists(tuning_file):
    print(f"FATAL: チューニングファイルが見つかりません: {tuning_file}")
else:
    try:
        print(f"カメラ {camera_num} をチューニングファイルありで初期化します...")
        picam2_with_tuning = Picamera2(tuning=tuning_file, camera_num=camera_num)
        config = picam2_with_tuning.create_still_configuration(main={"size": (wide, heigh)})
        picam2_with_tuning.configure(config)

        # 比較のため、露出とWBは手動で固定します
        ctrl = {
            "ExposureTime": shutter_speed,
            "AnalogueGain": analogue_gain,
            "AwbEnable": False,
            "ColourGains": (1.8, 1.5)  # 例としての固定値
        }
        picam2_with_tuning.set_controls(ctrl)

        picam2_with_tuning.start()
        print("カメラ起動。安定化のために2秒待機します...")
        time.sleep(2)

        output_file = "test_WITH_tuning.jpg"
        print(f"撮影します... -> {output_file}")
        picam2_with_tuning.capture_file(output_file)
        print("撮影完了。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        if picam2_with_tuning:
            picam2_with_tuning.stop()
            picam2_with_tuning.close()
        print("--- テスト1 終了 ---")


# --- 2. 比較のため、チューニングファイルなしで撮影 ---
picam2_no_tuning = None
print("\n--- 2. チューニングファイルなしのテストを開始 ---")
try:
    print(f"カメラ {camera_num} をチューニングファイルなしで初期化します...")
    picam2_no_tuning = Picamera2(camera_num=camera_num)
    config = picam2_no_tuning.create_still_configuration(main={"size": (wide, heigh)})
    picam2_no_tuning.configure(config)

    # 全く同じパラメータを設定します
    ctrl = {
        "ExposureTime": shutter_speed,
        "AnalogueGain": analogue_gain,
        "AwbEnable": False,
        "ColourGains": (1.8, 1.5)
    }
    picam2_no_tuning.set_controls(ctrl)

    picam2_no_tuning.start()
    print("カメラ起動。安定化のために2秒待機します...")
    time.sleep(2)

    output_file = "test_WITHOUT_tuning.jpg"
    print(f"撮影します... -> {output_file}")
    picam2_no_tuning.capture_file(output_file)
    print("撮影完了。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
finally:
    if picam2_no_tuning:
        picam2_no_tuning.stop()
        picam2_no_tuning.close()
    print("--- テスト2 終了 ---")
