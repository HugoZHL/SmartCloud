#!/bin/bash

rsync -vzrtopg --progress --delete --password-file=/etc/rsync.pwd fan@192.168.2.239::rsync-$1 test/$1/sync-folder/
exit

