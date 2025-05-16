# 开启虚拟化.
bios中开启虚拟化.

开启虚拟化：
Advanced -> Cpu Configure -> Intel virtual technology
开启VT-d:
Advanced -> System Agent(SA) Configure -> VT-d

# 添加内核参数
文件：/etc/default/grub。
找到 GRUB_CMDLINE_LINUX_DEFAULT 添加：
intel_iommu=on iommu=pt
或
intel_iommu=on iommu=pt default_hugepagesz=1G hugepagesz=1G hugepages=16
然后输入命令：
grub-mkconfig -o /boot/grub/grub.cfg
重启电脑。

# 检查iommu是否启用
dmesg | grep -e DMAR -e IOMMU
应该会看到大概15行的输出，其中一行是：
DMAR: IOMMU enabled
(如果只有这一行，可能是因为VT-d没有启用)

# 添加VFIO到内核模块
创建文件：
/etc/modprobe.d/vfio.conf
添加显卡的id：
options vfio-pci ids=10de:2503,10de:228e
options vfio-pci disable_idle_d3=1
options vfio-pci disable_vga=1
(需要重启)

# 安装虚拟机软件
pacman -S qemu-full libvirt virt-manager dnsmasq iptables-nft edk2-ovmf
(提示移除iptables选是)

# 自动启动服务 libvirtd virtlogd.socket
systemctl enable --now libvirtd
systemctl enable --now virtlogd.socket

# 创建网桥
在路径/etc/systemd/network中创建文件：
10-bridge.netdev
20-bridge.network
30-br0-static.network

>>>10-bridge.netdev 内容：
[NetDev]
Name=br0
Kind=bridge

>>> 20-bridge.network (注意改网卡名字)
[Match]
Name=enp6s0
[Network]
Bridge=br0

>>> 30-br0-static.network (注意改网段)
[Match]
Name=br0
[Network]
Address=192.168.20.70/24
Gateway=192.168.20.10
DNS=192.168.20.10

