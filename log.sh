#!/bin/bash

mv /home/pi/logs/imgur.log "/home/pi/logs/`date +%Y_%m_%d_imgur.log`"
touch /home/pi/logs/imgur.log
cd /home/pi/GitProjects/imgurbot
python iscore.py >> iscore.csv
git add iscore.csv
git commit -m "adding data to iscore.csv `date`"
