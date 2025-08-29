import os
import time
from Mission_Operator import Mission_Operator

# ==============================================================================
# このスクリプトは、カメラの各種パラメータ設定をテストするための単体実行ファイルです。
# 下の「▼▼▼ パラメータ設定 ▼▼▼」セクションの値を変更して実行してください。
# 実行すると、'test_images'というフォルダが作成され、そこに写真が保存されます。
# ==============================================================================

def main():
    """テストを実行するメイン関数"""

    # ▼▼▼ パラメータ設定 ▼▼▼
    # ==========================================================================

    # --- 基本設定 ---
    # カメラ番号: 0=Arducam, 1=Raspberry Pi V2 Camera
    CAM_NBR = 0
    # 写真の保存先フォルダ
    SAVE_DIR = "test_images"
    # 解像度
    IMAGE_WIDTH = 1920
    IMAGE_HEIGHT = 1080
    
    # --- Arducam専用設定 ---
    # Arducam (CAM_NBR=0) を使う場合のみ有効。不要な場合は None にする。
    TUNING_FILE_PATH = "/home/gardens/Desktop/MMJ_CAM_MIS/imx219_80d.json"

    # --- 撮影パラメータ ---
    # シャッタースピード (マイクロ秒)。None にすると自動露出
    SHUTTER_SPEED = 20000  # 例: 20000マイクロ秒 = 1/50秒
    # LEDの明るさ (0% ~ 100%)
    LED_LEVEL = 80
    
    # --- 画質調整パラメータ (Noneにするとカメラの自動設定が使われます) ---
    # アナログゲイン (1.0以上の値。数値を大きくすると明るくなるがノイズが増える)
    ANALOGUE_GAIN = 1.0 # 例: 1.0, 2.0, 4.0 など
    
    # コントラスト (デフォルト1.0。大きくすると明暗がはっきりする)
    CONTRAST = 1.2 # 例: 0.5 (低い), 1.0 (標準), 1.5 (高い)
    
    # 彩度 (デフォルト1.0。0.0で白黒、大きくすると色が鮮やかになる)
    SATURATION = 1.2 # 例: 0.0 (白黒), 1.0 (標準), 1.8 (鮮やか)
    
    # シャープネス (デフォルト1.0。大きくすると輪郭が強調される)
    SHARPNESS = 1.0 # 例: 0.5 (ソフト), 1.0 (標準), 2.0 (シャープ)
    
    # カラーゲイン (ホワイトバランスの手動設定)。(赤, 青)のゲインを指定。
    # 通常は自動(None)で問題ありません。
    COLOUR_GAINS = None # 例: (1.5, 1.2) -> 赤を強く、青を少し強く

    # ==========================================================================
    # ▲▲▲ パラメータ設定はここまで ▲▲▲

    # 保存先ディレクトリを作成
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    # ファイル名に現在時刻を追加して、毎回違う名前で保存されるようにする
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    print("===== カメラパラメータテストを開始します =====")
    print(f"カメラ番号: {CAM_NBR}")
    print(f"解像度: {IMAGE_WIDTH}x{IMAGE_HEIGHT}")
    print(f"保存先: {SAVE_DIR}")
    
    # Mission_Operatorの関数を呼び出して撮影を実行
    try:
        Mission_Operator.take_imaging_operator(
            # --- 基本パラメータ ---
            cam_nbr=CAM_NBR,
            tuning_file=TUNING_FILE_PATH if CAM_NBR == 0 else None,
            wide=IMAGE_WIDTH,
            heigh=IMAGE_HEIGHT,
            
            # --- テスト用の固定パラメータ ---
            cam_times=1,          # 1枚だけ撮影
            intervaltime=1,       # 撮影間隔は1秒
            mission_id=timestamp, # ファイル名になるID
            media_folder=SAVE_DIR,
            mission_type_id=0x99, # テスト用ID
            photo_type_id=0x99,   # テスト用ID

            # --- 可変パラメータ ---
            shutter_speed=SHUTTER_SPEED,
            led_level=LED_LEVEL,
            analogue_gain=ANALOGUE_GAIN,
            contrast=CONTRAST,
            saturation=SATURATION,
            sharpness=SHARPNESS,
            colour_gains=COLOUR_GAINS,
        )
        print("\n撮影が完了しました。")
        print(f"画像は {SAVE_DIR} フォルダに保存されています。")

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("===== テストを終了します =====")

if __name__ == "__main__":
    main()