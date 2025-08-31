import RPi.GPIO as GPIO  # RPi.GPIOライブラリをGPIOとしてインポート
import time              # timeライブラリをインポート

# 使用するGPIOピンの番号を指定
LED_PIN = 7

# GPIOのピン番号の指定方法をBCM（GPIO番号）に設定
GPIO.setmode(GPIO.BCM)

# 指定したピンを出力モードに設定
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    # 無限ループ
    while True:
        print("LED ON")
        # LED_PINから信号を出力（HIGH = 3.3V）してLEDを点灯
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(1)  # 1秒間待つ

        print("LED OFF")
        # LED_PINからの出力を停止（LOW = 0V）してLEDを消灯
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(1)  # 1秒間待つ

# Ctrl+Cキーが押されたら終了処理を実行
except KeyboardInterrupt:
    print("Stopping.")

# 最後にGPIOの設定をクリーンアップ
finally:
    GPIO.cleanup()