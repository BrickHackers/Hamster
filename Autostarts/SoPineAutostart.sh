#!/bin/bash

cd ../SoPine/
python SerialReader.py /dev/ttyS4 115200 10019 FromRPi &
python SerialReader.py /dev/ttyS3 115200 10018 FromMbed &
python main.py &

exit 0

