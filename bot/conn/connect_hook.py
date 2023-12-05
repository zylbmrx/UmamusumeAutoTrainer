import os
import time

from bot.conn.kill_emulator_bluestacks import kill_emulator_bluestacks
from config import CONFIG

old_bluestacks = ''
cfg_changed = False

def before_connect():
    global old_bluestacks
    global cfg_changed
    wLines = ''

    if CONFIG.bluestacks:
        if CONFIG.bluestacks.check_config:
            instance = CONFIG.bluestacks.instance
            with (open(CONFIG.bluestacks.bluestacks_conf, 'r', encoding='utf-8') as f):
                lines = f.readlines()

                with (open(CONFIG.bluestacks.bluestacks_conf+'.bak', 'w', encoding='utf-8') as bak):
                    bak.write(''.join(lines))

                for i in lines:
                    old_bluestacks += i
                    if i.startswith(instance + '.fb_height'):
                        fb_height = int(i.split('="')[1].split('"\n')[0])
                        wLines += instance + '.fb_height="' + str(CONFIG.bluestacks.fb_height) + '"\n'
                    elif i.startswith(instance + '.fb_width'):
                        fb_width = int(i.split('="')[1].split('"\n')[0])
                        wLines += instance + '.fb_width="' + str(CONFIG.bluestacks.fb_width) + '"\n'
                    elif i.startswith(instance + '.dpi'):
                        dpi = int(i.split('="')[1].split('"\n')[0])
                        wLines += instance + '.dpi="' + str(CONFIG.bluestacks.dpi) + '"\n'
                    elif i.startswith(instance + '.gl_win_screen'):
                        gl_win_screen = i.split('="')[1].split('"\n')[0]
                        wLines += instance + '.gl_win_screen="' + str(CONFIG.bluestacks.gl_win_screen) + '"\n'
                    else:
                        wLines += i
                if fb_height != CONFIG.bluestacks.fb_height or fb_width != CONFIG.bluestacks.fb_width or \
                        dpi != CONFIG.bluestacks.dpi or gl_win_screen != CONFIG.bluestacks.gl_win_screen:
                    cfg_changed = True

            if cfg_changed:
                print('蓝叠模拟器配置文件需要修改...')
                kill_emulator_bluestacks()
                with open(CONFIG.bluestacks.bluestacks_conf, 'w', encoding='utf-8') as f:
                    f.write(wLines)

        if CONFIG.bluestacks.path:
            os.popen('"' + CONFIG.bluestacks.path + '"')
            print('启动蓝叠模拟器...等待5秒...')
            # 可以检测单没必要
            time.sleep(5)


def after_connect():
    if CONFIG.bluestacks:
        if CONFIG.bluestacks.check_config and cfg_changed:
            kill_emulator_bluestacks()
            # TODO 校验是否可以直接覆盖
            with open(CONFIG.bluestacks.bluestacks_conf, 'w', encoding='utf-8') as f:
                f.write(old_bluestacks)
        elif CONFIG.bluestacks.close_bluestacks:
            # 是否需要关闭蓝叠模拟器
            kill_emulator_bluestacks()
