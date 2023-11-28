import os
import re

import psutil
import subprocess

from config import CONFIG


def kill_emulator_bluestacks():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'HD-Player' or proc.info['name'] == 'HD-Player.exe':
            print(proc.info)
            kill_emulator()
    return False


def kill_emulator():
    # 端口关闭代码
    pid = 0
    address = CONFIG.bot.auto.adb.device_name
    port = address[10:] if address.startswith('127') else '5555'

    port_cmd = f"netstat -ano|findstr \"{port}\""
    check_cmd = subprocess.Popen(port_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    reg = re.compile("\\s+")
    while True:
        line = check_cmd.stdout.readline().decode().strip()
        if not line:
            break
        if not line.lower().startswith("tcp"):
            continue
        line = reg.sub(",", line)
        try:
            arr = line.split(',')
            if len(arr) >= 2 and (arr[1] == address or arr[1] == f"[::]:{port}" or arr[1] == f"0.0.0.0:{port}"):
                pid = int(arr[4])
                print(pid)
                break
        except Exception as e:
            print(f"Failed to parse cmd.exe output: {str(e)}")

    if pid == 0:
        print("Failed to get emulator PID")
        return False
    try:
        emulator = psutil.Process(pid)
        emulator.terminate()
    except:
        return False

    return True
