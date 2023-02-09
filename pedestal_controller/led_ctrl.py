#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pigpio
import smbus
import sys
import time

class LEDCtrl:
    """ LED照明のコントローラクラス

        PD3への入力信号はシンクタイプを想定
        トリガー論理スイッチはLOW

        入力信号 | フォトカプラ | データ
        -------+------------+-------
         HIGH  |     OFF    |   1
         LOW   |     ON     |   0
    """

    # Constants for smbus
    REG_IODIRA_ = 0x00 # GPAの入出力設定レジスタ
    REG_IODIRB_ = 0x01 # GPBの入出力設定レジスタ
    REG_OLATA_  = 0x14 # GPAの出力レジスタ
    REG_OLATB_  = 0x15 # GPBの出力レジスタ

    # 信号
    SIG_LOW  = 0
    SIG_HIGH = 1

    usleep = lambda self, x: time.sleep(x/1000000.0)

    def __init__(self, brtwr_pin=10, chsel0_pin=9, chsel1_pin=11,
                 chsel2_pin=19, i2c_alloc_ch=1, mcp32017_addr=0x20):

        # Constants for pigpio
        # GPIO No. of RasPi
        self.brtwr_pin = brtwr_pin
        self.chsel0_pin = chsel0_pin
        self.chsel1_pin = chsel1_pin
        self.chsel2_pin = chsel2_pin
        self.mcp32017_addr = mcp32017_addr

        # pigpioモジュールでGPIO制御するには
        # デーモン(pigpiod)を起動させておく必要がある
        self.pi = pigpio.pi()
        self.pi.set_mode(self.brtwr_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.chsel0_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.chsel1_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.chsel2_pin, pigpio.OUTPUT)

        # ピンの入出力設定
        self.bus = smbus.SMBus(i2c_alloc_ch)
        self.bus.write_byte_data(self.mcp32017_addr, self.REG_IODIRA_, 0x00)
        self.bus.write_byte_data(self.mcp32017_addr, self.REG_IODIRB_, 0x00)

    def set_brightness(self, ch, brt_val):
        """ 選択したチャネルに調光データを設定する
            ch: 1-8
        """

        if not (1 <= ch <= 8):
            print("Invalid channel")
            return False

        # チャネル選択に関する信号を出力
        self.write_chsel_signal(ch)

        # 調光データの上限を0xff(=255)にする
        if brt_val > 0xff:
            brt_val = 0xff

        # 調光データに該当する信号を出力
        self.bus.write_byte_data(self.mcp32017_addr,
                                 self.REG_OLATA_,
                                 0xff-self.reversebits(brt_val))
        # 書込信号を出力
        self.pi.gpio_trigger(self.brtwr_pin, 100, self.SIG_LOW)

        return True

    def write_chsel_signal(self, ch):
        """ チャネル選択信号を出力する
        """

        chsel_sig = [self.SIG_LOW if (ch-1)&2**i>0 \
                     else self.SIG_HIGH for i in range(3)]

        self.pi.write(self.chsel0_pin, chsel_sig[0])
        self.pi.write(self.chsel1_pin, chsel_sig[1])
        self.pi.write(self.chsel2_pin, chsel_sig[2])

    def write_brtwr_signal(self, fall_time_us=50):
        """ 調光値書込みトリガを出力する
            立ち下がり時間 50us以上
        """

        self.pi.write(self.brtwr_pin, self.SIG_LOW)
        self.usleep(fall_time_us)
        self.pi.write(self.brtwr_pin, self.SIG_HIGH)

    def reversebits(self, x):
        """ ビットオーダーを反転させる
            ex. 01010101 -> 10101010
        """

        x = (x & 0x0F) << 4 | (x & 0xF0) >> 4
        x = (x & 0x33) << 2 | (x & 0xCC) >> 2
        x = (x & 0x55) << 1 | (x & 0xAA) >> 1

        return x

    def turn_on_led(self, ch_patt):
        """ LEDを点灯させる """

        # 点灯制御信号を出力
        self.bus.write_byte_data(self.mcp32017_addr,
                                 self.REG_OLATB_, ch_patt)

    def turn_off_led(self):
        """ LEDを消灯させる """

        # 点灯制御信号を出力
        self.bus.write_byte_data(self.mcp32017_addr,
                                 self.REG_OLATB_, 0x00)
