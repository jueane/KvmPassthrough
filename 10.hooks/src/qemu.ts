#!/usr/bin/env bun

import { $ } from "bun";
import { existsSync, readFileSync, appendFileSync } from "fs";
import { dirname } from "path";

// 切换到脚本所在目录
const scriptDir = dirname(import.meta.path.replace("file://", ""));
process.chdir(scriptDir);

// 从命令行参数获取虚拟机名称和 libvirt 任务
const guestName = process.argv[2];
const libvirtTask = process.argv[3];

if (!guestName || !libvirtTask) {
  console.error("Usage: qemu.ts <guest_name> <libvirt_task>");
  process.exit(1);
}

// 类型断言：经过上面的检查，这两个变量肯定不是 undefined
const vmName: string = guestName;
const taskName: string = libvirtTask;

// 日志文件路径
const LOG_FILE = "/var/log/libvirt/hooks.log";

/**
 * 写入日志到文件
 * @param message 日志消息
 */
function logToFile(message: string): void {
  try {
    appendFileSync(LOG_FILE, message + "\n");
  } catch (error) {
    // 如果无法写入日志文件，忽略错误（可能是权限问题）
  }
}

/**
 * 同时输出到控制台和日志文件
 * @param message 消息
 */
function log(message: string): void {
  console.log(message);
  logToFile(message);
}

const enabledVideoProcessor = false;

// 需要 GPU 直通的虚拟机列表
const passthroughVmNames = ["win11", "win10", "ubuntu", "manjaro", "win7"];

// 判断是否需要 GPU 直通
const needPassthrough = passthroughVmNames.includes(vmName);

/**
 * 检查指定进程是否存在
 * @param processName 进程名称
 * @returns 进程 PID，不存在返回 -1
 */
async function checkProcessExists(processName: string): Promise<number> {
  try {
    // 使用 pgrep 查找进程
    const result = await $`pgrep -x ${processName}`.quiet();
    const output = result.stdout.toString().trim();

    if (output) {
      const firstLine = output.split('\n')[0];
      if (firstLine) {
        const pid = parseInt(firstLine);
        return pid;
      }
    }
    return -1;
  } catch (error) {
    // pgrep 找不到进程时会返回非零退出码
    return -1;
  }
}

/**
 * 打开 GUI
 */
async function openGui(): Promise<void> {
  return; // 当前已禁用

  await sleep(5000);
  log("OpenGUI");
  await $`startx`.quiet();
}

/**
 * 关闭 GUI
 */
async function closeGui(): Promise<void> {
  return; // 当前已禁用

  log("CloseGUI");

  // const guiProcessName = "xinit";
  const guiProcessName = "Xorg";

  // 检查进程是否存在
  let pid = await checkProcessExists(guiProcessName);

  if (pid > 0) {
    log(`Process ${guiProcessName} exist`);

    // 发送 SIGTERM 信号 (15)
    try {
      process.kill(pid, 15);
    } catch (error) {
      logToFile(`Failed to kill process ${pid}: ${error}`);
    }

    let waitCount = 0;
    while (true) {
      waitCount++;

      // 检查进程是否存在
      pid = await checkProcessExists(guiProcessName);

      if (pid > 0) {
        await sleep(1000);
        log(`Waiting for ${guiProcessName}`);
        continue;
      } else {
        log(`Process ${guiProcessName} terminated`);
        await sleep(3000);
        break;
      }
    }
  } else {
    log(`Process ${guiProcessName} not exist`);
    await sleep(500);
  }
}

/**
 * 创建快照
 * @param guestName 虚拟机名称
 */
async function createSnapshot(guestName: string): Promise<void> {
  const dataset = `/jdata/vdisk/${guestName}`;

  if (existsSync(dataset)) {
    log(`路径 ${dataset} 存在`);
    const cmd = `/jdata/develop/AutoSnapshot/SnapshotHelper.py snap ${dataset}`;
    log(cmd);
    await $`${cmd}`.quiet();
  } else {
    log(`路径 ${dataset} 不存在`);
  }
}

/**
 * 检查 nvidia 内核模块是否已加载
 * @returns 是否已加载
 */
function checkNvidiaModuleLoaded(): boolean {
  try {
    const content = readFileSync("/proc/modules", "utf-8");
    const lines = content.split('\n');

    for (const line of lines) {
      if (line.trim() === '') continue;

      const moduleName = line.split(/\s+/)[0];
      if (moduleName && moduleName.toLowerCase().includes("nvidia")) {
        return true;
      }
    }
    return false;
  } catch (error) {
    log("/proc/modules文件不存在，可能不是Linux系统或者系统存在异常");
    return false;
  }
}

/**
 * 准备阶段处理 (虚拟机启动前)
 */
async function onPrepare(): Promise<void> {
  // 检查 nvidia 模块
  if (checkNvidiaModuleLoaded()) {
    log("已加载含nvidia的内核模块");
  } else {
    log("未加载含nvidia的内核模块");
  }

  // 暂时去掉开机快照，防止创建不必要的快照
  // await createSnapshot(guestName);

  if (needPassthrough) {
    await closeGui();
    // await $`modprobe -r nvidia_drm`.quiet();
    // await $`modprobe -r nvidia_uvm`.quiet();
    // await $`modprobe -r nvidia`.quiet();
  }
}

/**
 * 释放阶段处理 (虚拟机关闭后)
 */
async function onRelease(): Promise<void> {
  if (needPassthrough) {
    // await $`modprobe nvidia`.quiet();
    // await $`modprobe nvidia_uvm`.quiet();
    // await $`modprobe nvidia_drm`.quiet();
    await openGui();
  }
}

/**
 * QEMU 进程处理主函数
 */
async function qemuProcess(): Promise<void> {
  const now = new Date().toISOString();
  const message = `${now}: ${vmName} ${taskName}, passthrough:${needPassthrough}`;

  // 写入日志文件头部
  logToFile("");
  logToFile(`Date: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`);
  logToFile(`Command: ./qemu.ts "${vmName}" "${taskName}"`);

  log(message);

  if (taskName.includes("prepare")) {
    await onPrepare();
  } else if (taskName.includes("release")) {
    await onRelease();
  }
}

/**
 * 睡眠函数
 * @param ms 毫秒数
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 主执行流程
try {
  await qemuProcess();
  log("-----------------------end---------------------------");
  logToFile(""); // 添加空行分隔
} catch (error) {
  const errorMsg = `Error occurred: ${error}`;
  console.error(errorMsg);
  logToFile(errorMsg);
  logToFile("");
  process.exit(1);
}
