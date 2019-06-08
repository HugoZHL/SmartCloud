#!/bin/bash
# synchronization--pull from the other nas
#
#====================================================
# remote
# user@ip::sync-block  admin0@192.168.2.240::rsync-$1
#====================================================
# local
# sync folder          test/$1/sync-folder/
#====================================================
#
# more info refers to the link of rsync 
# you must deploy the rsync service before continuing

rsync -vzrtopg --progress --delete --password-file=/etc/rsync.pwd admin0@192.168.2.240::rsync-$1 test/$1/sync-folder/
exit

