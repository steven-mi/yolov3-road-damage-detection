# Yolov3 with Openvino

**Docker Container for openvino (FULL VERSION):** https://github.com/mateoguzman/openvino-docker

**Cross Compiling Docker Container:** https://github.com/dockcross/dockcross

**Code from:** https://github.com/mystic123/tensorflow-yolo-v3

**More guides:** https://software.intel.com/en-us/articles/OpenVINO-Using-TensorFlow

![Intel Computer Vision Basic Workflow](https://software.intel.com/sites/default/files/managed/2a/fb/CVSDK_Flow.png)

## OpenVINO Supported Layers (As of Dec 25, 2018)

- [Supported Framework Layers](https://docs.openvinotoolkit.org/R5/_docs_MO_DG_prepare_model_Supported_Frameworks_Layers.html)
- [Supported Caffe Layers](https://software.intel.com/en-us/articles/OpenVINO-Using-Caffe#caffe-supported-layers)
- [Supported TensorFlow Layers](https://software.intel.com/en-us/articles/OpenVINO-Using-TensorFlow#tensorflow-supported-layers)
- [Supported MXNet Layers](https://software.intel.com/en-us/articles/OpenVINO-Using-MXNet#mxnet-supported-layers)
- [Supported ONNX Layers](https://software.intel.com/en-us/articles/OpenVINO-Using-ONNX#supported-onnx-layers)

------

## Getting Started

Clone the repository:

```bash
git clone https://github.com/steven-mi/yolov3-road-damage-detection.git
```

### Store TF-Model as protobuf file 

In TensorFlow, the protbuf file contains the graph definition as well as the weights of the model. Thus, a `pb` file is all you need to be able to run a given trained model.

1. Download:
   1. [coco.names](https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names) file from the DarkNet website **OR** use labels that fit your task.
   2. weights file **OR** use your pretrained weights with the same structure

```bash
# skip if you want to use your own model
cd weights
chmod u+x download.sh
./download.sh # this will download allRun a converter: 		
```

2. Run a Converter

   For YOLOv3:

   ```bash
   python3 convert_weights_pb.py --class_names coco.names --data_format NHWC --weights_file yolov3.weights
   ```

   For YOLOv3-tiny:

   ```bash
   python3 convert_weights_pb.py --class_names coco.names --data_format NHWC --weights_file yolov3-tiny.weights --tiny
   ```

### Convert to IR 

**NOTE:** `mo/`, `extensions/`, `convert_pb_ir.py` are extracted from the Openvino toolkit. They are located at `<INSTALL_DIR>/deployment_tools/model_optimizer/`. The `convert_pb_ir.py` script is the same as `mo_tf.py`. 

```bash
cd ../models
```

The `yolo_v3.json` or `yolo_v3_tiny.json` are configuration files where:

- `id` and `match_kind` are parameters that you cannot change.
- `custom_attributes` is a parameter that stores all the YOLOv3 specific attributes: 		
  - `classes`, `coords`, `num`, and `mask`  are attributes that you should copy from the configuration file file  that was used for model training. If you used DarkNet officially shared  weights, you can use `yolov3.cfg` or `yolov3-tiny.cfg` configuration at https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg. Replace the default values in `custom_attributes` with the parameters that follow the `[yolo]` title in the configuration file.
  - `entry_points`

Inside the repository are the configuration for the original YOLOv3 and Tiny Yolov3 which can be found

- https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
- https://github.com/pjreddie/darknet/blob/master/cfg/yolov3-tiny.cfg

To generate the IR run:

- YOLOv3:

  ```bash
  python3 convert_pb_ir.py --input_model yolov3.pb --tensorflow_use_custom_operations_config yolov3.json --input_shape=[1,416,416,3] --data_type FP16
  ```

- Tiny Yolov3

  ```bash
  python3 convert_pb_ir.py --input_model yolov3-tiny.pb --tensorflow_use_custom_operations_config yolov3-tiny.json --input_shape=[1,416,416,3] --data_type FP16
  ```

### Deployment on Raspberry

**Requirements**

- `*.xml` and `*.bin` which `convert_pb_ir.py` created
- a WebCam

**Deployment with Python** 

Install Openvino on your PI:

```HTTP
https://software.intel.com/en-us/articles/OpenVINO-Install-RaspberryPI
```

Put `live_object_detection.py`,`xml` and `*.bin` which `convert_pb_ir.py` created on your PI. Afterward run following command:

```bash
python3 live_object_detection.py
```