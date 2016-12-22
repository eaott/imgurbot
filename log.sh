#!/bin/bash

mv /home/pi/logs/imgur.log "/home/pi/logs/`date +%Y_%m_%d_imgur.log`"
touch /home/pi/logs/imgur.log
