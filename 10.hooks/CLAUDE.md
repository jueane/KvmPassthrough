# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 KVM/QEMU 虚拟机的 libvirt hooks 系统,用于管理 GPU 直通 (GPU Passthrough)。当虚拟机启动/停止时,自动执行 GPU 绑定/解绑操作,使宿主机的 GPU 可以被虚拟机独占使用。

**关键概念:**
- **libvirt hooks**: libvirt 的钩子机制,在虚拟机生命周期事件时自动执行脚本
- **GPU Passthrough**: 将物理 GPU 直接分配给虚拟机使用,提供接近原生的图形性能
- **VFIO**: 虚拟功能 I/O,Linux 内核提供的设备直通框架

## 运行环境

- **运行时**: Bun (JavaScript/TypeScript runtime)
- **部署位置**: `/etc/libvirt/hooks/qemu` (libvirt hooks 标准路径)
- **日志文件**: `/var/log/libvirt/hooks.log`
- **目标虚拟机**: win11, win10, ubuntu, manjaro, win7 (在 qemu.py:13 定义)

## 核心架构

### 执行流程

```
libvirt 事件触发
    ↓
/etc/libvirt/hooks/qemu (Bash wrapper)
    ↓
qemu.py (Python 主逻辑)
    ↓
vfio-startup.sh / vfio-teardown.sh (GPU 绑定/解绑)
```

### 文件说明

- **qemu** (Bash): libvirt hooks 入口点,记录日志并调用 qemu.py
- **qemu.py** (Python): 主逻辑控制器
  - 检查虚拟机名称是否需要 GPU 直通
  - 在 `prepare` 阶段关闭宿主机 GUI、卸载 nvidia 驱动
  - 在 `release` 阶段重新加载 nvidia 驱动、启动 GUI
  - 包含快照创建功能(当前已禁用)
- **qemu.ts** (TypeScript): 测试/开发用的 TS 版本实现
- **vfio-startup.sh**: GPU 解绑脚本
  - 解绑 VT 控制台和 EFI framebuffer
  - 卸载 nvidia 驱动模块
  - 加载 VFIO 内核模块
  - 将 GPU 从宿主机分离
- **vfio-teardown.sh**: GPU 重新绑定脚本
  - 卸载 VFIO 模块
  - 重新绑定 GPU 到宿主机
  - 加载 nvidia 驱动
  - 恢复 VT 控制台

## 常用命令

### 开发与测试

```bash
# 安装依赖
bun install

# 运行 TypeScript 版本 (测试用)
bun run qemu.ts

# 类型检查
bun tsc --noEmit
```

### 部署到系统

```bash
# 将 qemu 脚本链接/复制到 libvirt hooks 目录
sudo cp qemu /etc/libvirt/hooks/qemu
sudo chmod +x /etc/libvirt/hooks/qemu

# 确保 Python 脚本可执行
chmod +x qemu.py vfio-startup.sh vfio-teardown.sh
```

### 调试与日志

```bash
# 查看 hooks 执行日志
tail -f /var/log/libvirt/hooks.log

# 检查 nvidia 模块是否加载
lsmod | grep nvidia

# 检查 VFIO 模块是否加载
lsmod | grep vfio

# 查看 GPU 设备绑定状态
virsh nodedev-list --tree
```

### 虚拟机操作

```bash
# 启动虚拟机 (会触发 prepare hooks)
virsh start win11

# 关闭虚拟机 (会触发 release hooks)
virsh shutdown win11

# 强制停止虚拟机
virsh destroy win11
```

## 重要实现细节

### GPU 设备 PCI 地址

在 vfio-startup.sh 和 vfio-teardown.sh 中硬编码:
- GPU: `pci_0000_01_00_0`
- GPU Audio: `pci_0000_01_00_1`

**修改时需要同步更新两个脚本中的设备地址。**

### 虚拟机名称配置

需要 GPU 直通的虚拟机列表在 `qemu.py:13` 定义:
```python
passthrough_vm_names = ["win11", "win10", "ubuntu", "manjaro", "win7"]
```

添加新虚拟机时需修改此列表。

### 快照功能

代码中包含开机快照功能 (`create_snapshot`),但当前已禁用 (qemu.py:85):
```python
# 暂时去掉开机快照,防止创建不必要的快照
# create_snapshot(guest_name)
```

快照依赖外部工具: `/jdata/develop/AutoSnapshot/SnapshotHelper.py`

### GUI 管理

`open_gui()` 和 `close_gui()` 函数当前已禁用 (函数开头 return)。
原本用于在 GPU 直通前关闭宿主机图形界面,避免资源冲突。

## 注意事项

1. **系统权限**: hooks 脚本需要 root 权限执行 (由 libvirtd 服务调用)
2. **时序敏感**: vfio-startup.sh 中有 5 秒延迟,vfio-teardown.sh 有 10 秒延迟,用于避免竞态条件
3. **错误处理**: 当前实现较为简单,建议增强错误处理和回滚机制
4. **安全性**: 脚本使用 `set -x` 调试模式,生产环境可考虑移除
5. **硬件依赖**: 需要 CPU 和主板支持 IOMMU (Intel VT-d / AMD-Vi)

## TypeScript 配置

项目使用严格的 TypeScript 配置 (详见 tsconfig.json):
- 启用 `strict` 模式
- `noUncheckedIndexedAccess: true` - 索引访问需要检查 undefined
- `noImplicitOverride: true` - 重写方法需要 `override` 修饰符
- `verbatimModuleSyntax: true` - 需要显式使用 `import type`
