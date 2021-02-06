#!/bin/bash
# 
# To check the output of the called script access the syslog with: cat /var/log/syslog
hostname="$(hostname)"
lines=$(ps -ef | grep python-telegram-bot.py | wc -l)
LOG='/home/pi/scripts/updateopspot/logs/log.txt'
LAUNCHLOG='/home/pi/scripts/updateopspot/logs/launch-log.txt'
current='/home/pi/scripts/opspot/python-telegram-bot.py'
downloaded='/home/pi/scripts/updateopspot/check/python-telegram-bot.py'
configfile='/home/pi/scripts/updateopspot/config/configuration.ini'
updateflaglocation="/home/pi/scripts/updateopspot/check/flag"

DATE=`date +%Y-%m-%d`
adddate() {
    while IFS= read -r line; do
        echo "$(date) $line"
    done
}

# load the in.ini INI file to current BASH - quoted to preserve line breaks
eval "$(cat $configfile  | /home/pi/scripts/updateopspot/config/ini2arr.py)"

# test it:
owner="${OWNEDBY[owner]}"


echo "----------------------------------------"
echo "$(date)"
echo "configuration.ini"
echo "Owner: $owner"
echo "----------------------------------------"
# Functions begin



# Functions end

# Begin print to log
{
echo "$(date) CameraBotInterface Launcher started"
echo "----------------------------------------"
# check for existing launch-log.txt, if found move to prev-launch-log.txt
rclone mkdir gdrive:client/logs/$owner/$hostname
if [ ! -f $LAUNCHLOG ]; then
   echo "$(date) Creating new launch-log.txt" ; touch /home/pi/scripts/updateopspot/logs/launch-log.txt || echo "failed to create updateopspot/logs/launch-log.txt"
else
   echo "$(date) Existing log found moving to previous-log.txt"
   rclone copyto -v /home/pi/scripts/updateopspot/logs/launch-log.txt gdrive:client/logs/$owner/$hostname/$DATE-last-launch-log.txt && echo "$(date) Uploaded launch-log.txt to drive/logs/$owner/$hostname/$DATE-launch-log.txt" || echo "$(date) Failed to upload launch-log.txt"
   
   mv -f /home/pi/scripts/updateopspot/logs/launch-log.txt /home/pi/scripts/updateopspot/logs/prev-launch-log.txt || echo "failed to move launch-log to prev-launch-log"
   # copy upload launch log drive
fi

# Check for existing log.txt file, if found move to prev-log.txt and upload, else make log
if [ ! -f $LOG ]; then
   echo "$(date) Creating new log.txt" ; touch /home/pi/scripts/updateopspot/logs/log.txt || echo "failed to create updateopspot/logs/log.txt"
else
   echo "$(date) Existing log found moving to previous-log.txt"
   rclone copyto -v /home/pi/scripts/updateopspot/logs/log.txt gdrive:client/logs/$owner/$hostname/$DATE-log.txt && echo "$(date) Uploaded launch-log.txt to drive/logs/$owner/$hostname/$DATE-log.txt" || echo "$(date) Failed to upload log.txt"
   mv -f /home/pi/scripts/updateopspot/logs/log.txt /home/pi/scripts/updateopspot/logs/prev-log.txt || echo "failed to move launch-log"
   # copy upload log drive
fi

# telegram /update copies telegram-python-bot.py from rclone remote then it is compared with current 

# compare downloaded file with current 
# NOPE INSTEAD CHECK FILE FOR UPDATE FLAG
#cmp --silent $current $downloaded || update="true"

update=$(head -n 1 $updateflaglocation)
echo "$update"
# if there is difference launch update script in /home/pi/scripts/
if [[ $update = "new" ]]; then
   echo Starting update...
   /home/pi/scripts/updateopspot/update.sh &
   update='false'
   echo "false" > $updateflaglocation
   echo "$(date) Update Process started - Launcher will exit and service will restart after the update"
   exit 1
else
   echo "$(date) Update flag was false"
fi



#while true
#do
# check if script is running - if not start it up
if [ $lines -ne 2 ]; then
    python /home/pi/scripts/opspot/python-telegram-bot.py 2>&1 | adddate >> /home/pi/scripts/opspot/logs/log.txt &
    echo "$(date) Bot started up"
else
   echo "$(date) Bot is already running"
fi
sleep 60
echo "$(date) Launcher finished exiting script"
# end print all to log
	} 2>&1 | tee -a $LAUNCHLOG 
#done
#exit 1

