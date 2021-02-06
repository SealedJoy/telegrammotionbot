#!/bin/bash
# 
# To check the output of the called script access the syslog with: cat /var/log/syslog
hostname="$(hostname)"
lines=$(ps -ef | grep python-telegram-bot.py | wc -l)
LOG='/home/pi/scripts/updateopspot/logs/python.log'
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

# check for existing launch-log.txt, if found move to prev-launch-log.txt
if [ ! -f $LAUNCHLOG ]; then
   echo "$(date) Creating new launch-log.txt" ; touch /home/pi/scripts/updateopspot/logs/launch-log.txt || echo "failed to create updateopspot/logs/launch-log.txt"
else
   echo "$(date) Existing launch log found moving to prev-launch-log.txt" >> $LAUNCHLOG
   mv -f /home/pi/scripts/updateopspot/logs/launch-log.txt /home/pi/scripts/updateopspot/logs/prev-launch-log.txt
   touch /home/pi/scripts/updateopspot/logs/launch-log.txt && echo "$(date) Started new launch-log as old one already exists - moved to prev-launch-log.txt" >> $LAUNCHLOG
fi

echo "----------------------------------------" >> $LAUNCHLOG
echo "$(date)" >> $LAUNCHLOG
echo "configuration.ini" >> $LAUNCHLOG
echo "Owner: $owner" >> $LAUNCHLOG
echo "----------------------------------------" >> $LAUNCHLOG
# Functions begin



# Functions end

# Begin print to log
#{
echo "$(date) CameraBotInterface Launcher started" >> $LAUNCHLOG
echo "----------------------------------------" >> $LAUNCHLOG


# Check for existing log.txt file, if found move to prev-log.txt and upload, else make log
if [ ! -f $LOG ]; then
   echo "$(date) Creating new python.log" ; touch /home/pi/scripts/updateopspot/logs/python.log || echo "failed to create updateopspot/logs/python.log" >> $LAUNCHLOG
else
   echo "$(date) Existing log found moving to previous-python.log" >> $LAUNCHLOG
   mv -f /home/pi/scripts/updateopspot/logs/python.log /home/pi/scripts/updateopspot/logs/prev-python.log || echo "failed to move python.log" >> $LAUNCHLOG
   # upload the last python log file to drive at end of launcher
fi

# python telegram bot /update command copies telegram-python-bot.py from rclone remote then it is compared with current and user is prompted to reboot if difference

# CHECK FILE FOR UPDATE FLAG
update=$(head -n 1 $updateflaglocation)
#echo "$update"
# if there is difference launch update script in /home/pi/scripts/
if [[ $update = "new" ]]; then
   echo "$(date) Update flag was true - Starting update..." >> $LAUNCHLOG
   /home/pi/scripts/updateopspot/update.sh &
   update='false'
   # update flag in file updateopspot/check/flag
   echo "false" > $updateflaglocation
   echo "$(date) Update flag was true - Launcher will exit and service will restart after the update" >> $LAUNCHLOG
   exit 1
else
   echo "$(date) Update flag was false" >> $LAUNCHLOG
fi



#while true
#do
# check if script is running - if not start it up
if [ $lines -ne 2 ]; then
  echo "$(date) Bot started up" >> $LAUNCHLOG
  python /home/pi/scripts/opspot/python-telegram-bot.py & #2>&1 | adddate >> /home/pi/scripts/updateopspot/logs/log.txt &
  wait
  echo "$(date) ran python-telegram-bot.py" >> $LAUNCHLOG
else
  echo "$(date) Bot is already running" >> $LAUNCHLOG
fi
#sleep 60
echo "----------------------------------------" >> $LAUNCHLOG
echo "$(date) Launcher finished - uploading logs then exiting script" >> $LAUNCHLOG

# make missing dir on drive
rclone mkdir gdrive:client/logs/$owner/$hostname
# upload the last python bot log file
rclone copyto -v /home/pi/scripts/updateopspot/logs/prev-python.log gdrive:client/logs/$owner/$hostname/$DATE-prev-python.log && echo "$(date) Uploaded python.log to drive/logs/$owner/$hostname/$DATE-python.log" || echo "$(date) Failed to upload python.log"

# end print all to log
#} >> $LAUNCHLOG
#	} 2>&1 | tee -a $LAUNCHLOG 
#done
#exit 1

# upload the current launch-log
rclone copyto -v /home/pi/scripts/updateopspot/logs/launch-log.txt gdrive:client/logs/$owner/$hostname/$DATE-launch-log.txt && echo "$(date) Uploaded launch-log.txt to drive/logs/$owner/$hostname/$DATE-launch-log.txt" || echo "$(date) Failed to upload launch-log.txt" 

