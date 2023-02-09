# -*- coding: utf-8 -*-

__author__  = "nishiyama"
__version__ = "1.0.0"
__date__    = "2020.3.11"

import os
import sys
import threading
import time
import queue
from datetime import datetime

import numpy as np
import cv2
from PyQt5 import QtCore, QtGui, uic, QtWidgets

from tritonclient.utils import *
# import tritonclient.grpc as grpcclient
import tritonclient.http as httpclient

from pear_imaging.bfs_controller import BFSCtrl
from pear_imaging import sercom as sc
from pear_imaging.enums import CameraId, OpCode, RxIndex, TableRot
from pear_imaging.widgets.image_widget import ImageWidget

form_class = uic.loadUiType("pear_imaging/app.ui")[0]
running = False
capture_thread = None
q = queue.Queue()
bfs_ctrl = BFSCtrl()
available_serial_list = []

TIMEOUT_LIMIT = 8000


def labeling(image, coordinates):
    """
    ラベルをつける対象の画像に対して，バウンディングボックスの作成及びラベルの文字付与を行う
    Args:
        image(ndarray): 対象の画像
        coordinates(Coordinate): バウンディングボックスのオブジェクト
        class_index(int): 対象領域の汚損要因のクラスインデックス
    Returns:
        labeled_image(ndarray): 対象画像にバウンディングﾎボックス及びラベルをつけた後の画像
    """
    # ラベル付けの対象位置を定義
    upper_left = (int(coordinates[0]), int(coordinates[1]))
    under_right = (int(coordinates[2]), int(coordinates[3]))

    # ラベル付け対象の位置にバウンディングボックスを生成
    labeled_image = cv2.rectangle(image, upper_left, under_right, (255, 255, 255))
    # バウンディングボックスに対してラベルの文字を付与
    labeled_image = cv2.putText(
        labeled_image,
        str(coordinates[4]),
        (int(coordinates[0]), int(coordinates[1] - 5)),
        cv2.FONT_HERSHEY_COMPLEX,
        0.7,
        (0, 0, 0),
        1
    )
    return labeled_image

