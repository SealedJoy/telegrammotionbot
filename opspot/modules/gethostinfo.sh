# Script: gethostinfo.sh
# Purpose: Output various diagnostic information from a raspbian stretch server
# Author: Joseph Slade 2019
# -------------------------------------------------------
gpu="$(/opt/vc/bin/vcgencmd measure_temp | cut -d= -f2)"
cpu=$(</sys/class/thermal/thermal_zone0/temp)
cpufreq=$(</sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)
SFWVERSION="$(uname -a)"
OSREL="$(uname -v | cut -dP -f2)"
OSKER="$(uname -s -r)"
MACHINE="$(uname -m)"
ROOTUSAGE="$(df --output=pcent / | sed -n '2p')"
ROOTSIZE="$(df --output=size -h / | sed -n '2p')"
HDDUSAGE="$(df --output=pcent /mounthdd | sed -n '2p')"
HDDSIZE="$(df --output=size -h /mounthdd | sed -n '2p')"
ethip="$(hostname -I | awk '{print $1}' | grep 192)"
wifiip="$(hostname -I | awk '{print $2}' | grep 192)"
hostname="$(hostname)"
uptime="$(uptime | sed -E 's/^[^,]*up *//; s/, *[[:digit:]]* users.*//; s/min/minutes/; s/([[:digit:]]+):0?([[:digit:]]+)/\1 hours, \2 minutes/')"
load="$(uptime | awk '{print $NF}')"
echo "Hardware"
echo "--------------"
echo "GPU Temp: $gpu"
echo "CPU Temp: $((cpu/1000))'C"
echo "Version: $MACHINE"
echo "Frequency: $((cpufreq/1000))Mhz"
echo "Load Avg: $load / 4.00"
echo "Startup:$ROOTUSAGE  /$ROOTSIZE"
if [[ $(lsblk | grep sda) ]]; then
    echo "HDD:$HDDUSAGE  /$HDDSIZE"
else
    echo "HDD: Not Detected"
fi
echo ""
echo "Software"
echo "--------------"
echo "Uptime: $uptime"
echo "OS Release: $OSREL"
echo "Kernel: $OSKER"
echo "Time: $(date)"
echo ""
echo "Network"
echo "--------------"
echo "Hostname: $hostname"
echo "Eth: $ethip"
echo "Wifi: $wifiip"
echo ""
echo "Camera links"
echo "--------------"
echo "Eth Config http://$ethip:8765"
echo "Livestream: http://$hostname:8081" #may require .local?
echo "Config menu: http://$hostname:8765"
