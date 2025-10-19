import sys
from pathlib import Path
from typing import List, Tuple

def measure_restart_intervals(jpeg_filepath: Path):
    """
    指定されたJPEGファイル内のリスタートマーカーを探し、
    それらの間のバイト間隔を測定して表示する。
    """

    if not jpeg_filepath.is_file():
        print(f"エラー: ファイルが見つかりません: {jpeg_filepath}", file=sys.stderr)
        return

    try:
        with open(jpeg_filepath, "rb") as f:
            data = f.read()
    except IOError as e:
        print(f"エラー: ファイルを読み込めません: {e}", file=sys.stderr)
        return

    print(f"--- ファイル '{jpeg_filepath.name}' のリスタートマーカー間隔を測定中 ---")

    markers_found: List[Tuple[int, int]] = [] # (offset, marker_number)

    # FF D0 から FF D7 までのマーカーをファイル全体から検索
    for i in range(8):
        marker = bytes([0xFF, 0xD0 + i]) # FF D0, FF D1, ... FF D7
        offset = data.find(marker)
        start_offset = 0

        while offset != -1:
            markers_found.append((offset, i)) # オフセットとマーカー番号(0-7)を記録
            # 次のマーカーを現在の位置以降から探す
            start_offset = offset + 1
            offset = data.find(marker, start_offset)

    if not markers_found:
        print("  -> リスタートマーカーは見つかりませんでした。")
        print("--- 測定完了 ---")
        return

    # 見つかったマーカーをファイル内での出現順（オフセット順）にソート
    markers_found.sort(key=lambda item: item[0])

    print(f"  -> 合計 {len(markers_found)} 個のリスタートマーカーを発見しました。")
    print("\n--- マーカー間のバイト間隔 ---")

    intervals: List[int] = []
    # ソートされたマーカーリストを走査し、連続するマーカー間のバイト数を計算
    for k in range(1, len(markers_found)):
        prev_offset, prev_marker_num = markers_found[k-1]
        current_offset, current_marker_num = markers_found[k]

        interval = current_offset - prev_offset
        intervals.append(interval)

        # マーカー番号が期待通りかチェック (0->1, 1->2, ..., 7->0)
        expected_next_marker_num = (prev_marker_num + 1) % 8
        marker_sequence_ok = (current_marker_num == expected_next_marker_num)
        sequence_note = "" if marker_sequence_ok else "  <-- マーカー順序が飛びました！"

        print(f"  RST{prev_marker_num} ({prev_offset:#x}) -> RST{current_marker_num} ({current_offset:#x}) : {interval} バイト{sequence_note}")

    if intervals:
        average_interval = sum(intervals) / len(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)
        print("\n--- 統計 ---")
        print(f"  平均間隔: {average_interval:.2f} バイト")
        print(f"  最小間隔: {min_interval} バイト")
        print(f"  最大間隔: {max_interval} バイト")

    print("\n--- 測定完了 ---")

# --- メインの実行部分 ---
if __name__ == "__main__":
    # コマンドライン引数からファイルパスを取得
    if len(sys.argv) < 2:
        print("使い方: python check_marker_rpi.py <JPEGファイルのパス>", file=sys.stderr)
        sys.exit(1) # エラー終了

    target_jpeg_path_arg = Path(sys.argv[1])
    measure_restart_intervals(target_jpeg_path_arg)