#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pigpio
import sys
import time
from enum import IntEnum

class Stat(IntEnum):
    HOME_END = 0
    IN_POS   = 1
    READY    = 2
    MOVE     = 3
    ALM_B    = 4

class MotorCtrl:
    """ ステッピングモータのコントローラクラス
    """

    # 信号
    SIG_LOW  = 0
    SIG_HIGH = 1

    usleep = lambda self, x: time.sleep(x/1000000.0)

    def __init__(self, start_pin=26, m0_pin=13, m1_pin=6, m2_pin=5,
                 zhome_pin=22, free_pin=27, stop_pin=17, alm_rst_pin=4,
                 home_end_pin=7, in_pos_pin=12, ready_pin=16,
                 move_pin=20, alm_b_pin=21):

        # Constants for pigpio
        # GPIO No. of RasPi
        self.start_pin = start_pin
        self.m0_pin = m0_pin
        self.m1_pin = m1_pin
        self.m2_pin = m2_pin
        self.zhome_pin = zhome_pin
        self.free_pin = free_pin
        self.stop_pin = stop_pin
        self.alm_rst_pin = alm_rst_pin
        self.home_end_pin = home_end_pin
        self.in_pos_pin = in_pos_pin
        self.ready_pin = ready_pin
        self.move_pin = move_pin
        self.alm_b_pin = alm_b_pin

        # pigpioモジュールでGPIO制御するには
        # デーモン(pigpiod)を起動させておく必要がある
        self.pi = pigpio.pi()
        self.pi.set_mode(self.start_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.m0_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.m1_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.m2_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.zhome_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.free_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.stop_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.alm_rst_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.home_end_pin, pigpio.INPUT)
        self.pi.set_mode(self.in_pos_pin, pigpio.INPUT)
        self.pi.set_mode(self.ready_pin, pigpio.INPUT)
        self.pi.set_mode(self.move_pin, pigpio.INPUT)
        self.pi.set_mode(self.alm_b_pin, pigpio.INPUT)

        # 入力信号をOFF
        self.reset_input_signals()

    def get_status(self):
        return [self.pi.read(self.home_end_pin),
                self.pi.read(self.in_pos_pin),
                self.pi.read(self.ready_pin),
                self.pi.read(self.move_pin),
                self.pi.read(self.alm_b_pin)]

    def is_home_end(self):
        """ HOME-END 信号の状態を真偽値で返す """
        return (True if self.pi.read(self.home_end_pin) == self.SIG_HIGH \
                else False)

    def is_in_pos(self):
        """ IN-POS 信号の状態を真偽値で返す """
        return (True if self.pi.read(self.in_pos_pin) == self.SIG_HIGH \
                else False)

    def is_ready(self):
        """ READY 信号の状態を真偽値で返す """
        return (True if self.pi.read(self.ready_pin) == self.SIG_HIGH \
                else False)

    def is_move(self):
        """ MOVE 信号の状態を真偽値で返す """
        return (True if self.pi.read(self.move_pin) == self.SIG_HIGH \
                else False)

    def is_alm_b(self):
        """ MOVE 信号の状態を真偽値で返す """
        return (True if self.pi.read(self.alm_b_pin) == self.SIG_LOW \
                else False)

    def reset_input_signals(self):
        self.pi.write(self.start_pin, self.SIG_LOW)
        self.pi.write(self.m0_pin, self.SIG_LOW)
        self.pi.write(self.m1_pin, self.SIG_LOW)
        self.pi.write(self.m2_pin, self.SIG_LOW)
        self.pi.write(self.zhome_pin, self.SIG_LOW)
        self.pi.write(self.free_pin, self.SIG_LOW)
        self.pi.write(self.stop_pin, self.SIG_LOW)

    def operate_motor(self, opdata):
        """ 選択した運転データでモータを運転する
        """
        self.select_operation_data(opdata)

        self.write_trigger_signal(self.start_pin, fall_time_us=500)

    def select_operation_data(self, opdata):
        """ 運転データを設定する
            opdata: 0-7
        """

        if not (0 <= opdata <= 7):
            print("Invalid operation data")
            return False

        m_sig = [self.SIG_HIGH if opdata&2**i>0 \
                else self.SIG_LOW for i in range(3)]

        # 運転データ選択に関する信号を出力
        self.pi.write(self.m0_pin, m_sig[0])
        self.pi.write(self.m1_pin, m_sig[1])
        self.pi.write(self.m2_pin, m_sig[2])

        return True

    def write_trigger_signal(self, pin, fall_time_us=50):
        """ トリガ信号を出力する
            立ち下がり時間 ?[us]
        """

        self.pi.write(pin, self.SIG_HIGH)
        self.usleep(fall_time_us)
        self.pi.write(pin, self.SIG_LOW)


