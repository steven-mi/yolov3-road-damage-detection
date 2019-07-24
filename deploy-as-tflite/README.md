# YOLOv3 with TF-Lite
From https://github.com/benjamintanweihao/YOLOv3
## Getting Started

Clone the repository:

```bash
git clone https://github.com/steven-mi/yolov3-road-damage-detection.git
cd yolov3-road-damage-detection/deploy-as-tflite
pip install -r requirement.txt
```

**Download weights and convert model to .h5**

1. Download weights:

   ```bash
   cd weights
   chmoud u+x download.sh
   ./download.sh # this will download all (skip this if you want to use your own model)
   ```

2. Run a Converter

   For YOLOv3:

   ```bash
   cd convert_to_h5
   # convert.py [config file] [weightfile] [output file]
   python3 convert.py yolov3.cfg ../weights/yolov3.weights convert_to_tflite/yolov.h5
   ```

   For YOLOv3-tiny:

   ```bash
   cd convert_to_h5
   python3 convert.py yolov3-tiny.cfg ../weights/yolov3-tiny.weights ../convert_to_tflite/yolo.h5
   ```

**Convert .h5 model to .tflite model**

Start the converter
   For YOLOv3:

   ```bash
   cd convert_to_tflite
   python3 convert.py
   ```

   For YOLOv3-tiny:

   ```bash
   cd convert_to_h5
   python3 convert.py --tiny
   ```

**Run demo**

```bash
cd ..
python3 webcam.py
```

