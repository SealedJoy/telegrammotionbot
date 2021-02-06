#!/bin/bash
# Start the update process for opspot
failed=1 
LOG='/home/pi/scripts/updateopspot/logs/update-log.txt'
BACKUPDIR='/home/pi/scripts/updateopspot/backup/beforeupdate'
configfile='/home/pi/scripts/updateopspot/config/configuration.ini'
hostname="$(hostname)"
DATE=`date +%Y-%m-%d`

# load the in.ini INI file to current BASH - quoted to preserve line breaks
eval "$(cat $configfile  | /home/pi/scripts/updateopspot/config/ini2arr.py)"

# test it:
owner=${OWNEDBY[owner]}


adddate() {
    while IFS= read -r line; do
        echo "$(date) $line"
    done
}
# Begin print to log
#{
echo "----------------------------------"
echo "$(date) Started the update process"
echo "----------------------------------"
echo "$(date) Stopping service"
#sudo systemctl stop camerabotinterface.service kills this script :(
# Make Copy of existing opspot folder
# if no dir make one
if [ ! -d "$BACKUPDIR" ]; then
echo "$(date) no backup dir found - one will be created for you" ; mkdir -p $BACKUPDIR
fi
cp -r -f -v /home/pi/scripts/opspot $BACKUPDIR && rclone copy -v gdrive:packages/update/opspot /home/pi/scripts/opspot || failed=0 | echo "$(date) Error making backup / copying from source remote gdrive"
if [[ $failed = 0 ]]; then
echo "$(date) Failed! - restoring backup" ; cp -r -f -v $BACKUPDIR /home/pi/scripts/opspot && echo "$(date) Backup was restored"
else echo "$(date) Success!"
fi
echo "$(date) Update script finished"
# restart the process
sudo systemctl restart camerabotinterface.service
echo "$(date) Restarted camerabotinterface service"
echo "----------------------------------"
echo "$(date) Done exiting update script"
#exit 1
#	} 2>&1 | tee -a $LOG 
# copy upload log back to gdrive
rclone copy /home/pi/scripts/updateopspot/logs/update-log.txt gdrive:client/logs/$owner/$hostname/$DATE-update-log.txt && echo "$(date) Uploaded update-log.txt as $hostname.txt" || echo "Failed to upload update-log.txt"

# End and print to log

exit 0
