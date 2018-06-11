#!/bin/bash

cp hamsterRPi.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable hamsterRPi.service
systemctl start hamsterRPi.service

exit 0
