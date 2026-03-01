# KVM/libvirt 虚拟化配置文档

本文档记录了本机所有 KVM 和 libvirt 相关的自定义配置，方便后续维护和参考。

## 目录
- [系统概览](#系统概览)
- [主要配置文件](#主要配置文件)
- [虚拟机清单](#虚拟机清单)
- [GPU直通配置](#gpu直通配置)
- [性能优化](#性能优化)
- [网络配置](#网络配置)
- [存储配置](#存储配置)
- [自定义Hook系统](#自定义hook系统)
- [系统服务](#系统服务)
- [安全配置](#安全配置)
- [故障排除](#故障排除)
- [备份和恢复](#备份和恢复)

---

## 系统概览

### 虚拟化环境状态
- **虚拟化平台**: KVM/QEMU with libvirt
- **管理工具**: virt-manager, virsh
- **当前运行VM**: 2台 (openwrtimt, win10)
- **已定义VM总数**: 12台
- **存储位置**: `/jdata/vdisk/`
- **配置仓库**: `/jdata/develop/KvmPassthrough/` (Git管理)

### 硬件环境
- **CPU**: Intel (支持VMX硬件虚拟化)
- **主板**: Z790平台
- **内存**: 支持大页面配置
- **GPU**: 支持VFIO直通

---

## 主要配置文件

### libvirt 配置目录
```
/etc/libvirt/
├── qemu/
│   ├── android.xml              # Android虚拟机
│   ├── docker.xml               # Docker虚拟机
│   ├── ikuai.xml                # 爱快软路由
│   ├── mac13.xml                # macOS 13
│   ├── mac14.xml                # macOS 14
│   ├── msdos.xml                # MS-DOS虚拟机
│   ├── mykernel.xml             # 内核开发环境
│   ├── openwrt.xml              # OpenWrt路由器
│   ├── openwrtimt.xml           # OpenWrt IMT版本 (运行中)
│   ├── win10.xml                # Windows 10 (运行中)
│   ├── win11.xml                # Windows 11
│   └── win7.xml                 # Windows 7
├── storage/
│   ├── default.xml              # 默认存储池
│   └── nvram.xml                # NVRAM存储池
└── networks/                    # 网络配置
    └── autostart/               # 自启动网络
```

### 系统配置文件
```
/etc/modprobe.d/
├── kvm.conf                     # KVM模块配置
└── vfio.conf                    # VFIO配置

/etc/sysctl.d/
└── 10-kvm-hugepages.conf        # 大页面配置

/etc/libvirt/hooks/
└── qemu -> /jdata/develop/KvmPassthrough/10.hooks/qemu.py
```

---

## 虚拟机清单

### 当前运行状态
| VM名称 | 状态 | 用途 | 主要配置 |
|--------|------|------|----------|
| openwrtimt | 运行中 | 软路由IMT版 | 2GB内存, virtio设备 |
| win10 | 运行中 | Windows 10 | 8GB内存, GPU直通 |

### 已关机虚拟机
| VM名称 | 用途 | 内存 | 存储 | 特色配置 |
|--------|------|------|------|----------|
| android | Android开发 | 4GB | qcow2 | GPU直通支持 |
| docker | Docker容器环境 | 4GB | qcow2 | 嵌套虚拟化 |
| ikuai | 爱快软路由 | 2GB | qcow2 | 双网段支持 |
| mac13 | macOS 13 | 8GB | qcow2 | GPU直通 |
| mac14 | macOS 14 | 8GB | qcow2 | GPU直通 |
| msdos | 经典游戏 | 512MB | qcow2 | 音频直通 |
| mykernel | 内核开发 | 2GB | qcow2 | 调试支持 |
| openwrt | OpenWrt标准版 | 1GB | qcow2 | 路由功能 |
| win11 | Windows 11 | 16GB | qcow2 | GPU直通 |
| win7 | Windows 7 | 4GB | qcow2 | 兼容性测试 |

---

## GPU直通配置

### VFIO 配置文件

#### `/etc/modprobe.d/kvm.conf`
```conf
# KVM虚拟化模块配置
options kvm_intel nested=1
options kvm_intel emulate_invalid_guest_state=0
options kvm ignore_msrs=1
```

#### `/etc/modprobe.d/vfio.conf`
```conf
# VFIO直通配置
options vfio-pci ids=10de:2504,10de:228b
options vfio-pci disable_vga=1
```

### 直通设备标识
- **GPU**: NVIDIA显卡 (10de:2504, 10de:228b)
- **IOMMU组**: 已分组支持设备隔离
- **中断处理**: 自定义中断分配策略

### GPU直通脚本

#### 设备解绑脚本
```bash
# GPU解绑和VFIO绑定
echo 1 > /sys/class/vtconsole/vtcon0/bind
# ... 解绑控制台
echo "vfio-pci" > /sys/bus/pci/devices/0000:01:00.0/driver_override
# ... 绑定到VFIO
```

#### 设备重新绑定脚本
```bash
# 重新绑定到宿主机驱动
echo "nvidia" > /sys/bus/pci/devices/0000:01:00.0/driver_override
# ... 重新加载NVIDIA驱动
```

---

## 性能优化

### 大页面配置

#### `/etc/sysctl.d/10-kvm-hugepages.conf`
```conf
# 16GB大页面配置 (1GB页面)
vm.nr_hugepages = 16384
vm.hugetlb_shm_group = 108
vm.overcommit_memory = 1
```

#### 大页面挂载
```bash
# /dev/hugepages 挂载配置
none /dev/hugepages hugetlbfs mode=1770,gid=108 0 0
```

### CPU优化
- **CPU模式**: host-passthrough (最大性能)
- **vCPU绑定**: 针对关键VM启用CPU亲和性
- **IO线程**: 独立IO线程提升磁盘性能
- **嵌套虚拟化**: Intel VT-x支持

### 内存优化
- **内存预留**: 避免内存交换
- **内存超分**: 控制内存超分比例
- **NUMA感知**: 针对NUMA架构优化

---

## 网络配置

### 桥接网络
```
br0: 10.0.0.2/24
├── eno2 (物理网卡)
├── vnet0 (openwrtimt)
├── vnet7 (win10)
└── 其他vnet接口
```

### 网络特性
- **Virtio网络**: 全virtio网络设备
- **SR-IOV**: 支持单根I/O虚拟化
- **VLAN**: 支持VLAN标签
- **QoS**: 网络质量控制

### 防火墙配置
```bash
# libvirt防火墙规则
-n libvirt-out -m comment --comment "libvirt outgoing" -j ACCEPT
-n libvirt-in -m comment --comment "libvirt incoming" -j ACCEPT
```

---

## 存储配置

### 主要存储位置
```
/jdata/vdisk/
├── android/
├── docker/
├── ikuai/
├── macos13/
├── macos14/
├── manjaro/
├── msdos/
├── openwrt/
├── openwrtimt/
├── win10/
├── win11/
├── win7/
├── __win10_tpl/
├── __win10_ltsc_tpl/
└── __linux_tpl/
```

### 存储池类型
- **default**: 默认存储池
- **nvram**: NVRAM存储
- **win10**: Windows 10专用存储
- **Downloads**: 下载镜像存储
- **Systems**: 系统镜像存储

### 磁盘格式特性
- **QCOW2**: 支持快照和压缩
- **RAW**: 高性能原生格式
- **写时复制**: 节约存储空间
- **增量备份**: 支持增量链

---

## 自定义Hook系统

### Hook主程序
**位置**: `/jdata/develop/KvmPassthrough/10.hooks/qemu.py`

### Hook功能
- **事件监听**: 监听VM启动/停止事件
- **设备管理**: 自动绑定/解绑GPU设备
- **日志记录**: 详细操作日志
- **错误处理**: 异常恢复机制

### Hook事件类型
```python
# 支持的Hook事件
['prepare', 'start', 'started', 'stopped', 'release']
```

### 日志系统
- **日志位置**: `/var/log/libvirt/hooks.log`
- **日志格式**: 时间戳 + 事件 + 详细信息
- **日志轮转**: 自动轮转和压缩

---

## 系统服务

### libvirt 相关服务
```bash
# 主要服务
libvirtd.service              # libvirt主守护进程
virtlogd.service              # 虚拟化日志服务
virtqemud.service             # QEMU守护进程

# 辅助服务
libvirt-guests.service        # VM客人管理
libvirtd-admin.socket         # 管理套接字
libvirtd-ro.socket            # 只读套接字
```

### 自定义服务
```bash
# 防止休眠服务
prevent-sleep-during-vm.service    # VM运行时禁止休眠
```

### 服务状态管理
```bash
# 启动虚拟化服务
systemctl start libvirtd virtlogd

# 设置开机自启
systemctl enable libvirtd virtlogd
```

---

## 安全配置

### 用户权限
- **libvirt组**: kvm, libvirtd, input
- **权限控制**: 细粒度权限管理
- **SELinux**: 适当的SELinux上下文

### 网络安全
- **防火墙规则**: libvirt专用防火墙链
- **端口管理**: 动态端口分配
- **VPN支持**: 支持VPN隧道直通

### 数据保护
- **磁盘加密**: 支持LUKS加密
- **备份策略**: 自动化备份方案
- **访问控制**: 基于角色的访问控制

---

## 故障排除

### 常见问题诊断

#### GPU直通失败
```bash
# 检查VFIO模块
lsmod | grep vfio

# 检查IOMMU分组
find /sys/kernel/iommu_groups/ -name "devices"

# 检查设备绑定
lspci -nnk -d 10de:
```

#### VM启动失败
```bash
# 查看libvirt日志
journalctl -u libvirtd -f

# 查看VM日志
virsh domxml-to-native qemu-xml vmname
```

#### 网络问题
```bash
# 检查桥接状态
brctl show

# 检查veth连接
ip link show type veth
```

### 性能调试工具
- **virt-top**: VM性能监控
- **perf**: 系统性能分析
- **qemu-monitor**: QEMU监控界面

---

## 备份和恢复

### 配置备份策略
```bash
# 备份libvirt配置
tar -czf libvirt-config-$(date +%Y%m%d).tar.gz /etc/libvirt/

# 备份VM磁盘
rsync -av /jdata/vdisk/ /backup/vdisk/
```

### 虚拟机迁移
```bash
# 导出VM配置
virsh dumpxml vmname > vmname.xml

# 迁移磁盘镜像
qemu-img convert -f qcow2 -O qcow2 source.qcow2 dest.qcow2
```

### 灾难恢复
1. **恢复libvirt服务**
2. **导入VM配置**
3. **恢复存储池**
4. **验证网络配置**
5. **测试VM启动**

---

## 维护建议

### 定期维护任务
- **日志清理**: 定期清理过期日志
- **磁盘整理**: 定期整理磁盘碎片
- **备份验证**: 验证备份完整性
- **性能监控**: 监控系统性能指标

### 升级注意事项
- **内核升级**: 检查KVM模块兼容性
- **libvirt升级**: 配置文件兼容性检查
- **QEMU升级**: 新特性适配
- **驱动更新**: GPU直通驱动更新

---

## 技术参考

### 有用链接
- **libvirt官方文档**: https://libvirt.org/
- **KVM官方文档**: https://www.linux-kvm.org/
- **VFIO文档**: https://vfio.blogspot.com/

### 配置模板
所有自定义配置模板存储在: `/jdata/develop/KvmPassthrough/`

---

**文档创建时间**: 2026-01-31  
**最后更新**: 2026-01-31  
**维护者**: 系统管理员

---

*此文档持续更新，记录所有KVM/libvirt相关的自定义配置和变更*