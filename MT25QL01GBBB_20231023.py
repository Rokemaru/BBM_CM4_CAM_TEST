# MT25QL01GBBB.py
# 2021.08 Daigo Tanaka, Misaki Hayashi
# This code is for testing(Writing and Reading data) Micron's SPI Flash memory, on the BIRDS OBC board.
# Changelog
# 2021/11/10 多バイト読み込み用関数[READ_DATA_BYTES_SMF]と多バイト書き込み用関数[WRITE_DATA_BYTES_SMF]



# -*- coding: utf-8 -*-
import sys
import struct
import os
import collections
import random
import binascii
import RPi.GPIO as GPIO
from time import sleep
import datetime
import spidev
import time
from array import array

from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN



class flash:
    #Vref = 3.3
    #ADRANGE = 4096
    # ※変数は使う順番で入れると、エラーが起こりにくい(それで1ヶ月近く作業が止まってた)
    # def __init__(self,CSB=1,baud=900000,bus=0)

    READ_ID = 0x9F
    READ_STATUS_REG = 0x05

    # define READ_ID              0x9F
    READ_STATUS_REG = 0x05
    READ_DATA_BYTES = 0x13  # 0x03 for byte
    ENABLE_WRITE = 0x06
    WRITE_PAGE = 0x12  # 0x02 for 3byte
    ERASE_SECTOR = 0xDC  # 0xD8 for 3byte
    ERASE_4KB_SUBSECTOR = 0x21
    ERASE_32KB_SUBSECTOR = 0x5C
    DIE_ERASE = 0xC4
    
    SUBSECTOR_SIZE_OF_4KB = 4096
    SUBSECTOR_SIZE_OF_32KB = 0x8000
    SECTOR_SIZE = 0x10000
    DATA_BUFFER_SIZE = 256

    def __init__(self, bus=0, CSB=0, baud=1000000):
        self.h = spidev.SpiDev()
        self.h.open(bus, CSB)
        # 1MHz
        self.h.max_speed_hz = baud
        self.h.mode = 0

    def __del__(self):
        try:
            self.spi.close()
        except:
            pass


    # SMFから1バイト読み込む
    def READ_DATA_BYTE_SMF(self, sector_address):
        #print("-------- read SMF START --------")
        cmd = [0x13]
        packet = cmd
        # 読み込みアドレスを格納
        data = (sector_address >> 24) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 16) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 8) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = 0xff & sector_address
        #packet = b""
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata
        # 読み込むバイト数を定義
        packet = packet + [0x00]
        # 生成したパケットをもとにSMFからデータを読み込む
        rcvdata = self.h.xfer2(packet)

        #print("-------- read SMF complete --------")
        return rcvdata[5]

    # SMFから多バイト読み込む
    def READ_DATA_BYTES_SMF(self, sector_address, amount):
        #print("-------- read SMF START --------")
        cmd = [0x13]
        packet = cmd
        # 読み込みアドレスを格納
        data = (sector_address >> 24) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 16) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 8) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = 0xff & sector_address
        #packet = b""
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata
        # 読み込むバイト数を定義
        #for i in range(int(amount)):
        
        packet = packet + [0x00] * amount
        # 生成したパケットをもとにSMFからデータを読み込む
        rcvdata = self.h.xfer2(packet)

        #print("-------- read SMF complete --------")
        #return rcvdata[amount]
        return rcvdata[5:]

    def READ_DATA_BYTES2_SMF(self, sector_address, amount):
        #print("-------- read SMF START --------")
        cmd = [0x13]
        packet = cmd
        # 読み込みアドレスを格納
        data = (sector_address >> 24) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 16) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 8) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = 0xff & sector_address
        #packet = b""
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata
        # 読み込むバイト数を定義
        #for i in range(int(amount)):
        
        packet = packet + [0x00] * amount
        # 生成したパケットをもとにSMFからデータを読み込む
        rcvdata = self.h.xfer3(packet)

        #print("-------- read SMF complete --------")
        #return rcvdata[amount]
        return rcvdata[5:]








    # veryfication confirmed on 22th Sep.

    def read_chip_id(self):
        #cmd = [0x9F,0x00]
        cmd = [0x9F, 0] + [255 for _ in range(19)]
        chip_id = self.h.xfer2(cmd)[1:]
        time.sleep(0.01)
        print('0x{:x}'.format(chip_id[0]))
        print('0x{:x}'.format(chip_id[1]))
        print("CHIP ID >>>", '0x{:x}'.format(chip_id[0]))
        return chip_id

    # veryfication confirmed on 22th Sep.

    # Funcion que borra un sector de 4KB de la Main Flash
    def SUBSECTOR_4KB_ERASE_OF(self, sector_address):
        # Recibe la direccion del sector que se quiere borrar

        cmd = [self.ERASE_4KB_SUBSECTOR]

        packet = cmd
        # 読み込みアドレスを格納
        data = (sector_address >> 24) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 16) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 8) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = 0xff & sector_address
        #packet = b""
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        packet = packet

        self.WRITE_ENABLE_OF()  # Funcion que habilita escritura en Own Flash

        # ///////////////////////////////////////////////////////////////////
        rcvdata = self.h.xfer2(packet)
        # //////////////////////////////////////////////////////////////////
        time.sleep(0.02)
        while self.read_status_register() & 0x01 == 1:
            time.sleep(0.01)
            print("erase")
            
        return

    def SUBSECTOR_32KB_ERASE_OF(self, sector_address):
        # Recibe la direccion del sector que se quiere borrar

        cmd = [self.ERASE_32KB_SUBSECTOR]

        packet = cmd
        # 読み込みアドレスを格納
        data = (sector_address >> 24) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 16) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 8) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = 0xff & sector_address
        #packet = b""
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        packet = packet

        self.WRITE_ENABLE_OF()  # Funcion que habilita escritura en Own Flash

        # ///////////////////////////////////////////////////////////////////
        rcvdata = self.h.xfer2(packet)
        # //////////////////////////////////////////////////////////////////
        time.sleep(0.01)
        while self.read_status_register() & 0x01 == 1:
            time.sleep(0.005)
        return
    #added 21th April 2022
    def SECTOR_ERASE(self, sector_address):
        # Recibe la direccion del sector que se quiere borrar

        cmd = [self.ERASE_SECTOR]

        packet = cmd
        # 読み込みアドレスを格納
        data = (sector_address >> 24) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 16) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (sector_address >> 8) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = 0xff & sector_address
        #packet = b""
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        packet = packet

        self.WRITE_ENABLE_OF()  # Funcion que habilita escritura en Own Flash

        # ///////////////////////////////////////////////////////////////////
        rcvdata = self.h.xfer2(packet)
        # //////////////////////////////////////////////////////////////////
        time.sleep(0.1)
        while self.read_status_register() & 0x01 == 1:
            time.sleep(0.05)
        return
    
    
    def WRITE_ENABLE_OF(self):
        # /////////////////////////////////////////////////////////////
        # //delay_ms(2);
        packet = [self.ENABLE_WRITE]
        self.h.xfer2(packet)  # //Send 0x06
        # /////////////////////////////////////////////////////////////

        return

    # //Funcion que escribe un Byte en la Mission Flash
    # SMFに1バイト書き込む
    
    # [memo 11/10 20:06 h.m]read_data_bytes_smfは、packetの生成は出来てるっぽいけど、肝心の受信がうまく行かない
    #may be max 256 due to data buffer size in flash
    def WRITE_DATA_BYTE_SMF(self, address, write_data):
        cmd = [self.WRITE_PAGE]
        packet = cmd

        data = (address >> 24) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (address >> 16) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (address >> 8) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = 0xff & address
        #packet = b""
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata
        # 書き込むバイト数を定義
        packet = packet + [write_data]
        # SMFに書き込み
        self.WRITE_ENABLE_OF()
        sleep(0.00001)

        # ////////////////////////////////////////////////////////////////

        self.h.xfer2(packet)
        # ////////////////////////////////////////////////////////////////
        time.sleep(0.0001)        
        while self.read_status_register() & 0x01 == 1:
            time.sleep(0.0001)

        return

    # SMFに多バイト書き込む
    #page_address = page address,  write_date is list
    def WRITE_DATA_BYTES_SMF(self, address, write_data):
        cmd = self.WRITE_PAGE
        packet = [cmd]

        data = (address >> 24) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (address >> 16) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = (address >> 8) & 0xff
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata

        data = 0xff & address
        #packet = b""
        hexdata = (b'' + data.to_bytes(1, 'big'))
        packet += hexdata
        # 書き込むバイト数を定義
        #for j in write_data:
        #    packet = packet + [j]
        packet = packet + write_data
        #print ("write start")            
        # SMFに書き込み
        self.WRITE_ENABLE_OF()
        sleep(0.0000001)
        #print(packet[-1])
        # ////////////////////////////////////////////////////////////////

        self.h.writebytes2(packet)
        # ////////////////////////////////////////////////////////////////

        time.sleep(0.0001)
        while self.read_status_register() & 0x01 == 1:
            time.sleep(0.0001)
        return


    #bit7 Status register write enable/disable
    #bit5 top/ bottom 0=top(default), 1= bottom
    #bit6,4:2 see protected area tables
    #bit1 write enableLatch 0 = clear (default) 1 = set
    #bit0 write inprogress 0=ready, 1 = busy
    def read_status_register(self):
        cmd = self.READ_STATUS_REG
        packet = [cmd,0x00]        
        rcvdata = self.h.xfer2(packet)
        #print("Status register: " + str(rcvdata[1]))
        if rcvdata[1] & 0x01 == 1 :
            print("busy")
        
        
        
        return rcvdata[1]


