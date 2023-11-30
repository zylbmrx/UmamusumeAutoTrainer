import time

import cv2

from bot.base.task import TaskStatus, EndTaskReason
from module.umamusume.task import EndTaskReason as UEndTaskReason
from bot.recog.image_matcher import image_match
from bot.recog.ocr import ocr_line, find_similar_text
from module.umamusume.asset.point import *
from module.umamusume.asset.ui import INFO
from module.umamusume.context import UmamusumeContext
import bot.base.log as logger

log = logger.get_logger(__name__)

TITLE = {
    0: "赛事详情",
    1: "休息&外出确认",
    2: "网络错误",
    3: "重新挑战",
    4: "获得誉名",
    5: "完成养成",
    6: "缩短事件设置",
    7: "外出确认",
    8: "技能获取确认",
    9: "成功获得技能",
    10: "养成结束确认",
    11: "优俊少女详情",
    12: "粉丝数未达到目标赛事要求",
    13: "外出",
    14: "跳过确认",
    15: "休息确认",
    16: "赛事推荐功能",
    17: "战术",
    18: "目标粉丝数不足",
    19: "连续参赛",
    20: "医务室确认",
    21: "礼物箱",
    22: "领取成功",
    23: "解锁角色剧情",
    24: "目标达成次数不足",
    25: "活动剧情解锁",
    26: "确认",
    27: "回复训练值",
    28: "选择养成难度",
    29: "菜单",
    30: "编成信息",
}


