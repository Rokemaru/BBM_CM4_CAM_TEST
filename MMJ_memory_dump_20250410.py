import MT25QL01GBBB_20231023 as MT25QL01GBBB

Flash = MT25QL01GBBB.flash()

# 1. アドレスの入力
keydata = input("input dump start address or shortcut key\n")

# 2. 長さの入力
DEFAULT_DUMP_SIZE = 256  # デフォルトのダンプサイズ (バイト)
length_str = input(f"input dump length (hex or dec, default: {DEFAULT_DUMP_SIZE} bytes)\n")

# 3. 長さの決定
try:
    if length_str.startswith('0x') or length_str.startswith('0X'):
        readLength = int(length_str, 16) # 16進数として処理
    else:
        readLength = int(length_str) # 10進数として処理
except ValueError:
    if length_str == "":
        readLength = DEFAULT_DUMP_SIZE
    else:
        print(f"Invalid length. Using default {DEFAULT_DUMP_SIZE} bytes.")
        readLength = DEFAULT_DUMP_SIZE

# --- アドレス設定 ---
CORN_MSN_TMBHEAD_DATA_ADDRESS = 0x05B60000
CORN_MSN_TMB_DATA_ADDRESS = 0x05B61000
AURORA_MSN_TMBHEAD_DATA_ADDRESS = 0x06340000
AURORA_MSN_TMB_DATA_ADDRESS = 0x6341000
PUMICE_MSN_TMBHEAD_DATA_ADDRESS = 0x06699000
PUMICE_MSN_TMB_DATA_ADDRESS = 0x0669A000

CORN_MSN_HEAD_DATA_ADDRESS = 0x069F2000
CORN_MSN_DATA_ADDRESS = 0x069F3000
AURORA_MSN_HEAD_DATA_ADDRESS = 0x06D13000
AURORA_MSN_DATA_ADDRESS = 0x06D14000
PUMICE_MSN_HEAD_DATA_ADDRESS = 0x07034000
PUMICE_MSN_DATA_ADDRESS = 0x07035000

CHIBANY_PHOTO_COPY_SIZE = 0x00000000
CHIBANY_PHOTO_COPY = 0x00001000

# --- アドレス決定 ---
if keydata == 'a':
    readAddress = CORN_MSN_TMBHEAD_DATA_ADDRESS
elif keydata == 'b':
    readAddress = CORN_MSN_TMB_DATA_ADDRESS
elif keydata == 'k':
    readAddress = AURORA_MSN_TMBHEAD_DATA_ADDRESS
elif keydata == 'l':
    readAddress = AURORA_MSN_TMB_DATA_ADDRESS
elif keydata == 'm':
    readAddress = PUMICE_MSN_TMBHEAD_DATA_ADDRESS
elif keydata == 'n':
    readAddress = PUMICE_MSN_TMB_DATA_ADDRESS
elif keydata == 'e':
    readAddress = CORN_MSN_HEAD_DATA_ADDRESS
elif keydata == 'f':
    readAddress = CORN_MSN_DATA_ADDRESS
elif keydata == 's':
    readAddress = AURORA_MSN_HEAD_DATA_ADDRESS
elif keydata == 't':
    readAddress = AURORA_MSN_DATA_ADDRESS
elif keydata == 'x':
    readAddress = PUMICE_MSN_HEAD_DATA_ADDRESS
elif keydata == 'y':
    readAddress = PUMICE_MSN_DATA_ADDRESS
elif keydata == '0':
    readAddress = CHIBANY_PHOTO_COPY_SIZE
elif keydata == '1':
    readAddress = CHIBANY_PHOTO_COPY
else:
    try:
        readAddress = int(keydata , 16)
    except ValueError:
        print("Invalid address. Exiting.")
        exit()

# 4. データ読み込み (readLength を使用)
print(f"Reading {readLength} bytes from {hex(readAddress)}...")
try:
    data = Flash.READ_DATA_BYTES2_SMF(readAddress, readLength)
except Exception as e:
    print(f"Error reading flash memory: {e}")
    exit() # エラーが発生したら終了

# --- ヘッダーの表示 (オフセット表示を改善) ---
print(f"Dumping {readLength} bytes starting from address: {hex(readAddress)}")
print("Offset ", end="")
for i in range(16):
    print(f"{i:02X} ", end="") # f"{hex(i)[2:].zfill(2)} " と同じ意味
print(" | ASCII Characters |")
print("-" * 68) # 区切り線

# 5. データの表示 (readLength に基づいてループ)
num_rows = (readLength + 15) // 16 # 表示に必要な行数を計算 (切り上げ)

for j in range(num_rows):
    offset = j * 16
    print(f"{offset:04X}:", end=" ") # オフセットを4桁16進数で表示

    # 16進数データの表示
    hex_str = ""
    for i in range(16):
        current_index = offset + i
        if current_index < readLength:
            # データを f-string の :02X で2桁16進数に
            hex_str += f"{data[current_index]:02X} "
        else:
            hex_str += "   " # データの範囲外は空白
    print(hex_str, end="")

    # ASCII文字の表示
    ascii_str = ""
    for i in range(16):
        current_index = offset + i
        if current_index < readLength:
            byte = data[current_index]
            if 32 <= byte <= 126:
                ascii_str += chr(byte)
            else:
                ascii_str += "."
        else:
            ascii_str += " " # データの範囲外は空白

    print(f" | {ascii_str}")

print("\nDump completed.")
