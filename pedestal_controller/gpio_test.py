#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys
import time
import pigpio

brtwr_pin = 10

# pigpioモジュールでGPIO制御するには
# デーモン(pigpiod)を起動させておく必要がある
pi = pigpio.pi()
pi.set_mode(brtwr_pin, pigpio.OUTPUT)

# 信号
SIG_LOW  = 0
SIG_HIGH = 1

#usleep = lambda x: time.sleep(x/1000000.0)

def usleep(delay):
    start = time.time()

    while (time.time()-start) < delay/1000000.0:
        continue


def write_test():
    usleep(500)
    pi.write(brtwr_pin, 1)

def main():

    #pi.set_PWM_frequency(brtwr_pin, 2000)
    #pi.set_PWM_range(brtwr_pin, 100)

    pi.write(brtwr_pin, SIG_LOW)
    try:
        while True:
            #pi.hardware_PWM(brtwr_pin, 800, 250000)
            #pi.set_servo_pulsewidth(brtwr_pin, 500)
            #pi.set_PWM_dutycycle(brtwr_pin, 50)
            #usleep(200)
            #usleep(500)
            #pi.gpio_trigger(brtwr_pin, 10, 1)

            #usleep(500)
            #pass
            """
            pi.set_PWM_frequency(brtwr_pin, 4000)
            pi.set_PWM_range(brtwr_pin, 100)
            pi.set_PWM_dutycycle(brtwr_pin, 0)
            usleep(100)
            pi.set_PWM_dutycycle(brtwr_pin, 100)
            """
            usleep(1000)
            pi.write(brtwr_pin, 1)
            usleep(50)
            pi.write(brtwr_pin, 0)


    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()


