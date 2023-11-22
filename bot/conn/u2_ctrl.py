import time
import random
import os
from typing import Optional

import cv2
import uiautomator2 as u2

import bot.conn.os as bot_os
import bot.base.log as logger
import threading

from bot.base.common import ImageMatchMode
from bot.base.point import ClickPoint, ClickPointType
from bot.conn.ctrl import AndroidController
from bot.recog.image_matcher import template_match
from config import CONFIG, Config
from dataclasses import dataclass, field

log = logger.get_logger(__name__)


#  wrapper 装饰器
# 用于重试adb命令
def wrapper(func):
    def checker(*args, **kwargs):
        tries = 0
        while tries < 3:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                tries += 1
                log.error(e)
                log.error("第" + str(tries) + "次失败")
                time.sleep(2)
        log.error("adb操作失败")
        raise Exception("adb操作失败")

    return checker
@dataclass
class U2AndroidConfig:
    _device_name: str
    delay: float
    bluestacks_config_path: Optional[str] = None
    bluestacks_config_keyword: Optional[str] = None

    _bluestacks_port: Optional[str] = field(init=False, repr=False, default=None)

    @property
    def device_name(self) -> str:
        bluestacks_port = self.bluestacks_port
        if bluestacks_port is not None:
            return f"127.0.0.1:{bluestacks_port}"
        return self._device_name

    @property
    def bluestacks_port(self) -> Optional[str]:
        if self._bluestacks_port is not None:
            return self._bluestacks_port
        if self.bluestacks_config_path and self.bluestacks_config_keyword:
            with open(self.bluestacks_config_path) as file:
                self._bluestacks_port = next((
                    line.split('=')[1].strip().strip('"')
                    for line in file
                    if self.bluestacks_config_keyword in line
                ), None)
        return self._bluestacks_port

    @staticmethod
    def load(config: Config):
        return U2AndroidConfig(
            _device_name=config.bot.auto.adb.device_name,
            delay=config.bot.auto.adb.delay,
            bluestacks_config_path=config.bot.auto.adb.bluestacks_config_path,
            bluestacks_config_keyword=config.bot.auto.adb.bluestacks_config_keyword,
        )