if __name__ == '__main__':

    Flash = flash()

    pjname = ['i', 'g', 'o', 'm', 'o', 'y']
    charData = 'yomogi'


    try:
        while True:

            print("input command")
            keydata = input()

            if keydata == 'c':
                print("Chip ID")
                sleep(1)
                data = Flash.read_chip_id()
                print(data)
            
            elif keydata == 'r':

                print("read Start")
                sleep(1)
                for i in range(6):
                    data = Flash.READ_DATA_BYTE_SMF(i)
                    print(data)
                 #  print(chr(data))
            elif keydata == 'e':

                Flash.SUBSECTOR_4KB_ERASE_OF(0)
                #data = Flash.READ_DATA_BYTE_SMF(0,6)
                sleep(1)

            elif keydata == 'w':

                print("write start")
                counter = 0
                for w in pjname:
                    Flash.WRITE_DATA_BYTE_SMF(counter, ord(w))
                    counter += 1

            elif keydata == 'b':
                print("read Start")
                sleep(1)
                for i in range(3):
                    data = Flash.READ_DATA_BYTE_SMF(i)
                    print(data)
            # 多バイト一括読み込みテスト
            elif keydata == 't':
                print("How many bytes will you want to read?")
                keydata = input()
                keynum = int(keydata)
                print(type(keynum))
                sleep(1)
                data = Flash.READ_DATA_BYTES_SMF(0, keynum)
                result_list = list(data)
                encoded_list = list()
                for i in result_list:
                    encoded_list = encoded_list + [chr(i)]
                print(encoded_list)
            # 多バイト一括書き込みテスト 
            elif keydata == 'y':
                sleep(1)
                packet = []
                for i in pjname:
                    packet = packet + [ord(i)]
                
                Flash.WRITE_DATA_BYTES_SMF(0, packet)
                #print(data)
    except KeyboardInterrupt:
        pass

    GPIO.cleanup()
