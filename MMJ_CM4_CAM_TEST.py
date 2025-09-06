import os
import time
from picamera2 import Picamera2
import RPi.GPIO as GPIO

# ==============================================================================
# カメラパラメータテスト用スクリプト【完全単体動作版】
# - このファイル1つだけで、カメラ撮影とLED制御のテストが完結します。
# - 実行するとデスクトップにカメラ別のフォルダが作られ、連番で写真が保存されます。
# ==============================================================================

def get_next_filename(directory: str) -> str:
    """指定されたディレクトリ内で、次の連番ファイル名を取得する"""
    os.makedirs(directory, exist_ok=True)
    existing_files = [f for f in os.listdir(directory) if f.endswith('.png')]
    
    if not existing_files:
        return os.path.join(directory, "000.png")
    
    max_num = -1
    for f in existing_files:
        try:
            num = int(os.path.splitext(f)[0])
            if num > max_num:
                max_num = num
        except ValueError:
            continue
            
    next_num = max_num + 1
    return os.path.join(directory, f"{next_num:03d}.png")


def main():
    """テストを実行するメイン関数"""

    # ▼▼▼ パラメータ設定 ▼▼▼
    # ==========================================================================

    # --- 基本設定 ---
    CAM_NBR = 0  # カメラ番号: 0=Arducam, 1=Raspberry Pi V2 Camera
    BASE_SAVE_DIR = "/home/gardens/Desktop"
    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 1080
    
    # --- Arducam専用設定 (CAM_NBR=0 の場合のみ有効) ---
    TUNING_FILE_PATH = "/home/gardens/Desktop/CAM_TEST/imx219_80d.json"
    # --- 撮影パラメータ ---
    SHUTTER_SPEED = 0  # マイクロ秒 (例: 20000 = 1/50秒)。Noneで自動露出
    LED_PIN = 18           # LEDを接続しているGPIOピン(BCM番号)
    LED_LEVEL = 100        # LEDの明るさ (0% ~ 100%)
    
    # --- 画質調整パラメータ (Noneにするとカメラの自動設定) ---
    ANALOGUE_GAIN = 1.0    # 1.0以上の値。大きくすると明るくなるがノイズが増える
    CONTRAST = 1.0         # 1.0が標準。大きくすると明暗がはっきりする
    SATURATION = 1.0       # 1.0が標準。0.0で白黒、大きくすると鮮やかになる
    SHARPNESS = 1.0        # 1.0が標準。大きくすると輪郭が強調される
    COLOUR_GAINS = None    # ホワイトバランス手動設定 (R, B)。通常はNoneでOK

    # ==========================================================================
    # ▲▲▲ パラメータ設定はここまで ▲▲▲

    # カメラとGPIOリソースを管理するための変数を初期化
    picam2 = None
    pwm = None

    try:
        # --- 1. 保存先の準備 ---
        if CAM_NBR == 0:
            save_dir_name = "cam0_arducam_test"
        else:
            save_dir_name = "cam1_v2_test"
        
        final_save_dir = os.path.join(BASE_SAVE_DIR, save_dir_name)
        save_filepath = get_next_filename(final_save_dir)
        
        print("===== カメラパラメータテスト(単体動作版)を開始します =====")
        print(f"カメラ番号: {CAM_NBR}")
        print(f"保存ファイルパス: {save_filepath}")

        # --- 2. GPIO (LED) の設定 ---
        print("LEDを初期化しています...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        # 高周波PWMでちらつきを抑制
        pwm = GPIO.PWM(LED_PIN, 10000)
        pwm.start(0)

        # --- 3. カメラの初期化と設定 ---
        print("カメラを初期化しています...")
        picam2 = Picamera2(camera_num=CAM_NBR)
        
        config = picam2.create_still_configuration(
            main={"size": (IMAGE_WIDTH, IMAGE_HEIGHT)}
        )
        picam2.configure(config)

        # チューニングファイルの適用 (必要な場合)
        if CAM_NBR == 0 and TUNING_FILE_PATH and os.path.exists(TUNING_FILE_PATH):
            print(f"チューニングファイルを適用: {TUNING_FILE_PATH}")
            tuning = Picamera2.load_tuning_file(TUNING_FILE_PATH)

        # パラメータ設定用の辞書を作成
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
        # パラメータが安定するまで少し待つ
        time.sleep(1)

        # --- 4. 撮影実行 ---
        print(f"LEDを {LED_LEVEL}% で点灯します...")
        pwm.ChangeDutyCycle(LED_LEVEL)
        # LEDが安定するまで待つ
        time.sleep(1)
        
        print("撮影中...")
        picam2.capture_file(save_filepath)
        print(f"撮影完了！ 画像を {save_filepath} に保存しました。")

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # --- 5. 後片付け ---
        # エラーが発生しても、必ずリソースを解放する
        print("リソースを解放しています...")
        if picam2 and picam2.started:
            picam2.stop()
        if picam2:
            picam2.close()
            print("カメラを解放しました。")
        
        # PWMを先に停止してからGPIOをクリーンアップ
        if pwm:
            pwm.stop()
        GPIO.cleanup()
        print("LED(GPIO)を解放しました。")
        
        print("===== テストを終了します =====")

if __name__ == "__main__":
    main()