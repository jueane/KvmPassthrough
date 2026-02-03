# KVM/QEMU GPU Passthrough Hooks

这是一个用于 KVM/QEMU 虚拟机的 libvirt hooks 系统，实现 GPU 直通 (GPU Passthrough) 的自动化管理。当虚拟机启动/停止时，自动执行 GPU 绑定/解绑操作，使宿主机的 GPU 可以被虚拟机独占使用。

## 项目概述

**核心功能：**
- 虚拟机启动前：自动解绑 GPU 驱动、加载 VFIO 模块
- 虚拟机关闭后：自动重新绑定 GPU、恢复宿主机图形
- 支持多个虚拟机配置
- 自动日志记录到 `/var/log/libvirt/hooks.log`

**技术栈：**
- 运行时：[Bun](https://bun.com) - 快速的 JavaScript/TypeScript 运行时
- 主脚本：TypeScript (qemu.ts)
- 辅助脚本：Bash (vfio-startup.sh, vfio-teardown.sh)

## 快速开始

### 1. 安装依赖

```bash
bun install
```

### 2. 配置虚拟机列表

编辑 `src/qemu.ts` 文件，修改需要 GPU 直通的虚拟机列表：

```typescript
const passthroughVmNames = ["win11", "win10", "ubuntu", "manjaro", "win7"];
```

### 3. 配置 GPU PCI 地址

编辑 `vfio-startup.sh` 和 `vfio-teardown.sh`，修改你的 GPU PCI 地址：

```bash
# 查看你的 GPU PCI 地址
lspci -nn | grep -i nvidia

# 在脚本中修改这些行
virsh nodedev-detach pci_0000_01_00_0  # GPU
virsh nodedev-detach pci_0000_01_00_1  # GPU Audio
```

### 4. 部署到系统

```bash
# 赋予执行权限
chmod +x src/qemu.ts
chmod +x vfio-startup.sh
chmod +x vfio-teardown.sh

# 部署到 libvirt hooks 目录
sudo cp src/qemu.ts /etc/libvirt/hooks/qemu
sudo cp vfio-startup.sh /etc/libvirt/hooks/
sudo cp vfio-teardown.sh /etc/libvirt/hooks/

# 或者使用符号链接（便于开发调试）
sudo ln -sf $(pwd)/src/qemu.ts /etc/libvirt/hooks/qemu
sudo ln -sf $(pwd)/vfio-startup.sh /etc/libvirt/hooks/
sudo ln -sf $(pwd)/vfio-teardown.sh /etc/libvirt/hooks/

# 重启 libvirtd 服务
sudo systemctl restart libvirtd
```

## 开发与测试

### 运行测试

```bash
# 测试脚本（不会实际执行 GPU 操作，因为相关功能已禁用）
./src/qemu.ts win11 prepare/begin
./src/qemu.ts win11 release/end

# 查看日志输出
tail -f /var/log/libvirt/hooks.log
```

### 类型检查

```bash
bunx tsc --noEmit
```

### 调试命令

```bash
# 查看 nvidia 模块加载状态
lsmod | grep nvidia

# 查看 VFIO 模块加载状态
lsmod | grep vfio

# 查看 GPU 设备绑定状态
virsh nodedev-list --tree

# 查看 libvirt hooks 日志
tail -f /var/log/libvirt/hooks.log
```

## 文件说明

### 核心文件

- **src/qemu.ts** - 主控制脚本（TypeScript 实现）
    - 检查虚拟机是否需要 GPU 直通
    - 在 prepare 阶段调用 vfio-startup.sh
    - 在 release 阶段调用 vfio-teardown.sh
    - 记录所有操作日志

- **vfio-startup.sh** - GPU 解绑脚本
    - 解绑 VT 控制台和 EFI framebuffer
    - 卸载 nvidia 驱动模块
    - 加载 VFIO 内核模块
    - 将 GPU 从宿主机分离

- **vfio-teardown.sh** - GPU 重新绑定脚本
    - 卸载 VFIO 模块
    - 重新绑定 GPU 到宿主机
    - 加载 nvidia 驱动
    - 恢复 VT 控制台

### 配置文件

- **tsconfig.json** - TypeScript 配置
- **package.json** - 项目依赖配置

## 虚拟机操作

```bash
# 启动虚拟机（会自动触发 GPU 直通）
virsh start win11

# 关闭虚拟机（会自动恢复 GPU）
virsh shutdown win11

# 强制停止虚拟机
virsh destroy win11

# 查看虚拟机状态
virsh list --all
```

## 工作原理

```
libvirt 虚拟机事件
    ↓
/etc/libvirt/hooks/qemu (src/qemu.ts)
    ↓
检查虚拟机是否在直通列表中
    ↓
prepare 阶段 → vfio-startup.sh  → 解绑 GPU
release 阶段 → vfio-teardown.sh → 绑定 GPU
    ↓
记录日志到 /var/log/libvirt/hooks.log
```

## 系统要求

### 硬件要求

- CPU 和主板支持 IOMMU（Intel VT-d 或 AMD-Vi）
- 至少一个支持直通的 GPU
- 建议：双 GPU 配置（一个给宿主机，一个给虚拟机）

### 软件要求

- Linux 系统（已测试：Arch Linux, Manjaro）
- libvirt 和 QEMU/KVM
- Bun 运行时
- VFIO 内核模块支持

### 启用 IOMMU

编辑 GRUB 配置：

```bash
# Intel CPU
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu=pt"

# AMD CPU
GRUB_CMDLINE_LINUX_DEFAULT="amd_iommu=on iommu=pt"

# 更新 GRUB
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

## 注意事项

1. **权限要求**：hooks 脚本需要 root 权限执行（由 libvirtd 服务自动调用）
2. **时序敏感**：脚本中包含延迟等待，避免竞态条件
3. **备份重要**：首次使用前建议备份虚拟机和系统配置
4. **测试环境**：建议先在测试环境中验证配置
5. **日志监控**：部署后监控日志文件，确保正常运行

## 常见问题

### GPU 直通失败

```bash
# 检查 IOMMU 是否启用
dmesg | grep -i iommu

# 检查 IOMMU 分组
find /sys/kernel/iommu_groups/ -type l

# 检查 vfio-pci 是否绑定成功
lspci -nnk -d 10de:  # NVIDIA GPU
```

### 虚拟机无法启动

```bash
# 查看详细错误信息
virsh start win11 --console

# 查看 libvirt 日志
sudo journalctl -u libvirtd -f
```

### 宿主机图形无法恢复

如果虚拟机关闭后宿主机图形无法恢复：

```bash
# 手动重新加载 nvidia 驱动
sudo modprobe nvidia
sudo modprobe nvidia_modeset
sudo modprobe nvidia_uvm
sudo modprobe nvidia_drm

# 重启显示管理器
sudo systemctl restart display-manager
```

## 项目结构

```
10.hooks/
├── src/
│   └── qemu.ts          # 主控制脚本 (TypeScript)
├── vfio-startup.sh      # GPU 解绑脚本
├── vfio-teardown.sh     # GPU 绑定脚本
├── package.json         # 项目配置
├── tsconfig.json        # TypeScript 配置
├── README.md            # 项目文档
├── CLAUDE.md            # AI 辅助开发文档
└── AGENTS.md            # 代码风格指南
```

## 开发规范

项目使用严格的 TypeScript 配置：
- 代码缩进使用 4 个空格
- 启用 `strict` 模式
- 所有索引访问需要检查 `undefined`
- 需要显式使用 `import type` 导入类型

更多详细信息请参考 [CLAUDE.md](./CLAUDE.md) 和 [AGENTS.md](./AGENTS.md)。

## 参考资源

- [libvirt Hooks Documentation](https://libvirt.org/hooks.html)
- [VFIO GPU Passthrough Guide](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF)
- [Bun Documentation](https://bun.sh/docs)

## License

本项目仅供学习和个人使用。
