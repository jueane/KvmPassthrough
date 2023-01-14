aplay -l | awk -F \: '/,/{print $2}' | awk '{print $1}' | uniq

