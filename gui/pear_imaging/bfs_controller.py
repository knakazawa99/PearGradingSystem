# -*- coding: utf-8 -*-
"""
FLIR(R) Blackfly S を利用するためのモジュール
"""
__author__  = "nishiyama"
__version__ = "1.0.1"
__date__    = "2018.9.1"

import numpy as np
import configparser
from enum import Enum
import sys
import PySpin

class ChannelNumEnums(Enum):
    C1 = 1
    C3 = 3

class BFSCtrl:
    """
    FLIR(R) Blackfly S からの画像を
    ndarray形式で取得するためのコントローラを提供するクラス
    """
    def __init__(self):
        # システムオブジェクトを取得
        self.__system      = PySpin.System.GetInstance()
        self.__cam_list    = PySpin.CameraList()
        self.__cam_list.Clear()
        self.__cam_list    = PySpin.CameraList()
        self.__num_cameras = 0
        self.__camera_ref  = []
        self.__serial_list = []

    def detect_devices(self):
        # カメラリストを取得
        self.__cam_list = self.__system.GetCameras()
        self.__num_cameras = self.__cam_list.GetSize()

        if self.__num_cameras == 0:
            return False

        self.__camera_ref  = [None for i in range(self.__num_cameras)]
        self.__serial_list = ["" for i in range(self.__num_cameras)]

        self.__initialize()

        return True

    def __initialize(self):
        """
        認識したカメラを初期化する

        認識したカメラに接続し，XMLを取得してノードマップを生成する
        その後，カメラへの参照とシリアルナンバーをリストに格納する
        """
        for i in range(self.__num_cameras):
            cam = self.__cam_list.GetByIndex(i)
            cam.Init()
            self.__camera_ref[i] = cam
            self.__serial_list[i] = cam.DeviceSerialNumber.GetValue()

    def configure_custom_settings(self, ini_file, char_code, key=None, suppress_msg=False):
        """
        iniファイルから追加の設定を行う
        """
        try:
            config = configparser.ConfigParser()
            if not config.read(ini_file, char_code):
                raise NameError("INI file was not found")

            if key is None:
                for i in range(self.__num_cameras):
                    # print(f"camera {i}")
                    if not self.__configure_custom_settings(self.__camera_ref[i], config, suppress_msg):
                        return False
            else:
                idx = self.__key2index(key)
                if not self.__configure_custom_settings(self.__camera_ref[idx], config, suppress_msg):
                    return False

        except NameError as e:
            self.__exit_with_error_massage(e)
        except PySpin.SpinnakerException as e:
            self.__exit_with_error_massage(e)

        return True

    def __configure_custom_settings(self, cam, config, suppress_msg=False):
        """
        コンフィグファイルから追加の設定を行う
        """
        try:
            result = True

            if not suppress_msg:
                print("========================")
                print("Device ID: %s " % cam.DeviceSerialNumber.GetValue())
                print("------------------------")

            # Pixel Format
            pixel_format = config["PixelFormat"]
            format = pixel_format.get("format", "Mono8")
            if cam.PixelFormat.GetAccessMode() == PySpin.RW:
                if format == "Mono8":
                    cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono8)
                    self.__num_color_channel = 1
                elif format == "BGR8":
                    cam.PixelFormat.SetValue(PySpin.PixelFormat_BGR8)
                    self.__num_color_channel = 3
                elif format == "RGB8":
                    cam.PixelFormat.SetValue(PySpin.PixelFormat_RGB8)
                    self.__num_color_channel = 3
                else:
                    print("[PixelFormat]: Invalid value in \"format: %s\"." % format)
                    return False
                if not suppress_msg:
                    print("Pixel format set to %s..." % cam.PixelFormat.GetCurrentEntry().GetSymbolic())
            else:
                print("Pixel format not available...")
                result = False

            # Image Size
            image_size = config["ImageSize"]
            width = image_size.get("width", "Max")
            height = image_size.get("height", "Max")
            # Width
            if cam.Width.GetAccessMode() == PySpin.RW:
                if width.isdigit():
                    if cam.Width.GetMin() <= int(width) <= cam.Width.GetMax():
                        cam.Width.SetValue(int(width))
                    else:
                        print("[ImageSize] Invalid value in \"width: %s\"." % width)
                        return False
                else:
                    if width == "Max":
                        cam.Width.SetValue(cam.Width.GetMax())
                    elif width == "Min":
                        cam.Width.SetValue(cam.Width.GetMin())
                    else:
                        print("[ImageSize] Invalid value in \"width: %s\"." % width)
                        return False
                if not suppress_msg:
                    print("Width set to %i..." % cam.Width.GetValue())
            else:
                print("Width not available...")
                result = False
            # Height
            if cam.Height.GetAccessMode() == PySpin.RW:
                if height.isdigit():
                    if cam.Height.GetMin() <= int(height) <= cam.Height.GetMax():
                        cam.Height.SetValue(int(height))
                    else:
                        print("[ImageSize] Invalid value in \"height: %s\"." % height)
                        return False
                else:
                    if height == "Max":
                        cam.Height.SetValue(cam.Height.GetMax())
                    elif height == "Min":
                        cam.Height.SetValue(cam.Height.GetMin())
                    else:
                        print("[ImageSize] Invalid value in \"height: %s\"." % height)
                        return False
                if not suppress_msg:
                    print("Height set to %i..." % cam.Height.GetValue())
            else:
                print("Height not available...")
                result = False

            # Set Auto White Balance
            if format == "Mono8":
                pass
            else:
                white_balance = config["WhiteBalance"]
                mode = white_balance.get("mode", "Continuous")
                if cam.BalanceWhiteAuto.GetAccessMode() == PySpin.RW:
                    if mode == "Continuous":
                        # Enable Auto White Balance
                        cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Continuous)
                    elif mode == "Once":
                        # Enable Auto White Balance
                        cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Once)
                    else:
                        cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Off)
                        # Enable Manual White Balance
                        cam.BalanceRatioSelector.SetValue(PySpin.BalanceRatioSelector_Red)
                        cam.BalanceRatio.SetValue(white_balance.getfloat("red_ratio" , "0.732421875"))
                        cam.BalanceRatioSelector.SetValue(PySpin.BalanceRatioSelector_Blue)
                        cam.BalanceRatio.SetValue(white_balance.getfloat("blue_ratio", "3.662109375"))

                    if not suppress_msg:
                        print("Balance white auto set to %s..." % cam.BalanceWhiteAuto.GetCurrentEntry().GetSymbolic())
                        if mode == "Off":
                            print("Balance ratio set to Manual...")
                            cam.BalanceRatioSelector.SetValue(PySpin.BalanceRatioSelector_Red)
                            red_ratio = cam.BalanceRatio.GetValue()
                            cam.BalanceRatioSelector.SetValue(PySpin.BalanceRatioSelector_Blue)
                            blue_ratio = cam.BalanceRatio.GetValue()
                            print("(Red: %s, Blue: %s)" % (red_ratio, blue_ratio))
                else:
                    print("Balance white auto not available...")
                    result = False

        except PySpin.SpinnakerException as e:
            print("Error: %s" % e)
            return False

        return result

    def start_device(self, key):
        idx = self.__key2index(key)
        self.__camera_ref[idx].BeginAcquisition()
        print(f'key is: {key},idx: {idx}, started device in bfs_cotroller')

    def start_all_devices(self):
        for key in self.__serial_list:
            self.start_device(key)

    def grab(self, key, suppress_msg=False):
        """
        カメラから1フレーム分の画像をndarray形式で取得する
        """
        try:
            idx = self.__key2index(key)

            if not self.__camera_ref[idx].IsStreaming():
                self.__camera_ref[idx].BeginAcquisition()
            image_result = self.__camera_ref[idx].GetNextImage()
            # Ensure image is complete
            if image_result.IsIncomplete():
                if not suppress_msg:
                    print("Image incomplete with image status %d..." % image_result.GetImageStatus())
                # blank画像
                shape = (image_result.GetHeight(),
                         image_result.GetWidth(),
                         self.__num_channel(image_result.GetPixelFormat()))
                ndarray_image = np.zeros(shape, np.uint8)
            else:
                # Get image data as numpy.ndarray
                ndarray_image = image_result.GetNDArray()
                # Release image
                image_result.Release()

        except Exception as e:
            self.__exit_with_error_massage(e)
        except PySpin.SpinnakerException as e:
            self.__exit_with_error_massage(e)

        return ndarray_image

    def __num_channel(self, pixel_format):
        if pixel_format == PySpin.PixelFormat_BGR8 \
           or pixel_format == PySpin.PixelFormat_RGB8:
            return ChannelNumEnums.C3
        else:
            return ChannelNumEnums.C1

    def release_devices(self):
        try:
            # カメラへの参照オブジェクトを開放
            for i in range(self.__num_cameras):
                if self.__camera_ref[i].IsStreaming():
                    self.__camera_ref[i].EndAcquisition()
                if self.__camera_ref[i].IsInitialized():
                    self.__camera_ref[i].DeInit()
                self.__camera_ref[i] = None
                self.__serial_list[i] = ""

            # システムを開放する前にカメラリストをクリア
            self.__cam_list.Clear()
            self.__num_cameras = 0
            # 取得したシステムを開放
            self.__system.ReleaseInstance()

        except PySpin.SpinnakerException as e:
            self.__exit_with_error_massage(e)

    def get_num_device(self):
        return self.__num_cameras

    def get_serial_list(self):
       return self.__serial_list

    def __key2index(self, key):
        try:
            if type(key) is int:
                idx = key
            elif type(key) is str:
                idx = self.__serial2index(key)
            else:
                raise ValueError("the type of key was neither \'int\' nor \'str\'")

            if 0 <= idx < self.__num_cameras:
                return idx
            else:
                raise IndexError("camera corresponding to key (%s) did not exist" % key)

        except Exception as e:
            self.__exit_with_error_massage(e)

    def __serial2index(self, serial):
        if serial in self.__serial_list:
            return self.__serial_list.index(serial)
        else:
            return -1

    def __exit_with_error_massage(self, msg):
        print("Error: %s" % msg)
        sys.exit(1)
