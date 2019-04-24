#! /bin/bash


cp -b -S "-`date "+%Y%m%d%H%M%S"`" mqtt2sms.ini     /usr/local/bin/
cp mqtt2sms.py      /usr/local/bin/
cp mqtt2sms.sh      /usr/local/bin/
cp mqtt2sms.service /lib/systemd/system/

systemctl daemon-reload
systemctl enable mqtt2sms
systemctl start mqtt2sms
