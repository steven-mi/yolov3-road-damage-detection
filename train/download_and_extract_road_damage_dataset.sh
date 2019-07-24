#!/bin/bash
# download and extract
echo "Starting downloading images"
python3 download_road_damage_dataset.py

echo "Download finished, started extracting images"
tar -zxf ./RoadDamageDataset.tar.gz
#mv ./RoadDamageDataset/ ../data/
rm -rf ./RoadDamageDataset.tar.gz

echo "Extracting, started creating file with paths to train and val images"
python3 road_damage_dataset.py
cd ..
echo "done, train.txt and val.txt are inside the script folder"
