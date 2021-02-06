#!/bin/bash
# To check the output of the called script access the syslog with: cat /var/log/syslog
lines=$(ps -ef | grep removeoldvideosgdrive.sh | wc -l)

if [ $lines -ne 2 ]; then
    bash /home/pi/scripts/removeoldvideosgdrive.sh 2>&1 | logger &
fi