import gpiod
import time

# --- 設定 ---
CHIP_NAME = "gpiochip4"
PIN_NUM = 7

print("GPIOアクセステストを開始します...【旧ライブラリ対応版】")
print(f"使用チップ: {CHIP_NAME}, 対象ピン: GPIO{PIN_NUM}")

try:
    with gpiod.Chip(CHIP_NAME) as chip:
        line = chip.get_line(PIN_NUM)
        print(f"GPIO{PIN_NUM}の制御権をOSに要求します...")

        # ▼▼▼【原因箇所を修正】▼▼▼
        # 古いgpiodライブラリの書き方に修正しました
        line.request(
            consumer="gpio_access_test",
            type=gpiod.LINE_REQ_DIR_IN  # gpiod.LineReq.INPUT から変更
        )
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

        print(">>> 成功: GPIOピンの確保が完了しました！")
        print("ピンは正常に汎用モードとして使用可能です。")
        value = line.get_value()
        print(f"現在のピンの状態: {'HIGH' if value == 1 else 'LOW'}")

except OSError as e:
    if e.errno == 16:
        print("\n>>> 失敗: やはり 'Device or resource busy' エラーが発生しました。")
        print("    エラーコード: [Errno 16]")
        print("    これは、OSまたはカーネルがこのピンを確保していることを強く示唆します。")
    else:
        print(f"\n>>> 予期せぬOSエラーが発生しました: {e}")
except Exception as e:
    print(f"\n>>> 不明なエラーが発生しました: {e}")

finally:
    print("\nテストプログラムを終了します。")