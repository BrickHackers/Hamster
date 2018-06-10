#!/bin/bash

cd PineBook/
python SerialReader.py /dev/ttyAMAO 115200 10020 FromSoPine &
python main.py &

exit 0

