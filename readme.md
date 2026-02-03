libvirt钩子配置：

`/etc/libvirt/hooks/qemu`
```shell
[root@h /etc/libvirt/hooks]# l
total 4.0K
lrwxrwxrwx 1 root root 43 Sep  2  2023 qemu -> /jdata/develop/KvmPassthrough/10.hooks/qemu
```

`/jdata/develop/KvmPassthrough/10.hooks/qemu`
```shell
#!/bin/bash

guest_name="$1"
libvirt_task="$2"

# 获取脚本所在的目录
script_dir=$(dirname "$(readlink -f "$BASH_SOURCE")")

# 获取当前日期和时间
current_date=$(date '+%Y-%m-%d %H:%M:%S')

cd "$script_dir"
command="./qemu.py \"$guest_name\" \"$libvirt_task\""
echo "" >> /var/log/libvirt/hooks.log
echo "Date: $current_date" >> /var/log/libvirt/hooks.log
echo "Command: $command" >> /var/log/libvirt/hooks.log
eval "$command" >> /var/log/libvirt/hooks.log 2>&1 # 将输出写入日志文件
echo "" >> /var/log/libvirt/hooks.log
```


