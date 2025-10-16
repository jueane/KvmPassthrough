#!/usr/bin/python3
import os
import sys
import time
from datetime import datetime
import psutil

guest_name = sys.argv[1]
libvirt_task = sys.argv[2]

enabled_video_processor = False

passthrough_vm_names = ["win11", "win10", "ubuntu", "manjaro", "win7"]

need_passthrough = False
if guest_name in passthrough_vm_names:
    need_passthrough = True


def check_process_exists(process_name):
    for process in psutil.process_iter(["name"]):
        if process.info["name"] == process_name:
            return process.pid
    return -1


def open_gui():
    return
    time.sleep(5)
    print("OpenGUI")
    os.system("startx")


def close_gui():
    return
    print("CloseGUI")
    exist = False

    # gui_process_name = "xinit"
    gui_process_name = "Xorg"

    # 检查进程是否存在
    pid = check_process_exists(gui_process_name)
    if pid > 0:
        print(f"Process {gui_process_name} exist")
        os.kill(pid, 15)
        # os.system("pkill Xorg")
        wait_count = 0
        while True:
            wait_count += 1
            # 检查Process是否存在
            pid = check_process_exists(gui_process_name)
            if pid > 0:
                time.sleep(1)
                print(f"Waiting for {gui_process_name}")
                continue
            else:
                print(f"Process {gui_process_name} terminated")
                time.sleep(3)
                break
    else:
        print(f"Process {gui_process_name} not exist")
        time.sleep(0.5)


def create_snapshot(guest_name):
    dataset = f"/jdata/vdisk/{guest_name}"
    if os.path.exists(dataset):
        print(f"路径 {dataset} 存在")
        cmd = f"/jdata/develop/AutoSnapshot/SnapshotHelper.py snap {dataset}"
        print(cmd)
        os.system(cmd)
    else:
        print(f"路径 {dataset} 不存在")


def on_prepare():
    # check nvidia
    if check_nvidia_module_loaded():
        print("已加载含nvidia的内核模块")
    else:
        print("未加载含nvidia的内核模块")

    # 暂时去掉开机快照，防止创建不必要的快照
    # create_snapshot(guest_name)

    if need_passthrough:
        close_gui()
        # os.system("modprobe -r nvidia_drm")
        # os.system("modporbe -r nvidia_uvm")
        # os.system("modprobe -r nvidia")


def on_release():
    if need_passthrough:
        # os.system("modprobe nvidia")
        # os.system("modporbe nvidia_uvm")
        # os.system("modprobe nvidia_drm")
        open_gui()


def qemu_process():
    print(
        f"{datetime.now()}: {guest_name} {libvirt_task}, passthrough:{need_passthrough}"
    )

    if libvirt_task.__contains__("prepare"):
        on_prepare()
    elif libvirt_task.__contains__("release"):
        on_release()


def check_nvidia_module_loaded():
    try:
        with open("/proc/modules", "r") as f:
            content = f.read()
            lines = content.splitlines()
            for line in lines:
                module_name = line.split()[0]
                if "nvidia" in module_name.lower():
                    return True
            return False
    except FileNotFoundError:
        print("/proc/modules文件不存在，可能不是Linux系统或者系统存在异常")
        return False


qemu_process()
print("-----------------------end---------------------------")
