# check_status.py
import MT25QL01GBBB_20231023 as MT25QL01GBBB
import time

# Flashメモリのクラスをインスタンス化
Flash = MT25QL01GBBB.flash()

print("--- 外部フラッシュメモリの現在のステータスを監視します ---")
print("Ctrl+Cで終了します。")

try:
    while True:
        # ステータスレジスタを読み出す
        status = Flash.read_status_register()
        
        # 結果を16進数、2進数、10進数で表示
        # 2進数で表示することで、どのビットが立っているか一目瞭然になります
        print(f"現在のステータス: {hex(status)} ({bin(status)}, {status})")
        
        # 1秒待機
        time.sleep(1)

except KeyboardInterrupt:
    print("\n監視を終了します。")

finally:
    # __del__が呼ばれるようにインスタンスを削除
    del Flash
    print("--- 監視終了 ---")