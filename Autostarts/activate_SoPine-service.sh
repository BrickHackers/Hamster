#!/bin/bash

cp hamsterSoPine.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable hamsterSoPine.service
systemctl start hamsterSoPine.service

exit 0
