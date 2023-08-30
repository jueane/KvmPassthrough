set -x

#sleep 1

modprobe -r vfio_pci
modprobe -r vfio
modprobe -r vfio_iommu_type1
modprobe -r vfio_virqfd
modprobe -r virtio_net
modprobe -r virtio_blk
modprobe -r virtio

virsh nodedev-reattach pci_0000_00_01_0
virsh nodedev-reattach pci_0000_01_00_0
virsh nodedev-reattach pci_0000_01_00_1

echo 1 > /sys/class/vtconsole/vtcon0/bind
echo 1 > /sys/class/vtconsole/vtcon1/bind

modprobe nvidia
modprobe nvidia_modeset
modprobe nvidia_uvm
modprobe nvidia_drm
modprobe drm_kms_helper
modprobe i2c_nvidia_gpu
modprobe drm

echo efi-framebuffer.0 > /sys/bus/platform/drivers/efi-framebuffer/bind

#sleep 1

#systemctl start gdm

#systemctl start getty@tty1

