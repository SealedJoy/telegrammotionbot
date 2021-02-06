#!/bin/bash    
# Script: my-pi-temp.sh
# Purpose: Removes EVERYTHING older than x from google drive (called by cron at 4am) except jpgs
# Author: J Slade
# -------------------------------------------------------
adddate() {
    while IFS= read -r line; do
        echo "$(date) $line"
    done
}
old=24h
delfolder="$(rclone lsd gdrive:/ --min-age $old | awk '{print $2}')"
echo Starting google drive clear-up
rclone --include "*.mp4" delete gdrive:/ --min-age $old --drive-use-trash=false || echo "Error deleting .mp4 files"
# --drive-use-trash=false
echo "files older than $old were deleted"
echo $delfolder will be deleted
rclone rmdir gdrive:SummerhouseCam/$delfolder --drive-use-trash=false || echo "Error removing folders" # --drive-use-trash=false
echo "folders older than: $old were removed"
echo "finished google drive clear-up"
