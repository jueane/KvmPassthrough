# UEFI
>> efivar --list
​​如果输出 UEFI 变量列表​​（如 BootOrder、BootCurrent 等），则为 UEFI 模式。
>> dmesg | grep "EFI v"
如果输出类似 EFI vX.X 的信息，则为 UEFI 模式。
无输出则可能是 BIOS 模式。
# 分区
lsblk
fdisk /dev/xxx

>> ​​创建GPT分区表​​
g

>> 创建EFI分区（500MiB）​​
n → 回车（默认分区号） → 回车（默认起始扇区） → +500M  
t → 1（选择EFI类型） → 1（EFI System）

>> 创建Swap分区（4GiB）
n → 回车 → 回车 → +4G  
t → 2（分区号） → 19（Linux Swap）

>> 创建根分区（剩余空间）
n → 回车 → 回车 → 回车（使用全部剩余空间）

>> 保存并退出
w

>> 格式化
mkfs.fat -F32 /dev/sda1
mkswap /dev/sda2
swapon /dev/sda2
mkfs.btrfs /dev/sda3

>> 挂载
mount /dev/sda3 /mnt

>> 创建系统子卷
cd /mnt
btrfs subvolume create arch
umount /mnt

>> 重新挂载
mount -o subvol=arch /dev/sda3 /mnt
mkdir -p /mnt/boot
mount /dev/sda1 /mnt/boot

# 联网
>>> 创建文件/etc/systemd/network/18-wired.network (注意改网段)
[Match]
Name=en*
[Network]
Address=192.168.20.90/24
Gateway=192.168.20.10
DNS=114.114.114.114

# 安装必需的软件包
pacstrap -K /mnt base linux linux-firmware
(最后会看到报错error: command failed to execute correctly，忽视不管发现也没有问题)

# 生成 fstab 文件
genfstab -U /mnt > /mnt/etc/fstab

# chroot 到新安装的系统
arch-chroot /mnt

(后续内容全都是在arch-chroot中进行)

# 安装必须包
(arch-chroot之前已经配置了安装环境的网络，在此可以直接使用，然后再配置网络)
pacman -S vim openssh grub efibootmgr

# 配置网络
>> 创建文件
/etc/systemd/network/20.wired.network

>> 编辑内容：
[Match]
Name=en*
Name=eth*
[Network]
Address=192.168.20.14/24
Gateway=192.168.20.254

>> 配置DNS /etc/resolv.conf
nameserver 192.168.20.10

>> 网络服务配置
systemctl enable --now systemd-networkd
systemctl enable --now systemd-resolved

# 配置ssh
vim /etc/ssh/sshd_config
> 允许root登录（修改值）
PermitRootLogin yes
> 允许密码验证（arch中非必须）
PasswordAuthentication yes
> 配置服务
systemctl restart sshd
systemctl enable --now sshd
> 修改密码
passwd

# 在新系统中配置
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
hwclock --systohc

>> 编辑 /etc/locale.gen，然后取消掉 en_US.UTF-8 UTF-8 和其他需要的 UTF-8 区域设置前的注释（#）。
vim /etc/locale.gen
>> 接着执行 locale-gen 以生成 locale 信息：
locale-gen
> （可选）在终端中让 Git 正确显示中文，而不是显示编码（避免路径转义）：
执行命令：git config --global core.quotepath false


>> 创建 hostname 文件：
/etc/hostname

>> 设置root密码
passwd

# 安装引导
（确保已经 arch-chroot /mnt 进入新系统安装，否则会报错）
（前面已经安装了grub efibootmgr）
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=jgrub
grub-mkconfig -o /boot/grub/grub.cfg



# 安装桌面环境（可选）（未验证）
> 安装
pacman -S plasma xorg-server xorg-xinit dbus

> 创建普通用户je

> 配置.xinitrc
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus

ibus-daemon -drx

export DESKTOP_SESSION=PLASMA
exec startplasma-x11

#export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1

