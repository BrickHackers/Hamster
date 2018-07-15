#!/bin/bash

cd /home/teapack/GIT/hamster/RPiZero/
python SerialReader.py /dev/ttyAMA0 115200 10020 FromSoPine &
python main.py &

exit 0

