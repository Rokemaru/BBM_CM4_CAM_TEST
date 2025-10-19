from picamera2 import Picamera2
from PIL import Image
import time
import os

# --- 衛星パラメータからの設定 ---
OUTPUT_FILENAME = "output_without_restart_marker.jpg"
CAMERA_INDEX = 0  # pollenミッションのカメラを想定
TUNING_FILE_PATH = "/home/gardens/MMJ_SW_319_MMJ_CAM_MIS/imx219_80d.json" # チューニングファイルパス
# JPEG_RESTART_INTERVAL_MCU_COUNT は使わない
# -----------------------------

# --- その他の設定 ---
PNG_FILENAME = "temp_capture_no_rst.png" # 一時ファイル名
RESOLUTION = (1920, 1080) # 撮影解像度 (適宜変更してください)
JPEG_QUALITY = 90 # JPEG品質 (0-100)

picam2 = None # カメラオブジェクトを初期化

print(f"--- リスタートマーカーなしJPEG生成スクリプト ---")

try:
    # 1. カメラの初期化 (チューニングファイル適用)
    print(f"カメラ {CAMERA_INDEX} を初期化中...")
    tuning_applied = False
    if os.path.exists(TUNING_FILE_PATH):
        try:
            picam2 = Picamera2(camera_num=CAMERA_INDEX, tuning=TUNING_FILE_PATH)
            tuning_applied = True
            print(f"チューニングファイル '{os.path.basename(TUNING_FILE_PATH)}' を適用しました。")
        except Exception as e:
            print(f"警告: チューニングファイルの適用に失敗しました: {e}。デフォルト設定で続行します。")
            picam2 = Picamera2(camera_num=CAMERA_INDEX)
    else:
        print(f"警告: チューニングファイルが見つかりません: {TUNING_FILE_PATH}。デフォルト設定で続行します。")
        picam2 = Picamera2(camera_num=CAMERA_INDEX)

    config = picam2.create_still_configuration(main={"size": RESOLUTION})
    picam2.configure(config)
    print("カメラ設定完了。")

    # 2. 撮影
    print("撮影を開始します...")
    picam2.start()
    time.sleep(2) # センサー安定待機
    image_array = picam2.capture_array("main")
    picam2.stop()
    print("撮影完了。")

    # 3. PNGとして一時保存
    print(f"画像を '{PNG_FILENAME}' として一時保存中...")
    pil_image_png = Image.fromarray(image_array)
    pil_image_png.save(PNG_FILENAME, "PNG")
    print("PNG保存完了。")

    # 4. PNGを読み込み
    print(f"'{PNG_FILENAME}' を読み込み中...")
    pil_image_jpg = Image.open(PNG_FILENAME)
    print("PNG読み込み完了。")

    # 5. JPEGとして保存 (★rstオプションを指定しない★)
    print(f"画像を '{OUTPUT_FILENAME}' としてリスタートマーカーなしで保存中...")
    save_options = {
        "quality": JPEG_QUALITY,
        # ★★★ rst を指定しない ★★★
    }
    pil_image_jpg.save(OUTPUT_FILENAME, "JPEG", **save_options)
    print(f"JPEG保存完了 (品質: {JPEG_QUALITY}, RST: なし)。")

    # 6. 一時PNGファイルを削除
    try:
        os.remove(PNG_FILENAME)
        print(f"一時ファイル '{PNG_FILENAME}' を削除しました。")
    except OSError as e:
        print(f"警告: 一時ファイル '{PNG_FILENAME}' の削除に失敗しました: {e}")

    print("\n--- 処理完了 ---")

except Exception as e:
    print(f"\n!!! エラーが発生しました: {e}")

finally:
    # カメラリソース解放
    if picam2 and picam2.started:
        picam2.stop()
    if picam2:
        picam2.close()
        print("カメラリソースを解放しました。")
