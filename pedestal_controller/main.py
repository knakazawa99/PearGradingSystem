#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys
import serial
import time
import sercom as sc
import led_ctrl
import motor_ctrl
from enum import IntEnum

class OpCode(IntEnum):
    SYS_EXIT = 0
    SET_BRT  = 1
    LED_ON   = 2
    MV_MOTOR = 3

class RpiRes(IntEnum):
    NAK = 0
    ACK = 1
    ERR = 2


DEV_NAME = "/dev/serial0" # ポート名
BOUDRATE = "115200" # ボーレート

def mask_send_msg(rpi_res, motor_stat):

    bits = [0 for i in range(8)]

    bits[0] = 1 if (rpi_res&1)>0 else 0
    bits[1] = 1 if (rpi_res&2)>0 else 0

    for e in motor_ctrl.Stat:
        bits[2+e.value] = motor_stat[e.value]

    byte = 0
    for i in range(8):
        byte |= bits[i]*(2**(i))

    return byte

"""
def compress_list_to_1byte(data_list):
    # リストデータを1バイトの数値データに圧縮
    # 先頭から8ビット分を取り出す
    bits = data_list[:8]

    # 不足しているビットを0埋め
    data_len = len(data_list)
    if data_len < 8:
        bits.extend([0 for i in range(8-data_len)])

    byte = 0
    for i in range(8):
        byte |= bits[i]*(2**(i))

    return byte
"""

def main():
    """ メイン処理 """

    ser = sc.SerCom(DEV_NAME, BOUDRATE, 3)
    l_ctrl = led_ctrl.LEDCtrl()
    m_ctrl = motor_ctrl.MotorCtrl()

    try:
        print("[RPi] System Start.")

        while True:
            rx_data = ser.recv()


            if len(rx_data) == 3:
                opcode = rx_data[0]
                data1  = rx_data[1]
                data2  = rx_data[2]

                if opcode == OpCode.SYS_EXIT:
                    print("[RPi] System Exit.")
                    l_ctrl.turn_off_led()

                    ser.stop()

                    sys.exit(0)

                elif opcode == OpCode.SET_BRT:
                    is_set = l_ctrl.set_brightness(data1, data2)

                    if not is_set:
                        print("[RPi] Cannot set brightness.")

                        ser.stop()
                        sys.exit(1)

                    # ACKを送信する
                    msg = mask_send_msg(RpiRes.ACK, m_ctrl.get_status())
                    ser.send_data(msg)

                elif opcode == OpCode.LED_ON:
                    l_ctrl.turn_on_led(data1)

                    # ACKを送信する
                    msg = mask_send_msg(RpiRes.ACK, m_ctrl.get_status())
                    ser.send_data(msg)

                elif opcode == OpCode.MV_MOTOR:
                    if m_ctrl.is_ready():
                        m_ctrl.operate_motor(data1)

                        #while not m_ctrl.is_in_pos():
                        while not m_ctrl.is_ready():
                            # NAKを送信する
                            msg = mask_send_msg(RpiRes.NAK, m_ctrl.get_status())
                            ser.send_data(msg)

                        # ACKを送信する
                        msg = mask_send_msg(RpiRes.ACK, m_ctrl.get_status())
                        ser.send_data(msg)
                    else:
                        m_ctrl.reset_input_signals()

                else:
                    # ERRを送信する
                    msg = mask_send_msg(RpiRes.ERR, m_ctrl.get_status())
                    ser.send_data(msg)

            else:
                # NAKを送信する
                msg = mask_send_msg(RpiRes.NAK, m_ctrl.get_status())
                ser.send_data(msg)

    except KeyboardInterrupt:
        print("\n[RPi] KB Interrupted!")
        l_ctrl.turn_off_led()

        # ERRを送信する
        msg = mask_send_msg(RpiRes.ERR, m_ctrl.get_status())
        ser.send_data(msg)
        ser.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()


