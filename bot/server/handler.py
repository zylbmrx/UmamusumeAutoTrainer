import asyncio
import json
import os
import signal
import sys
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect

from bot.conn.connect_hook import before_connect, after_connect
from bot.engine import ctrl as bot_ctrl
from bot.server.protocol.task import *
from starlette.responses import FileResponse
import bot.base.log as logger

server = FastAPI()

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
log = logger.get_logger(__name__)


@server.on_event("startup")
def startup_event():
    before_connect()


@server.on_event("shutdown")
def shutdown_event():
    if sys.platform == "win32":
        after_connect()
        # 解决pycharm下按ctrl+c无法退出的问题
        os.popen("taskkill /F /PID " + str(os.getpid()))


@server.post("/task")
def add_task(req: AddTaskRequest):
    bot_ctrl.add_task(req.app_name, req.task_execute_mode, req.task_type, req.task_desc,
                      req.cron_job_config, req.attachment_data)


@server.delete("/task")
def delete_task(req: DeleteTaskRequest):
    bot_ctrl.delete_task(req.task_id)


@server.get("/task")
def get_task():
    return bot_ctrl.get_task_list()


@server.post("/action/bot/reset-task")
def reset_task(req: ResetTaskRequest):
    bot_ctrl.reset_task(req.task_id)


@server.post("/action/bot/start")
def start_bot():
    bot_ctrl.start()


@server.post("/action/bot/stop")
def stop_bot():
    bot_ctrl.stop()


@server.get("/")
async def get_index():
    return FileResponse('public/index.html')


@server.websocket("/ws/get_log")
async def websocket_get_log_func(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            msgType = data.get("msgType")
            wait_time = 0

            match msgType:
                case "ping":
                    await pong(websocket)
                case "get_log":
                    while True:
                        bot_ctrl_log = bot_ctrl.get_log()
                        if len(bot_ctrl_log) > 0:
                            wait_time = 0
                            await websocket.send_json({
                                "msgType": "log",
                                "log": bot_ctrl_log})
                        else:
                            wait_time += 1
                            if wait_time > 30:
                                await pong(websocket)
                                wait_time = 0
                        await asyncio.sleep(1)

    except WebSocketDisconnect as e:
        log.error("/ws/get_log Client disconnected", e)
    except Exception as e:
        log.error(e)


@server.websocket("/ws/get_task_list")
async def websocket_get_task_list_func(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            msgType = data.get("msgType")

            match msgType:
                case "ping":
                    await pong(websocket)
                case "get_task_list":
                    while True:
                        await websocket.send_json({
                            "msgType": "taskList",
                            "taskList": bot_ctrl.get_task_json_list(),
                        })
                        await asyncio.sleep(1)
    except WebSocketDisconnect as e:
        log.error("/ws/get_task_list Client disconnected", e)
    except Exception as e:
        log.error(e)


async def pong(websocket: WebSocket):
    await websocket.send_json({
        "msgType": "pong"
    })


@server.get("/{whatever:path}")
async def get_static_files_or_404(whatever):
    # try open file for path
    file_path = os.path.join("public", whatever)
    if os.path.isfile(file_path):
        if file_path.endswith((".js", ".mjs")):
            return FileResponse(file_path, media_type="application/javascript")
        else:
            return FileResponse(file_path)
    return FileResponse('public/index.html')