class U2AndroidController(AndroidController):
    config = U2AndroidConfig.load(CONFIG)

    path = "deps\\adb\\"
    recent_point = None
    recent_operation_time = None
    same_point_operation_interval = 0.3
    u2client = None

    def __init__(self):
        if CONFIG.test.save_screen:
            if not os.path.exists(CONFIG.test.save_screen_path):
                os.makedirs(CONFIG.test.save_screen_path)

        pass

    # init_env 初始化环境
    @wrapper
    def init_env(self) -> None:
        self.u2client = u2.connect(self.config.device_name)

    # get_screen 获取图片
    @wrapper
    def get_screen(self, to_gray=False):
        cur_screen = self.u2client.screenshot(format='opencv')
        if to_gray:
            return cv2.cvtColor(cur_screen, cv2.COLOR_BGR2GRAY)

        if CONFIG.test.save_screen:
            # 保存截图,方便确认识别问题
            # try:
            #     cv2.imwrite(CONFIG.test.save_screen_path + "/%s.png" % time.time(), cur_screen)
            # except :
            #     log.debug("save screen1 error")
            try:
                cv2.imencode('.png', cur_screen)[1].tofile(CONFIG.test.save_screen_path + "/%s.png" % time.time())
            except :
                log.debug("save screen error")

        return cur_screen

    # ===== ctrl =====

    @wrapper
    def click_by_point(self, point: ClickPoint, random_offset=True):
        if self.recent_point is not None:
            if self.recent_point == point and time.time() - self.recent_operation_time < self.same_point_operation_interval:
                log.warning("request for a same point too frequently")
                return
        if point.target_type == ClickPointType.CLICK_POINT_TYPE_COORDINATE:
            self.click(point.coordinate.x, point.coordinate.y, name=point.desc, random_offset=random_offset)
        elif point.target_type == ClickPointType.CLICK_POINT_TYPE_TEMPLATE:
            cur_screen = self.get_screen(to_gray=True)
            if point.template.image_match_config.match_mode == ImageMatchMode.IMAGE_MATCH_MODE_TEMPLATE_MATCH:
                match_result = template_match(cur_screen, point.template.template_image)
                if match_result.find_match:
                    self.click(match_result.center_point[0], match_result.center_point[1], random_offset=random_offset)
        self.recent_point = point
        self.recent_operation_time = time.time()

    @wrapper
    def click(self, x, y, name="", random_offset=True, max_x=720, max_y=1280):
        if name != "":
            log.debug("click >> " + name)
        if random:
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            x += offset_x
            y += offset_y
        if x >= max_x:
            x = max_x - 1
        if y >= max_y:
            y = max_y - 1
        if x < 0:
            x = 1
        if y <= 0:
            y = 1
        _ = self.execute_adb_shell("shell input tap " + str(x) + " " + str(y), True)
        time.sleep(self.config.delay)

    @wrapper
    def swipe(self, x1=1025, y1=550, x2=1025, y2=550, duration=0.2, name=""):
        if name != "":
            log.debug("swipe >> " + name)
        _ = self.execute_adb_shell("shell input swipe " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2) + " "
                                   + str(duration), True)
        time.sleep(self.config.delay)

    # ===== common =====

    # execute_adb_shell 执行adb命令
    @wrapper
    def execute_adb_shell(self, cmd, sync):
        cmd = bot_os.run_cmd(self.path + "adb.exe -s " + self.config.device_name + " " + cmd)
        if sync:
            cmd.communicate()
        else:
            threading.Thread(target=cmd.communicate, args=())
        return cmd

    @wrapper
    def start_app(self, name):
        self.u2client.app_start(name)
        log.info("starting app <" + name + ">")

    # get_front_activity 获取前台正在运行的应用
    @wrapper
    def get_front_activity(self):

        rsp = self.execute_adb_shell("shell \"dumpsys window windows | grep \"Current\"\"", True).communicate()
        log.debug(str(rsp))
        return str(rsp)

    # get_devices 获取adb连接设备状态
    @wrapper
    def get_devices(self):
        p = bot_os.run_cmd(self.path + "adb.exe devices").communicate()
        devices = p[0].decode()
        log.debug(devices)
        return devices

    # connect_to_device 连接至设备
    @wrapper
    def connect_to_device(self):
        p = bot_os.run_cmd(self.path + "adb.exe connect " + self.config.device_name).communicate()
        log.debug(p[0].decode())

    # kill_adb_server 停止adb-server
    @wrapper
    def kill_adb_server(self):
        p = bot_os.run_cmd(self.path + "adb.exe kill-server").communicate()
        log.debug(p[0].decode())

    # check_file_exist 判断文件是否存在
    @wrapper
    def check_file_exist(self, file_path, file_name):
        rsp = self.execute_adb_shell("shell ls " + file_path, True).communicate()
        file_list = rsp[0].decode()
        log.debug(str("ls file result:" + file_list))
        return file_name in file_list

    # push_file 推送文件
    @wrapper
    def push_file(self, src, dst):
        self.execute_adb_shell("push " + src + " " + dst, True)

    # get_device_os_info 获取系统信息
    @wrapper
    def get_device_os_info(self):
        rsp = self.execute_adb_shell("shell getprop ro.build.version.sdk", True).communicate()
        os_info = rsp[0].decode().replace('\r', '').replace('\n', '')
        log.debug("device os info: " + os_info)
        return os_info

    # get_device_cpu_info 获取cpu信息
    @wrapper
    def get_device_cpu_info(self):
        rsp = self.execute_adb_shell("shell getprop ro.product.cpu.abi", True).communicate()
        cpu_info = rsp[0].decode().replace('\r', '').replace('\n', '')
        log.debug("device cpu info: " + cpu_info)
        return cpu_info

    # destroy 销毁
    def destroy(self):
        pass