def script_info(ctx: UmamusumeContext):
    img = ctx.current_screen
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    result = image_match(img, UI_INFO)
    if result.find_match:
        pos = result.matched_area
        title_img = img[pos[0][1] - 5:pos[1][1] + 5, pos[0][0] + 150: pos[1][0] + 405]
        title_text = ocr_line(title_img)
        log.debug(title_text)
        title_text = find_similar_text(title_text, TITLE.values(), 0.8)
        if title_text == "":
            log.warning("未知的选项框")
            return
        if title_text == TITLE[0]:
            ctx.ctrl.click_by_point(CULTIVATE_GOAL_RACE_INTER_3)
            time.sleep(1)
        if title_text == TITLE[1]:
            ctx.ctrl.click_by_point(INFO_SUMMER_REST_CONFIRM)
        if title_text == TITLE[2]:
            ctx.ctrl.click_by_point(NETWORK_ERROR_CONFIRM)
        if title_text == TITLE[3]:
            if ctx.prev_ui is INFO:
                ctx.cultivate_detail.clock_used -= 1
            if ctx.cultivate_detail.clock_use_limit > ctx.cultivate_detail.clock_used:
                ctx.ctrl.click_by_point(RACE_FAIL_CONTINUE_USE_CLOCK)
                ctx.cultivate_detail.clock_used += 1
            else:
                ctx.ctrl.click_by_point(RACE_FAIL_CONTINUE_CANCEL)
            log.debug("闹钟限制%s,已使用%s", str(ctx.cultivate_detail.clock_use_limit),
                      str(ctx.cultivate_detail.clock_used))
        if title_text == TITLE[4]:
            ctx.ctrl.click_by_point(GET_TITLE_CONFIRM)
        if title_text == TITLE[5]:
            ctx.ctrl.click_by_point(CULTIVATE_FINISH_RETURN_CONFIRM)
        if title_text == TITLE[6]:
            ctx.ctrl.click_by_point(SCENARIO_SHORTEN_SET_2)
            time.sleep(0.5)
            ctx.ctrl.click_by_point(SCENARIO_SHORTEN_CONFIRM)
        if title_text == TITLE[7]:
            ctx.ctrl.click_by_point(CULTIVATE_OPERATION_COMMON_CONFIRM)
        if title_text == TITLE[8]:
            ctx.ctrl.click_by_point(CULTIVATE_LEARN_SKILL_CONFIRM_AGAIN)
        if title_text == TITLE[9]:
            ctx.ctrl.click_by_point(CULTIVATE_LEARN_SKILL_DONE_CONFIRM)
            ctx.cultivate_detail.learn_skill_selected = False
        if title_text == TITLE[10]:
            ctx.ctrl.click_by_point(CULTIVATE_FINISH_CONFIRM_AGAIN)
        if title_text == TITLE[11]:
            ctx.ctrl.click_by_point(CULTIVATE_RESULT_CONFIRM)
        if title_text == TITLE[12]:
            ctx.ctrl.click_by_point(CULTIVATE_FAN_NOT_ENOUGH_RETURN)
        if title_text == TITLE[13]:
            ctx.ctrl.click_by_point(CULTIVATE_TRIP_WITH_FRIEND)
        if title_text == TITLE[14]:
            ctx.ctrl.click_by_point(SKIP_CONFIRM)
        if title_text == TITLE[15]:
            ctx.ctrl.click_by_point(CULTIVATE_OPERATION_COMMON_CONFIRM)
        if title_text == TITLE[16]:
            ctx.ctrl.click_by_point(RACE_RECOMMEND_CONFIRM)
        if title_text == TITLE[17]:
            date = ctx.cultivate_detail.turn_info.date
            if date != -1:
                if date <= 72:
                    ctx.ctrl.click_by_point(TACTIC_LIST[ctx.cultivate_detail.tactic_list[int((date - 1) / 24)] - 1])
                else:
                    ctx.ctrl.click_by_point(TACTIC_LIST[ctx.cultivate_detail.tactic_list[2] - 1])
            time.sleep(0.5)
            ctx.ctrl.click_by_point(BEFORE_RACE_CHANGE_TACTIC_CONFIRM)
        if title_text == TITLE[18]:
            ctx.ctrl.click_by_point(CULTIVATE_FAN_NOT_ENOUGH_RETURN)
        if title_text == TITLE[19]:
            ctx.ctrl.click_by_point(CULTIVATE_TOO_MUCH_RACE_WARNING_CONFIRM)
        if title_text == TITLE[20]:
            ctx.ctrl.click_by_point(CULTIVATE_OPERATION_COMMON_CONFIRM)
        if title_text == TITLE[21]:
            ctx.ctrl.click_by_point(RECEIVE_GIFT)
        if title_text == TITLE[22]:
            ctx.ctrl.click_by_point(RECEIVE_GIFT_SUCCESS_CLOSE)
        if title_text == TITLE[23]:
            ctx.ctrl.click_by_point(UNLOCK_STORY_TO_HOME_PAGE)
        if title_text == TITLE[24]:
            ctx.ctrl.click_by_point(WIN_TIMES_NOT_ENOUGH_RETURN)
        if title_text == TITLE[25]:
            ctx.ctrl.click_by_point(ACTIVITY_STORY_UNLOCK_CONFIRM)
        if title_text == TITLE[26]:
            if not ctx.cultivate_detail.allow_recover_tp:
                ctx.task.end_task(TaskStatus.TASK_STATUS_FAILED, UEndTaskReason.TP_NOT_ENOUGH)
            else:
                ctx.ctrl.click_by_point(TO_RECOVER_TP)
        if title_text == TITLE[27]:
            if image_match(ctx.ctrl.get_screen(to_gray=True), REF_RECOVER_TP_1).find_match:
                ctx.ctrl.click_by_point(USE_TP_DRINK)
            elif image_match(ctx.ctrl.get_screen(to_gray=True), REF_RECOVER_TP_2).find_match:
                ctx.ctrl.click_by_point(USE_TP_DRINK_CONFIRM)
            elif image_match(ctx.ctrl.get_screen(to_gray=True), REF_RECOVER_TP_3).find_match:
                ctx.ctrl.click_by_point(USE_TP_DRINK_RESULT_CLOSE)
        if title_text == TITLE[28]:
            ctx.ctrl.click_by_point(SELECT_DIFFICULTY)
        if title_text == TITLE[29]:
            if ctx.cultivate_detail.umamusume_girl is None:
                ctx.ctrl.click_by_point(OPEN_BREEDING_INFORMATION)
            else:
                ctx.ctrl.click_by_point(CLOSE_MENU)
        if title_text == TITLE[30]:
            if ctx.cultivate_detail.umamusume_girl is None:
                ctx.cultivate_detail.umamusume_girl = ocr_line(img[170:260, 150:680])
                log.info("养成的马娘:%s" % ctx.cultivate_detail.umamusume_girl)
                ctx.ctrl.click_by_point(CLOSE_BREEDING_INFORMATION)
            else:
                ctx.ctrl.click_by_point(CLOSE_BREEDING_INFORMATION)
        time.sleep(1)
