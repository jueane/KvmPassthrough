# 无图形界面安装虚拟机使用cockpit最为方便
安装cockpit cockpit-machines
pacman -S cockpit cockpit-machines

# 允许root登录:
/etc/cockpit/disallowed-users 注释掉root。

# 合建虚拟机的过程中，无法访问win10镜像iso：
设置iso文件为a+rwx即可。

# 创建虚拟机后，关闭安全启动：
    1.<os>
        <firmware>
            <feature enabled='no' name='secure-boot'/>   这里改成no。

    2.修改OVMF配置
    <loader readonly='yes' secure='yes' type='pflash' format='raw'>/usr/share/edk2/x64/OVMF_CODE.secboot.4m.fd</loader>
    改为：
    <loader readonly='yes' secure='no' type='pflash' format='raw'>/usr/share/edk2/x64/OVMF_CODE.4m.fd</loader>

# 正常安装win虚拟机
在cockpit的vnc远程管理中配置好windows的网络连接。
开启远程桌面，之后直接在远程桌面操作。


# 安装virtio-win驱动（可选）
https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso

