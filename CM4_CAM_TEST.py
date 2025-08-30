import os
import time
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import traceback
import io
from PIL import Image # Pillowライブラリをインポート
import numpy as np   # NumPyをインポート

# ==============================================================================
# 高速連写対応 撮影スクリプト v4.1
# - BGRからRGBへの色空間変換を追加し、ファイルの互換性を向上
# ==============================================================================

# (設定項目は変更ありません)
# ==============================================================================
# ▼▼▼ 基本設定 ▼▼▼
# ==============================================================================
SAVE_TO_MEMORY_FIRST = True
CAM_NBR = 1
BASE_SAVE_DIR = "/home/gardens/Desktop/captures"
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
NUM_SHOTS = 10
INTERVAL_SEC = 0.5
SHUTTER_SPEED = 50000
ANALOGUE_GAIN = 1.0
CONTRAST = 1.0
SATURATION = 1.0
SHARPNESS = 1.0
AWB_ENABLE = True
COLOUR_GAINS = (1.0, 1.0)
USE_LED = True
LED_PIN = 18
LED_LEVEL = 100
# ==============================================================================
# ▲▲▲ 設定ここまで ▲▲▲
# ==============================================================================


def get_next_filename(directory: str, extension: str) -> str:
    # ... (内容は変更なし)
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
        # ... (準備部分は変更なし)
        print(f"📸 高速連写モード: {'有効' if SAVE_TO_MEMORY_FIRST else '無効'}")
        print(f"   撮影枚数: {NUM_SHOTS}枚, 撮影間隔: {INTERVAL_SEC}秒")
        final_save_dir = os.path.join(BASE_SAVE_DIR, "png")

        picam2 = Picamera2(camera_num=CAM_NBR)
        config = picam2.create_still_configuration(main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)})
        picam2.configure(config)
        
        controls = {"ExposureTime": SHUTTER_SPEED, "AnalogueGain": ANALOGUE_GAIN, "Contrast": CONTRAST, "Saturation": SATURATION, "Sharpness": SHARPNESS, "AwbEnable": AWB_ENABLE}
        if not AWB_ENABLE: controls["ColourGains"] = COLOUR_GAINS
        picam2.set_controls(controls)
        
        picam2.start()
        time.sleep(2)
        if USE_LED:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(LED_PIN, GPIO.OUT)
            pwm = GPIO.PWM(LED_PIN, 10000)
            pwm.start(LED_LEVEL)
            time.sleep(1)

        total_start_time = time.monotonic()

        if SAVE_TO_MEMORY_FIRST:
            print("\n--- 🚀 高速撮影フェーズ ---")
            captured_images_data = []
            start_filename_full = get_next_filename(final_save_dir, ".png")
            directory = os.path.dirname(start_filename_full)
            base_name = os.path.basename(start_filename_full)
            start_num = int(os.path.splitext(base_name)[0])
            extension = os.path.splitext(base_name)[1]
            
            for i in range(NUM_SHOTS):
                shot_num = i + 1
                shot_start_time = time.monotonic()
                
                raw_array = picam2.capture_array("main")
                
                if raw_array is not None and raw_array.size > 0:
                    current_num = start_num + i
                    filename = os.path.join(directory, f"{current_num:03d}{extension}")
                    captured_images_data.append((filename, raw_array))
                    shot_end_time = time.monotonic()
                    print(f"({shot_num}/{NUM_SHOTS}) メモリにRAWキャプチャ成功 (⏱️ {shot_end_time - shot_start_time:.3f}秒)")
                else:
                    print(f"({shot_num}/{NUM_SHOTS}) ❌ キャプチャ失敗: カメラから空のデータが返されました。")
                if shot_num < NUM_SHOTS: time.sleep(INTERVAL_SEC)
            
            capture_phase_end_time = time.monotonic()
            print(f"--- ✅ 全撮影完了 (合計時間: {capture_phase_end_time - total_start_time:.3f}秒) ---")

            if not captured_images_data:
                print("保存する画像がありません。")
            else:
                print("\n--- 🗜️ PNG圧縮 & 💾 一括保存フェーズ ---")
                save_start_time = time.monotonic()
                for filename, raw_array in captured_images_data:
                    
                    # --- ★★ 修正点 ★★ ---
                    # BGR (カメラの生データ) から RGB (Pillowの標準) へ色の順序を変換
                    rgb_array = raw_array[:, :, ::-1]
                    image = Image.fromarray(rgb_array)
                    # --- ★★ 修正ここまで ★★ ---

                    byte_buffer = io.BytesIO()
                    image.save(byte_buffer, format="PNG")
                    
                    with open(filename, "wb") as f:
                        f.write(byte_buffer.getvalue())
                    print(f"保存完了: {os.path.basename(filename)}")
                save_end_time = time.monotonic()
                print(f"--- ✅ 全保存完了 (合計時間: {save_end_time - save_start_time:.3f}秒) ---")
        else:
            # ...
            pass
        
        total_end_time = time.monotonic()
        print(f"\n✨ 全工程の合計所要時間: {total_end_time - total_start_time:.3f}秒")

    except Exception as e:
        print(f"\n❌ メイン処理でエラーが発生しました: {e}")
        traceback.print_exc()

    finally:
        # ... (後処理は変更なし)
        print("\nリソースを解放しています...")
        if picam2 and picam2.started: picam2.stop()
        if picam2: picam2.close()
        if USE_LED and 'pwm' in locals() and pwm is not None:
            pwm.stop()
            GPIO.cleanup(LED_PIN)
        print("テストを終了します。")

if __name__ == "__main__":
    main()