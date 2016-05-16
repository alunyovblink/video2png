#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install python-pip -y
sudo pip install youtube_dl
sudo apt-get install pngcrush python-opencv python-numpy python-scipy -y
sudo apt-get install gif2apng -y


sudo add-apt-repository ppa:mc3man/trusty-media
sudo apt-get update
sudo apt-get dist-upgrade -y
sudo apt-get install ffmpeg -y
