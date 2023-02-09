#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys
import serial
import time
import sercom as sc
import led_ctrl
import motor_ctrl

DEV_NAME = "/dev/serial0" # ポート名
BOUDRATE = "9600" # ボーレート

def init_system():
    """ RasPi側のシステム初期化 """
    pass

def main():

    init_system()
    ser = sc.SerCom(DEV_NAME, BOUDRATE)
    l_ctrl = led_ctrl.LEDCtrl()
    #m_ctrl = motor_ctrl.MotorCtrl()

    i = 0

    try:
        for i in range(4):
            is_set = l_ctrl.set_brightness(i+1, 255)

        ser.stop()



    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()


