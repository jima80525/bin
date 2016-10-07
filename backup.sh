#!/bin/sh

#Variable with current date and time (for the file name)
DATE_NAME=$(date +'%Y-%m-%d-%H-%M-%S')
#DATE_NAME=$(date +'%u')

#Your dropbox backup location.
#Modify ‘username’ and ‘server_name’ accordinly
DROPBOX_BACKUP_DIR_URL="/home/jima/Dropbox/backups/home_laptop/"

#The temp location to copy all files
TEMP_DIR="/tmp"
#The full url for the temp directory
#including the date/time directory
TEMP_BACKUP_DIR_URL="$TEMP_DIR/$DATE_NAME"

#The full temp URLS for each directory you want to backup
#TEMP_DOC_BACKUP_DIR_URL="$TEMP_BACKUP_DIR_URL/Documents"
TEMP_DOC_BACKUP_DIR_URL="/home/jima/Documents"

tar -zcvf $DROPBOX_BACKUP_DIR_URL/$DATE_NAME.tar.gz $TEMP_DOC_BACKUP_DIR_URL
################################################################################
# JHA skipping the "make temp dir and copy" step as I'm only doing one directory
################################################################################
#Create the directories above
#mkdir -p $TEMP_DOC_BACKUP_DIR_URL

#Perform the backups, this is where you go to town
#by copying all the files you want to backup
#cp -R "/home/jima/Documents/" "$TEMP_DOC_BACKUP_DIR_URL"
#cp -R "/usr/local/sites/" "$TEMP_SITES_BACKUP_DIR_URL"
#cp -R "/etc/nginx/sites-available/" "$TEMP_NGINX_CONFIG_DIR_URL"
#cp /etc/nginx/*.common $TEMP_NGINX_CONFIG_DIR_URL
#cp -R "/etc/supervisor/conf.d/" "$TEMP_SUPERVISOR_CONFIG_DIR_URL"

#This will backup all my databases
#Modify ‘backup_username’ and ‘PASSWORD’ accordingly
#mysqldump -u backup_username -pPASSWORD --all-databases > "$TEMP_MYSQL_DATABASE_BACKUP_DIR_URL/databases.sql"

#Now we change into the temp directory
#cd $TEMP_DIR
#We tar up and compress the files to backup
#and output the tar into our Dropbox
#tar -zcvf $DROPBOX_BACKUP_DIR_URL/$DATE_NAME.tar.gz $DATE_NAME

#Now we can delete the temp backup directory
#rm -rf $TEMP_BACKUP_DIR_URL
