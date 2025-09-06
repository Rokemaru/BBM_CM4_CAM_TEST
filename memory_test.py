# memory_test.py
import MT25QL01GBBB_20231023 as MT25QL01GBBB
import time

# --- 設定項目 ---
# テストに使用するメモリアドレス（既存のデータを破壊しないよう注意してください）
TEST_ADDRESS = 0x00123400 
# 書き込みと読み出しをテストするための文字列
TEST_STRING = "Hello MMJ"
# ----------------

# Flashメモリのクラスをインスタンス化
Flash = MT25QL01GBBB.flash()

print("--- 外部フラッシュメモリの書き込み・読み出しテストを開始します ---")

try:
    # 1. 消去 (Erase)
    # ----------------------------------------------------------------
    # Flashメモリは、書き込む前に該当領域を消去する必要があります。
    # ここではTEST_ADDRESSを含む4KBのサブセクタを消去します。
    print(f"1. アドレス {hex(TEST_ADDRESS)} を含む4KBサブセクタを消去します...")
    Flash.SUBSECTOR_4KB_ERASE_OF(TEST_ADDRESS)
    print("   -> 消去コマンドを送信しました。")
    # 消去処理には時間がかかるため、少し待機します。
    # (ライブラリ内でビジー状態をチェックしていますが、念のため)
    time.sleep(0.5) 
    print("   -> 消去完了。")

    # 2. 書き込み (Write)
    # ----------------------------------------------------------------
    # テスト文字列をバイトのリストに変換します。
    write_data = list(TEST_STRING.encode('utf-8'))
    
    print(f"\n2. アドレス {hex(TEST_ADDRESS)} にデータを書き込みます...")
    Flash.WRITE_DATA_BYTES_SMF(TEST_ADDRESS, write_data)
    print(f"   -> 書き込んだデータ: '{TEST_STRING}'")
    
    status = Flash.read_status_register()
    print(f"   -> 書き込み直後のステータスレジスタ値: {hex(status)} ({bin(status)})")

    print("   -> 書き込み完了。")
    time.sleep(0.1)

    # 3. 読み出し (Read)
    # ----------------------------------------------------------------
    print(f"\n3. アドレス {hex(TEST_ADDRESS)} からデータを読み出します...")
    
    print("   -> READ_DATA_BYTES_SMF関数を呼び出します...")
    # 書き込んだデータと同じ長さを読み出します。
    read_data_bytes = Flash.READ_DATA_BYTES_SMF(TEST_ADDRESS, len(write_data))
    print("   -> READ_DATA_BYTES_SMF関数から戻りました。")
    print(f"   -> 読み出した生のバイトデータ: {read_data_bytes}") # 取得した生データを表示
    
    # 読み出したバイトリストを文字列に変換します。
    read_string = ""
    if read_data_bytes:
        try:
            print("   -> バイトデータをUTF-8文字列にデコードします...")
            read_string = bytes(read_data_bytes).decode('utf-8')
            print("   -> デコード成功。")
        except UnicodeDecodeError:
            read_string = "（デコード不可能なバイナリデータ）"
            print("   -> デコード失敗。")

    print(f"   -> 読み出したデータ: '{read_string}'")
    print("   -> 読み出し完了。")
    
    # 4. 検証 (Verify)
    # ----------------------------------------------------------------
    print("\n4. データの検証を行います...")
    if TEST_STRING == read_string:
        print("   ✅ [成功] 書き込んだデータと読み出したデータが完全に一致しました！")
    else:
        print("   ❌ [失敗] データが一致しませんでした。")

except Exception as e:
    print(f"\nエラーが発生しました: {e}")
    print("SPIの接続や権限などを確認してください。")

finally:
    print("\n--- テストを終了します ---")