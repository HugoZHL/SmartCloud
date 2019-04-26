#!/bin/bash

rsync -vzrtopg --progress --delete --password-file=/etc/rsync.pwd admin0@192.168.2.240::rsync-$1 test/$1/sync-folder/
exit

