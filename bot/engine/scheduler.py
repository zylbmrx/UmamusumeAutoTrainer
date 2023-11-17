import copy
import datetime
import threading
import time

import croniter

from bot.base.task import TaskStatus as TaskStatus, TaskExecuteMode, Task
import bot.engine.executor as executor
import bot.base.log as logger

log = logger.get_logger(__name__)


class Scheduler:
    task_list: list[Task] = []
    running_task: Task = None
    log_queue = logger.get_log_queue()

    active = False

    scheduler_status = False

    def stop(self):
        self.scheduler_status = False

    def get_log(self):
        queue_data = []
        while not self.log_queue.empty():
            data = self.log_queue.get()
            queue_data.append(data.message)

        return queue_data

    def add_task(self, task):
        log.info("已添加任务：" + task.task_id)
        self.task_list.append(task)

    def delete_task(self, task_id):
        remove_idx = -1
        for i, v in enumerate(self.task_list):
            if v.task_id == task_id:
                remove_idx = i
        if remove_idx != -1:
            del self.task_list[remove_idx]
            return True
        else:
            return False

    def reset_task(self, task_id):
        reset_idx = -1
        for i, v in enumerate(self.task_list):
            if v.task_id == task_id:
                reset_idx = i
        if reset_idx != -1:
            self.task_list[reset_idx].task_status = TaskStatus.TASK_STATUS_PENDING
            self.task_list[reset_idx].end_task_reason = None
            return True
        else:
            return False

    def init(self):
        task_executor = executor.Executor()
        self.scheduler_status = True
        while self.scheduler_status:
            if self.active:
                task_status = TaskStatus.TASK_STATUS_INVALID
                for task in self.task_list:
                    if task.task_status == TaskStatus.TASK_STATUS_RUNNING:
                        task_status = TaskStatus.TASK_STATUS_RUNNING  # 有任务正在运行
                        break
                if task_status == TaskStatus.TASK_STATUS_RUNNING:
                    # 有任务正在运行，不执行转正操作
                    pass
                else:
                    # TODO 任务调度,添加连续执行生成多个任务
                    for task in self.task_list:
                        if task.task_status == TaskStatus.TASK_STATUS_PENDING and not task_executor.active:
                            executor_thread = threading.Thread(target=task_executor.start, args=([task]))
                            executor_thread.start()

                            task.task_status = TaskStatus.TASK_STATUS_RUNNING
                            task_status = TaskStatus.TASK_STATUS_RUNNING
                            # 开始运行任务,不再判断下一个任务
                            break
                if task_status == TaskStatus.TASK_STATUS_INVALID:
                    # 执行完毕后，停止判断,下次开始需要手动启动
                    self.stop_task()
            else:
                if task_executor.active:
                    task_executor.stop()
            time.sleep(1)
        # 退出时停止所有任务
        if task_executor.active:
            task_executor.stop()

    def copy_task(self, task, to_task_execute_mode: TaskExecuteMode):
        new_task = copy.deepcopy(task)
        new_task.task_id = str(int(round(time.time() * 1000)))
        if (to_task_execute_mode == TaskExecuteMode.TASK_EXECUTE_MODE_ONE_TIME and task.task_execute_mode ==
                TaskExecuteMode.TASK_EXECUTE_MODE_CRON_JOB):
            new_task.task_id = "CRONJOB_" + new_task.task_id
            new_task.cron_job_config = None
        new_task.task_execute_mode = to_task_execute_mode
        if new_task.task_execute_mode == TaskExecuteMode.TASK_EXECUTE_MODE_ONE_TIME:
            new_task.task_status = TaskStatus.TASK_STATUS_PENDING
        self.task_list.append(new_task)

    def stop_task(self):
        self.active = False

    def start_task(self):
        self.active = True

    def get_task_list(self):
        return self.task_list

    def get_task_json_list(self):
        task_list = []
        for task in self.task_list:
            task_list.append(task.to_dict())
        return task_list


scheduler = Scheduler()
