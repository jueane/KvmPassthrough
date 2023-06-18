#!/usr/bin/python3
import os
import sys
import time
from datetime import datetime

guest_name = sys.argv[1]
libvirt_task = sys.argv[2]

enabled_video_processor = False

passthrough_vm_names = ['win11', 'win10', 'ubuntu', 'manjaro', 'win7']

need_passthrough = False
if guest_name in passthrough_vm_names:
    need_passthrough = True


def check_process_exists(process_name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == process_name:
            return process.pid
    return -1


def open_gui():
    print('OpenGUI')
    # os.system('startx')


def close_gui():
    print('CloseGUI')
    exist = False

    gui_process_name = "xinit"
    # gui_process_name = "htop"

    # 检查进程是否存在
    pid = check_process_exists(gui_process_name)
    if pid > 0:
        print(f"Process {gui_process_name} exist")
        os.kill(pid, 15)
        wait_count = 0
        while True:
            wait_count += 1
            # 检查Process是否存在
            pid = check_process_exists(gui_process_name)
            if pid > 0:
                time.sleep(1)
                print(f'Waiting for {gui_process_name}')
                continue
            else:
                print(f'Process {gui_process_name} terminated')
                time.sleep(3)
                break
    else:
        print(f"Process {gui_process_name} not exist")
        time.sleep(0.5)


def on_prepare():
    os.system('/jdata/develop/AutoSnapshot/zfs/data_snap.py ' + guest_name)
    if need_passthrough:
        pass
        close_gui()


def on_release():
    if need_passthrough:
        open_gui()


def qemu_process():
    print(f'{datetime.now()}: {guest_name} {libvirt_task}, passthrough:{need_passthrough}')

    if libvirt_task == 'prepare':
        on_prepare()
    elif libvirt_task == 'release':
        on_release()


qemu_process()
