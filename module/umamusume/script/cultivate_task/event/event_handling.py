import json
import os

import requests

from bot.recog.ocr import find_similar_text
from config import CONFIG
from module.umamusume.define import EventType
import bot.base.log as logger
import urllib.parse
from lxml import etree

log = logger.get_logger(__name__)


def character_maketrans(english_str: str):
    # 定义中文符号
    chinese_character = r'，。！？；：（）《》【】“”\‘\’'
    # 定义对应的英文符号
    english_character = r',.!?;:()<>[]""\'\''

    # 创建转换表
    table = str.maketrans(english_character, chinese_character)
    return english_str.translate(table)


class event_handling:
    # event 格式如下
    # {
    #    "!!girls": {
    #     "[雀跃维他命心拍]特别周": {
    #       "girl_name": "【雀跃♪维他命心拍】特别周",
    #       "uid": 1001,
    #       "spUid": 100102
    #     }
    # }
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
    girls_key_name = "!!girls"

    def __init__(self):
        self.event_path = "./event.json" if CONFIG.event.path is None else CONFIG.event.path
        if not os.path.exists(self.event_path):
            with open(self.event_path, "w", encoding='utf-8') as f:
                f.write(json.dumps({EventType.EVENT.value: {}, }, indent=4, ensure_ascii=False))
        self.event = self.read_event()
        if self.girls_key_name not in self.event:
            self.event[self.girls_key_name] = {}
            self.save_event()
        self.wiki_path = "https://wiki.biligame.com/umamusume/" \
            if CONFIG.event.wiki_path is None else CONFIG.event.wiki_path

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

    def check_umamusume_girl_name(self, umamusume_name, girl_name=None):
        log.debug("检查马娘名称: %s " % umamusume_name)
        query_path = urllib.parse.urljoin(self.wiki_path, "index.php?title=")
        query = urllib.parse.quote("简/" +
                                   (character_maketrans(umamusume_name) if girl_name is None else girl_name)
                                   )
        event_path = urllib.parse.urljoin(self.wiki_path, "api.php")
        event_params = {"action": "parse",
                        "format": "json",
                        "disablelimitreport": True,
                        "prop": "text",
                        "contentmodel": "wikitext",
                        }

        try:
            log.info("访问马娘wiki: %s " % query_path + query + "  请稍等...")
            r = requests.get(query_path + query)
            re = r.text
            if "'''有分支'''" not in re:
                log.error("马娘名称检查失败,需要手动生成马娘名称")
                self.event[self.girls_key_name][umamusume_name] = {
                    "girl_name": None,
                    "uid": None,
                    "spUid": None
                }
                self.save_event()
                raise Exception("马娘名称检查失败")

            api_text = re.split("'''有分支'''\n&lt;hr&gt;")[1].split("&lt;br&gt;\n'''赛后'''")[0]

            uid = int(api_text.split("角色id::")[1].split("|")[0])
            spUid = int(api_text.split("特有id::")[1].split("|")[0])

            self.event[self.girls_key_name][umamusume_name] = {
                "girl_name": character_maketrans(umamusume_name) if girl_name is None else girl_name,
                "uid": uid,
                "spUid": spUid
            }

            if umamusume_name not in self.event:
                self.event[umamusume_name] = {EventType.EVENT.value: {}, EventType.SUPPORT_CARD.value: {}}

            event_params["text"] = api_text
            log.info("访问马娘wiki: %s " % event_path + "  请稍等...")
            re = requests.get(event_path, params=event_params)
            re = re.json()
            html = (urllib.parse.unquote(re.get("parse", {}).get("text", {}).get("*")))
            html = etree.HTML(html)
            event_list = html.xpath("//span[@class='popup']")

            e = self.event[umamusume_name][EventType.EVENT.value]
            for event in event_list:
                eName = event.xpath(".//div[@class='sj-an']/a/text()")[0]
                e[eName] = {"def_opt": 1, "opt": {}}
                rows = event.xpath(".//table/tbody/tr")[1:]
                count = 0
                for row in rows:
                    count += 1
                    if row.xpath("./td[1]/text()")[0] != "\n":
                        td1 = row.xpath("./td[1]/text()")[0].replace("\n", "")
                    else:
                        td1 = row.xpath("./td[1]/span/text()")[0]
                    td2 = ";".join(row.xpath("./td[2]/text()")).replace("\n", "")
                    e[eName]["opt"][count] = {
                        'opt': td1,
                        "desc": td2
                    }
            self.save_event()
        except Exception as e:
            raise e

        return umamusume_name

    def get_umamusume_girl_name(self, umamusume_name):
        re = find_similar_text(umamusume_name, self.event.get(self.girls_key_name, {}).keys(), 0.9)
        # 可能会误判,等出现问题再说
        if re != "":
            umamusume_name = re

        if umamusume_name not in self.event[self.girls_key_name]:
            return self.check_umamusume_girl_name(umamusume_name)

        if self.event[self.girls_key_name][umamusume_name].get("girl_name") is None:
            return self.check_umamusume_girl_name(umamusume_name)

        if self.event[self.girls_key_name][umamusume_name].get("uid") is None:
            if self.event[self.girls_key_name][umamusume_name].get("girl_name") is not None:
                # 针对无法识别的马娘名称
                girl_name = self.event[self.girls_key_name][umamusume_name]["girl_name"]
                return self.check_umamusume_girl_name(umamusume_name, girl_name)
        return umamusume_name

    def get_msg_from_wiki(self, umamusume_name, event_type: EventType, event_name):
        if event_type == EventType.EVENT:
            pass
        elif event_type == EventType.SUPPORT_CARD:
            pass

        return {
            # 1: {"opt": "", "desc": ""}
        }

    def get_event_handling(self, umamusume_name, event_type: EventType, event_name):
        # TODO 从马娘wiki上获取没有的协助卡事件详细数据并保存

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
