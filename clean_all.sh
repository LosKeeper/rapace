#!/bin/bash

sh clean_p4src.sh
sh clean_topo.sh light
sh clean_topo.sh medium
sh clean_topo.sh complex

sudo rm -rf *.json
rm -rf *.png
sudo rm -rf log/*
sudo rm -rf pcap/*
