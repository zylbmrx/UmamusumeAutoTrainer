from typing import Union

from bot.recog.ocr import find_similar_text
from module.umamusume.define import EventType
from module.umamusume.script.cultivate_task.event.event_handling import event_handling
from module.umamusume.script.cultivate_task.event.scenario_event import *
import bot.base.log as logger

log = logger.get_logger(__name__)

event_map: dict[str, Union[callable, int]] = {
    "安心～针灸师，登☆场": 5,
    "新年的抱负": scenario_event_1,
    "新年参拜": scenario_event_2,
    "新年祈福": scenario_event_2
}

event_name_list: list[str] = [*event_map]


def get_event_choice(ctx: UmamusumeContext, event_name: str, event_type: EventType) -> int:
    events = ctx.cultivate_detail.events
    event_name_normalized = find_similar_text(event_name, event_name_list, 0.8)
    if event_name_normalized != "":
        if event_name_normalized in event_map:
            opt = event_map[event_name_normalized]
            if type(opt) is int:
                return opt
            if callable(opt):
                return opt(ctx)
            else:
                log.warning("事件[%s]未提供处理逻辑", event_name_normalized)
                return 1

    opt = events.get_event_handling(ctx.cultivate_detail.umamusume_girl, event_type, event_name)
    if opt is None:
        log.info("事件[%s]首次出现, 使用默认选项1", event_name)
        return 1
    else:
        return opt
