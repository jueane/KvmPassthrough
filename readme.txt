创建用户je


########################################

配置.xinitrc
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus

ibus-daemon -drx

export DESKTOP_SESSION=PLASMA
exec startplasma-x11

#export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1



########################################


安装包
pacman -S virt-manager virt-viewer qemu  edk2-ovmf vde2 ebtables dnsmasq bridge-utils openbsd-netcat libguestfs


