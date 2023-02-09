# -*- coding: utf-8 -*-
""" シリアル通信 """

import queue
import threading
import serial

class SerCom:

    def __init__(self, tty, baud="115200", rx_buff_len=1):
        self.ser = serial.Serial(tty, baud, timeout=0.1)
        self.queue = queue.Queue()
        self.rx_buff_len = rx_buff_len

        self.event = threading.Event()
        self.thread_r = threading.Thread(target=self.recv_)
        self.thread_r.start()
        self.rx_buff_ = []

    def recv_(self):
        while not self.event.is_set():
            self.rx_buff_ = self.ser.read(self.rx_buff_len)

    def recv(self):
        return self.rx_buff_

    def send_data(self, data):
        self.ser.write(data.to_bytes(1, "big"))

    def send_pkt(self, pkt):
        for data in pkt:
            self.send_data(data)

    def stop(self):
        self.event.set()
        self.thread_r.join()
