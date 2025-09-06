# 改善されたメモリダンプ表示コード
import MT25QL01GBBB_20231023 as MT25QL01GBBB

Flash = MT25QL01GBBB.flash()

keydata = input("input dump start address or shortcut key\n")

# アドレス設定
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

# アドレス決定
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
    readAddress = int(keydata)

# データ読み込み
data = Flash.READ_DATA_BYTES2_SMF(readAddress, 4096)

# ヘッダーの表示
print(f"Dumping data starting from address: {hex(readAddress)}")
print("      ", end="")
for i in range(16):
    print(f"{hex(i)[2:].zfill(2)} ", end="")
print("  | ASCII Characters |")

# データの表示
for j in range(16):
    print(f"{hex(j)[2:].zfill(3)}:", end=" ")

    # 16進数データの表示
    for i in range(16):
        print(f"{hex(data[i + j * 16])[2:].zfill(2)} ", end="")

    # ASCII文字の表示
    ascii_str = ""
    for i in range(16):
        byte = data[i + j * 16]
        if 32 <= byte <= 126:
            ascii_str += chr(byte)
        else:
            ascii_str += "."

    print(f" | {ascii_str}")

print("\nDump completed.")
