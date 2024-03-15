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
    return
    time.sleep(5)
    print('OpenGUI')
    os.system('startx')


def close_gui():
    return
    print('CloseGUI')
    exist = False

    # gui_process_name = "xinit"
    gui_process_name = 'Xorg'

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
    cmd = f'/jdata/develop/AutoSnapshot/zfs/data_snap.py ' + guest_name
    print(cmd)
    os.system(cmd)
    if need_passthrough:
        close_gui()


def on_release():
    if need_passthrough:
        open_gui()


def qemu_process():
    print(f'{datetime.now()}: {guest_name} {libvirt_task}, passthrough:{need_passthrough}')

    if libvirt_task.__contains__('prepare'):
        on_prepare()
    elif libvirt_task.__contains__('release'):
        on_release()


qemu_process()
