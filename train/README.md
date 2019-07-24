# Road Damage Dataset Downloader and Training YOLOv3 on darknet tutorial

Dataset from: https://github.com/sekilab/RoadDamageDetector


## Getting Started

### Preparation 
Clone this repository
```bash
cd ~/
git clone https://github.com/steven-mi/yolov3-road-damage-detection.git
```


Pull darknet container and run it
```bash
docker pull jimmylin1017cs/darknet
NV_GPU=0 nvidia-docker run -v ~/yolov3-road-damage-detection:/yolov3-road-damage-detection --rm -it jimmylin1017cs/darknet bash
mv /yolov3-road-damage-detection /jimmy/yolov3-road-damage-detection

apt update
apt upgrade
apt install python3 python3-pip

mkdir old
mv darknet/ old/
mv *.zip old/
```

Install darknet from AlexeyAB
```bash
# follow https://github.com/AlexeyAB/darknet#how-to-train-tiny-yolo-to-detect-your-custom-objects
# and install with GPU support
git clone https://github.com/AlexeyAB/darknet.git
``` 

### Download the Road Damage Dataset

```bash
cd /jimmy/yolov3-road-damage-detection
cd yolov3-road-damage-detection/train
chmod u+x download_and_extract_road_damage_dataset.sh
./download_and_extract_road_damage_dataset.sh
```

Move every configuration files into the darknet repository

```bash
cd /jimmy/darknet
mv /jimmy/yolov3-road-damage-detection/train/tiny-yolov3-cfgs/*.cfg ./cfg/
mv /jimmy/yolov3-road-damage-detection/train/tiny-yolov3-cfgs/RoadDamageDataset.* ./build/darknet/x64/data/
mv /jimmy/yolov3-road-damage-detection/train/RoadDamageDataset ./
mv /jimmy/yolov3-road-damage-detection/train/*.txt ./build/darknet/x64/data/
```

### Training Yolov3 on the Road Damage Dataset
Get pretrained weights and convert them

```bash
wget https://pjreddie.com/media/files/yolov3-tiny.weights #only if the weights are not inside the darknet folder
./darknet partial cfg/yolov3-tiny.cfg yolov3-tiny.weights yolov3-tiny.conv.15 15
```

Calculate anchors and add them to the .cfgs
```bash
./darknet detector calc_anchors build/darknet/x64/data/RoadDamageDataset.data -num_of_clusters 6 -width 416 -height 416
```

Train YOLOv3 on new Road Damage Dataset

```bash
./darknet detector train build/darknet/x64/data/RoadDamageDataset.data cfg/yolov3-tiny-RoadDamageDataset-train.cfg yolov3-tiny.conv.15 -map
```

After training you have to select the weight-file with the highest **mAP (mean average precision)** or **IoU (intersect over union** by running following command for every weight file and comparing the output for each weight file

```bash
./darknet detector map build/darknet/x64/data/RoadDamageDataset.data cfg/yolov3-tiny-RoadDamageDataset-train.cfg backup/yolov3-tiny-RoadDamageDataset_x.weights
```

Take the best weight file and move it to the repository folder
```bash
mv backup/yolov3-tiny-RoadDamageDataset_x.weights /jimmy/yolov3-road-damage-detection
```

