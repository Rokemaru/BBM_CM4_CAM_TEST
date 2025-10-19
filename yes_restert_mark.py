from PIL import Image
import os
from pathlib import Path

# --- 設定 ---
output_filename = "definitely_with_restart_marker.jpg"
image_width = 640
image_height = 480
background_color = (200, 100, 150) # 適当な色 (R, G, B)
jpeg_quality = 90
restart_interval = 1 # ★リスタート間隔 (MCU単位)

# --- 画像生成 ---
try:
    # 新しい画像を作成
    img = Image.new('RGB', (image_width, image_height), color=background_color)
    print(f"サイズ {image_width}x{image_height} の画像を生成しました。")

    # --- JPEGとして保存 (rstオプションを確実に指定) ---
    print(f"'{output_filename}' をリスタートマーการ間隔 {restart_interval} MCU で保存します...")
    save_options = {
        "quality": jpeg_quality,
        "rst": restart_interval # ★★★ この行で確実に指定 ★★★
    }
    img.save(output_filename, "JPEG", **save_options)
    print(f"JPEG保存完了 (品質: {jpeg_quality}, RST間隔: {restart_interval})。")

    # 生成されたファイルのサイズを表示
    file_size = os.path.getsize(output_filename)
    print(f"ファイルサイズ: {file_size} バイト")

    print("\n--- 検証 ---")
    print(f"生成された '{output_filename}' に対して、check_marker.py スクリプトを実行してマーカーを確認してください。")
    print(f"例: python check_marker.py {output_filename}")


except Exception as e:
    print(f"エラーが発生しました: {e}")