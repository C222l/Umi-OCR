# =======================================
# =============== 二维码页 ===============
# =======================================

from .page import Page  # 页基类
from ..image_controller.image_provider import PixmapProvider  # 图片提供器
from ..mission.mission_qrcode import MissionQRcode

import os
import time
from PIL import Image, ImageEnhance, ImageFilter
import base64

try:
    import zxingcpp
except Exception as e:
    zxingcpp = None
    zxingcppErr = str(e)


class QRcode(Page):
    # def __init__(self, *args):
    #     super().__init__(*args)

    # 对一个imgID进行扫码
    def scanImgID(self, imgID, configDict):
        msnInfo = {
            "onStart": self._onStart,
            "onReady": self._onReady,
            "onGet": self._onGet,
            "onEnd": self._onEnd,
            "argd": configDict,
        }
        msnList = [{"pil": PixmapProvider.getPilImage(imgID), "imgID": imgID}]
        MissionQRcode.addMissionList(msnInfo, msnList)

    # 对一串path进行扫码
    def scanPaths(self, paths, configDict):
        msnInfo = {
            "onStart": self._onStart,
            "onReady": self._onReady,
            "onGet": self._onGet,
            "onEnd": self._onEnd,
            "argd": configDict,
        }
        msnList = [{"path": x} for x in paths]
        MissionQRcode.addMissionList(msnInfo, msnList)

    # 生成二维码
    # format: "Aztec","Codabar","Code128","Code39","Code93","DataBar","DataBarExpanded","DataMatrix","EAN13","EAN8","ITF","LinearCodes","MatrixCodes","MaxiCode","MicroQRCode","PDF417","QRCode","UPCA","UPCE",
    # quiet_zone: 四周的空闲区域
    # ec_level：纠错等级，-1 - 自动, 1- L-7% , 0 - M-15%, 3 - Q-25%, 2 - H-30%
    # 纠错仅用于Aztec、PDF417和QRCode
    def writeBarcode(self, format, text, w=0, h=0, quiet_zone=-1, ec_level=-1):
        # 转整数
        w, h = round(w), round(h)
        quiet_zone, ec_level = round(quiet_zone), round(ec_level)
        # 生成格式对象
        bFormat = getattr(zxingcpp.BarcodeFormat, format, None)
        if not bFormat:
            return f"[Error] format {format} not in zxingcpp.BarcodeFormat!"
        try:
            bit = zxingcpp.write_barcode(bFormat, text, w, h, quiet_zone, ec_level)
        except Exception as e:
            return f"[Error] [{format}] {e}"
        try:
            img = Image.fromarray(bit, "L")
        except Exception as e:
            return f"[Error] Image.fromarray: {e}"
        imgID = PixmapProvider.setPilImage(img)
        # 若 setPilImage 失败， imgID.startswith("[Error]")
        return imgID

    # ========================= 【扫码处理】 =========================

    def _onStart(self, msnInfo):  # 任务队列开始
        self.callQmlInMain("setRunning", True)

    def _onReady(self, msnInfo, msn):  # 单个任务准备
        pass

    def _onGet(self, msnInfo, msn, res):  # 单个任务完成
        # 通知qml更新UI
        imgID = msn.get("imgID", "")
        imgPath = msn.get("path", "")
        self.callQmlInMain("onQRcodeGet", res, imgID, imgPath)  # 在主线程中调用qml

    def _onEnd(self, msnInfo, msg):  # 任务队列完成或失败
        # msg: [Success] [Warning] [Error]
        self.callQmlInMain("setRunning", False)
