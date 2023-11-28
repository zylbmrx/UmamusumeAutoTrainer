import os
import signal
import sys

from bot.conn.kill_emulator_bluestacks import kill_emulator_bluestacks
from config import CONFIG

old_bluestacks = ''


def before_connect():
    global old_bluestacks
    if CONFIG.bluestacks:
        if CONFIG.bluestacks.check_config:
            instance = CONFIG.bluestacks.instance
            with open(CONFIG.bluestacks.bluestacks_conf, 'r+', encoding='utf-8') as f:
                lines = f.readlines()
                wLines = ''
                for i in lines:
                    old_bluestacks += i
                    if i.startswith(instance + '.fb_height'):
                        wLines += instance + '.fb_height="' + str(CONFIG.bluestacks.fb_height) + '"\n'
                    elif i.startswith(instance + '.fb_width'):
                        wLines += instance + '.fb_width="' + str(CONFIG.bluestacks.fb_width) + '"\n'
                    elif i.startswith(instance + '.dpi'):
                        wLines += instance + '.dpi="' + str(CONFIG.bluestacks.dpi) + '"\n'
                    elif i.startswith(instance + '.gl_win_screen'):
                        wLines += instance + '.gl_win_screen="' + str(CONFIG.bluestacks.gl_win_screen) + '"\n'
                    else:
                        wLines += i
                f.write(wLines)
        if CONFIG.bluestacks.path:
            os.popen('"' + CONFIG.bluestacks.path + '"')


def after_connect():
    if CONFIG.bluestacks:
        if CONFIG.bluestacks.check_config:
            with open(CONFIG.bluestacks.bluestacks_conf, 'r+', encoding='utf-8') as f:
                f.write(old_bluestacks)
        kill_emulator_bluestacks()
