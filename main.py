import sys
import threading

from bot.base.manifest import register_app
from bot.engine.scheduler import scheduler
from config import CONFIG
from module.umamusume.manifest import UmamusumeManifest
from uvicorn import run

if __name__ == '__main__':
    if sys.version_info.minor != 10 or sys.version_info.micro != 9:
        print("\033[33m{}\033[0m".format("注意：python 版本号不正确，可能无法正常运行"))
        print("建议python版本：3.10.9 当前：" + sys.version)
    register_app(UmamusumeManifest)
    scheduler_thread = threading.Thread(target=scheduler.init, args=())
    scheduler_thread.start()
    run("bot.server.handler:server", host=CONFIG.host, port=CONFIG.port, log_level="error")
    # TODO run的reload=True 参数无法使用
