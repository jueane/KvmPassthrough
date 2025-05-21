# 导入虚拟机
virsh define vm_template.xml
(如果创建出错，可以使用virsh undefine删除重建)

# 启动前配置
修改<domain><name>中的虚拟机名称

# 确认VNC端口与转发​​
virsh vncdisplay arch-test1
输出表示相对起始端口5900的偏移量。假如输出 :1，则VNC端口为 ​​5901​​（默认端口计算方式：5900 + 显示号）。
在本地使用vnc连接到宿主机的5901即可。

# 虚拟机系统安装完成后配置
修改启动顺序（将 <boot dev='cdrom'/> 改为 <boot dev='hd'/>）
删除CDROM设备：
<disk type='file' device='cdrom'>...</disk>
