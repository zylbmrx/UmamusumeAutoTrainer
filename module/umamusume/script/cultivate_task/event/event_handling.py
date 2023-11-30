import json
import os

from config import CONFIG
from module.umamusume.define import EventType


class event_handling:
    # event 格式如下
    # {
    # "!support_card": {},# 这里是支援卡事件默认选项
    #         # 暂不考虑支援卡区别(单纯k支援卡卡面太麻烦了)
    # "马娘名称": {
    #     "event": {
    #         "事件名称": {
    #             "def_opt": 1,  # int,默认选项
    #             "opt": {  # dict,选项
    #                 1: {
    #                     "desc": "选项描述",
    #                 }
    #             }
    #         }
    #
    #     },
    #     "!support_card": {
    #         "事件名称": {
    #             "def_opt": 1,  # int,默认选项
    #             "opt": {  # dict,选项
    #                 1: {
    #                     "desc": "选项描述",
    #                 }
    #             }
    #         }
    #     }}
    # }

    def __init__(self):
        self.event_path = "./event.json" if CONFIG.event.path is None else CONFIG.event.path
        if not os.path.exists(self.event_path):
            with open(self.event_path, "w", encoding='utf-8') as f:
                f.write(json.dumps({EventType.EVENT.value: {}, }, indent=4, ensure_ascii=False))
        self.event = self.read_event()

    def reload(self):
        self.event = self.read_event()

    def read_event(self):
        with open(self.event_path, "r", encoding='utf-8') as f:
            lines = f.read()
            j = json.loads(lines)
            return j

    def save_event(self):
        with open(self.event_path, "w", encoding='utf-8') as f:
            f.write(json.dumps(self.event, indent=4, ensure_ascii=False))
            # 不转义中文

    def get_msg_from_wiki(self, umamusume_name, event_type: EventType, event_name):
        if event_type == EventType.EVENT:
            pass
        elif event_type == EventType.SUPPORT_CARD:
            pass

        return {
            # 1: {"opt": "", "desc": ""}
        }

    def get_event_handling(self, umamusume_name, event_type: EventType, event_name):
        # TODO 从马娘wiki上获取没有的事件详细数据并保存

        if event_type == EventType.EVENT:
            # 如果是养成优俊少女事件
            if umamusume_name not in self.event:
                self.event[umamusume_name] = {EventType.EVENT.value: {}, EventType.SUPPORT_CARD.value: {}}
                self.event[umamusume_name][event_type.value][event_name] = {"def_opt": 1, "opt": {}}  # 1: {"desc": ""}
                self.save_event()
                return None

            if event_name not in self.event[umamusume_name][event_type.value]:
                self.event[umamusume_name][event_type.value][event_name] = {"def_opt": 1, "opt": {}}
                self.save_event()
                return None
            else:
                return self.event[umamusume_name][event_type.value][event_name]["def_opt"]
        elif event_type == EventType.SUPPORT_CARD:
            # 如果是支援卡事件
            if event_name not in self.event[event_type.value]:
                self.event[event_type.value][event_name] = {"def_opt": 1, "opt": {}}
                self.save_event()
                return None
            else:
                # 注意一定是先有默认的选项才会去检查否有对应马娘的配置
                if umamusume_name not in self.event:
                    self.event[umamusume_name] = {EventType.EVENT.value: {}, EventType.SUPPORT_CARD.value: {}}
                    self.save_event()
                    return self.event[event_type.value][event_name]["def_opt"]
                elif event_name in self.event[umamusume_name][event_type.value]:
                    return self.event[umamusume_name][event_type.value][event_name]["def_opt"]
                else:
                    return self.event[event_type.value][event_name]["def_opt"]
