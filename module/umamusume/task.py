import json
from enum import Enum
from bot.base.task import Task, TaskExecuteMode, TaskType


class TaskDetail:
    scenario_name: str
    current_attribute: list[int]
    expect_attribute: list[int]
    follow_support_card_name: str
    follow_support_card_level: int
    extra_race_list: list[int]
    learn_skill_list: list[str]
    tactic_list: list[int]
    clock_use_limit: int
    learn_skill_threshold: int
    learn_skill_only_user_provided: bool
    allow_recover_tp: bool
    cultivate_progress_info: dict
    extra_weight: list


class EndTaskReason(Enum):
    TP_NOT_ENOUGH = "训练值不足"


class UmamusumeTask(Task):
    detail: TaskDetail

    def to_dict(self):
        re = super().to_dict()
        re.update({
            "detail": self.detail.__dict__
        })
        return re

    def end_task(self, status, reason) -> None:
        super().end_task(status, reason)

    def start_task(self) -> None:
        pass


class UmamusumeTaskType(TaskType):
    UMAMUSUME_TASK_TYPE_UNKNOWN = 0
    UMAMUSUME_TASK_TYPE_CULTIVATE = 1


def build_task(task_execute_mode: TaskExecuteMode, task_type: int,
               task_desc: str, cron_job_config: dict, attachment_data: dict) -> UmamusumeTask:
    td = TaskDetail()
    ut = UmamusumeTask(task_execute_mode=task_execute_mode,
                       task_type=UmamusumeTaskType(task_type), task_desc=task_desc, app_name="umamusume")
    ut.cron_job_config = cron_job_config
    td.current_attribute = []
    td.expect_attribute = attachment_data['expect_attribute']
    td.follow_support_card_level = int(attachment_data['follow_support_card_level'])
    td.follow_support_card_name = attachment_data['follow_support_card_name']
    td.extra_race_list = attachment_data['extra_race_list']
    td.learn_skill_list = attachment_data['learn_skill_list']
    td.tactic_list = attachment_data['tactic_list']
    td.clock_use_limit = attachment_data['clock_use_limit']
    td.learn_skill_threshold = attachment_data['learn_skill_threshold']
    td.learn_skill_only_user_provided = attachment_data['learn_skill_only_user_provided']
    td.allow_recover_tp = attachment_data['allow_recover_tp']
    td.extra_weight = attachment_data['extra_weight']
    td.cultivate_result = {}
    # td.scenario_name = attachment_data['scenario_name']
    ut.detail = td
    return ut
