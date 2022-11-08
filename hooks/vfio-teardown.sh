#!/bin/bash
set -x
  
# Re-Bind GPU to Nvidia Driver
virsh nodedev-reattach pci_0000_01_00_0
virsh nodedev-reattach pci_0000_01_00_1

# Reload nvidia modules
# modprobe nvidia
# modprobe nvidia_modeset
# modprobe nvidia_uvm
# modprobe nvidia_drm
modprobe nouveau

# Rebind VT consoles
echo 1 > /sys/class/vtconsole/vtcon0/bind
# Some machines might have more than 1 virtual console. Add a line for each corresponding VTConsole
#echo 1 > /sys/class/vtconsole/vtcon1/bind

nvidia-xconfig --query-gpu-info > /dev/null 2>&1
echo vesa-framebuffer.0 > /sys/bus/platform/drivers/vesa-framebuffer/bind

# Restart Display Manager
# systemctl start display-manager.service