class MainWindow(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.inc_pear_no_btn.clicked.connect(self.increase_pear_no)
        self.dec_pear_no_btn.clicked.connect(self.decrease_pear_no)
       
        # self.apply_motor_btn.clicked.connect(lambda: self.move_turntable(-1))
        self.zhome_btn.clicked.connect(lambda: self.move_turntable(TableRot.ZHOME))

        self.save_img_btn.clicked.connect(self.evaluate)

        self.widget_shape = [self.img_window.frameSize().height(),
                             self.img_window.frameSize().width()]
        self.img_window    = ImageWidget(self.img_window)
        self.__set_image(self.__blank_rgb_image(self.widget_shape), self.img_window, self.widget_shape)
        
        self.current_pear_no = 1
        self.current_pear_rot = 0

        self.frame_buff = None

        self.dst_parent_dir = "./output"
        if not os.path.isdir(self.dst_parent_dir):
            os.mkdir(self.dst_parent_dir)
        
        self.ser = sc.SerCom("COM3", "115200")
        self.rx_data = []
        self.timeout = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1) # 1ms間隔

        self.__start()

    def __blank_rgb_image(self, shape):
        height, width = shape
        return np.zeros((height, width, 3), dtype=np.uint8)
    
    def __start(self):
        global running
        running = True

        if not bfs_ctrl.detect_devices():
            print("Error: device could not be detected")
            bfs_ctrl.release_devices()
            self.close()

            sys.exit(1)

        print("Detected number of device: %d" % bfs_ctrl.get_num_device())

        global available_serial_list
        available_serial_list = bfs_ctrl.get_serial_list()
        if not bfs_ctrl.configure_custom_settings("ini/device_config.ini", \
                                                  "utf8", suppress_msg=False):
            # print(a)
            print("Error: failed to set custom image settings")
            print("Please reconnect the devices")
            bfs_ctrl.release_devices()
            self.close()

            sys.exit(1)
        print("OK!!")
        
        self.save_img_btn.setEnabled(True)

        self.pear_no_label.setText("{0:02d}".format(self.current_pear_no))
        
        bfs_ctrl.start_device(CameraId.SIDE)
        capture_thread.start()
        led_patt = 3 # self.__get_current_led_pattern()
        pkt = [OpCode.LED_ON, led_patt, 255]
        self.ser.send_pkt(pkt)

        self.zhome_btn.setEnabled(False)
        self.__msg_listener()
        self.set_led()
        self.move_turntable(TableRot.ZHOME)
     
        print("[PC] Start")
    
    def increase_pear_no(self):
        self.current_pear_no += 1
        if self.current_pear_no > 99:
            self.current_pear_no = 1
        self.pear_no_label.setText("{0:02d}".format(self.current_pear_no))

    def decrease_pear_no(self):
        self.current_pear_no -= 1
        if self.current_pear_no < 1:
            self.current_pear_no = 99
        self.pear_no_label.setText("{0:02d}".format(self.current_pear_no))

    def set_led(self):
        led_patt = 3 # self.__get_current_led_pattern()
        pkt = [OpCode.LED_ON, led_patt, 0]
        print('sfasfa')
        self.ser.send_pkt(pkt)

    def move_turntable(self, opdata=-1):
        if opdata == -1:
            opdata = self.opdata_combobox.currentIndex()
        print(self.__check_ready())
        # print(opdata)
        if self.__check_ready():
            pkt = [OpCode.MV_MOTOR, opdata, 0]
            # print(f'pkt {pkt}')
            self.ser.send_pkt(pkt)
                    
            if opdata == TableRot.ZHOME:
                self.current_pear_rot = 0
            else:
                self.current_pear_rot += TableRot.DEG_PER_120   
            
            self.turntable_rot_label.setText(str(self.current_pear_rot))
            #self.print_message("Table rotation: {0:4d}[deg]".format(self.current_pear_rot))

            if self.current_pear_rot == 0:
                self.zhome_btn.setEnabled(False)
            else:
                self.zhome_btn.setEnabled(True)

    def evaluate(self):
        """ 現在の画像を保存 """
        global running
        global available_serial_list
        number_pictures = 3
        if running:
            dst_dir_path = os.path.join(self.dst_parent_dir, "Pear{:02d}".format(self.current_pear_no))
            # async_responses = []
            file_names = []
            # client = httpclient.InferenceServerClient("133.35.129.10:8000")
            for index in range(number_pictures):

                fname = "Pear{0:02d}-{1}.png".format(self.current_pear_no, str(index))
                file_names.append(fname)
                if not os.path.isdir(dst_dir_path):
                    os.mkdir(dst_dir_path)
                    os.mkdir(dst_dir_path + '/result/')
                dst_file_path = os.path.join(dst_dir_path, fname)
                image = bfs_ctrl.grab(CameraId.SIDE)
                # image = image[700:, 700:1800]
                cv2.imwrite(dst_file_path, image)
                self.move_turntable(TableRot.DEG_PER_120)
                # inputs = [
                #     httpclient.InferInput("IMAGE", image.shape,
                #                         np_to_triton_dtype(image.dtype)),
                # ]

                # inputs[0].set_data_from_numpy(image)

                # outputs = [
                #     httpclient.InferRequestedOutput("SEGMENTATION_RESULT"),
                #     httpclient.InferRequestedOutput("DETECTION_RESULT"),
                # ]

                # async_responses.append(
                #     client.async_infer(
                #         model_name='pear_evaluator',
                #         inputs=inputs,
                #         outputs=outputs
                #     )
                # )
                # print(f'Inference {index} requested.')
                time.sleep(3)
                self.update()
            # # self.move_turntable(TableRot.DEG_PER_90)
            # for response, fname in zip(async_responses, file_names):
            #     result = response.get_result()
            #     coordinates = result.as_numpy("DETECTION_RESULT")

            #     for coordinate in coordinates:
            #         image = labeling(image, coordinate)
                
            #     dst_file_path = os.path.join(dst_dir_path + '/result/' , fname)
            #     print(dst_file_path)
            #     cv2.imwrite(dst_file_path, image)

            self.print_message('検査終了')
            self.print_message('検査結果は 青秀 です。')
            
    
    def print_message(self, msg):
        self.message_box.append("{0:%Y-%m-%d %H:%M:%S}: ".format(datetime.now()))
        self.message_box.append("  "+msg)

    def update(self):
        global available_serial_list

        # フレーム更新
        if not q.empty():
            frame = q.get()
            
            if CameraId.SIDE in available_serial_list:
                self.frame_buff = frame["Side"]
                self.__set_image(self.frame_buff, self.img_window, self.widget_shape)
            
            #q.task_done()  # フレームの更新が完了したことをキューに知らせる

        # RXデータの更新
        self.__msg_listener()
    
    def __msg_listener(self):
        if running and self.timeout > TIMEOUT_LIMIT:
            print("System Timeout.")
            self.close()
        rx_tmp = self.ser.recv()
        if rx_tmp == b'':
            self.rx_data = []
            self.timeout += 1
        else:
            self.rx_data = [1 if (int.from_bytes(rx_tmp, "big") & 2**i)>0 else 0 for i in range(8)]
            # モータのステータス更新
            #self.__status_monitor()

            self.timeout = 0

    def __check_ready(self):
        return True if self.rx_data[RxIndex.READY] else False

    def __set_image(self, src_img, img_widget, widget_shape):
        if self.__is_gray_image(src_img):
            img_height, img_width = src_img.shape
            img_format = QtGui.QImage.Format_Grayscale8
        else:
            img_height, img_width, __ = src_img.shape
            img_format = QtGui.QImage.Format_RGB888

        widget_height, widget_width = widget_shape

        scale_w = float(widget_width) / float(img_width)
        scale_h = float(widget_height) / float(img_height)
        scale = min([scale_w, scale_h])
        if scale == 0:
            scale = 1

        processed_img = cv2.resize(src_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        if self.__is_gray_image(src_img):
            height, width = processed_img.shape
            bpl = width
        else:
            processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
            height, width, bpc = processed_img.shape
            bpl = bpc * width

        qimage = QtGui.QImage(processed_img.data, width, height, bpl, img_format)
        img_widget.setImage(qimage)

    def __is_gray_image(self, image):
        if len(image.shape) == 2:
            return True
        else:
            return False

def grabber(queue):
    
    global running
    global available_serial_list
    while running:
        #q.join()  # アプリ側のフレーム更新メソッドが完了するまで待機
        frame = {}
        if CameraId.SIDE in available_serial_list:
            frame["Side"] = bfs_ctrl.grab(CameraId.SIDE)

        if queue.qsize() < 10:
            queue.put(frame)
        else:
            # print(queue.qsize())
            pass

if __name__ == "__main__":
    capture_thread = threading.Thread(target=grabber, args=(q,))
    try:
        app = QtWidgets.QApplication(sys.argv)
        w = MainWindow(None)
        w.setWindowTitle("Pear Imaging System")
        w.show()
        app.exec_()

        # 後始末
        del capture_thread
        bfs_ctrl.release_devices()
    except Exception:
        del capture_thread
        bfs_ctrl.release_devices()
        sys.exit()
