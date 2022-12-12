#!/bin/bash
set -x


sleep 10


modprobe -r vfio_pci
modprobe -r vfio
modprobe -r vfio_iommu_type1
modprobe -r vfio_virqfd
  
# Re-Bind GPU to Nvidia Driver
virsh nodedev-reattach pci_0000_01_00_0
virsh nodedev-reattach pci_0000_01_00_1


# Rebind VT consoles
echo 1 > /etc/class/vtconsole/vtcon0/bind
echo 1 > /etc/class/vtconsole/vtcon1/bind

# Some machines might have more than 1 virtual console. Add a line for each corresponding VTConsole
#echo 1 > /sys/class/vtconsole/vtcon1/bind


# echo vesa-framebuffer.0 > /sys/bus/platform/drivers/vesa-framebuffer/bind
echo efi-framebuffer.0 > /sys/bus/platform/drivers/efi-framebuffer/bind


# modprobe nouveau
modprobe nvidia
modprobe nvidia_modeset
modprobe nvidia_uvm
modprobe nvidia_drm
modprobe drm_kms_helper
modprobe i2c_nvidia_gpu
modprobe drm

startx
# Restart Display Manager
# systemctl start display-manager.service
