# NOTE: Because of a bug in TensorFlow, this should be run in the console
# NOTE: python tflite.py
import sys
import os
sys.path.append(os.path.abspath('../src'))

import tensorflow as tf
from tensorflow.keras import Input, Model

import argparse

parser = argparse.ArgumentParser(description='Keras to TF-Lite converter')
parser.add_argument(
    '-tiny',
    '--tiny',
    help='If set then tiny-yolov3 will be converted to tflite',
    action='store_true')

args = parser.parse_args()

if args.tiny:
    print("test")
    from darknet_tiny import darknet_base
else:
    from darknet import darknet_base

inputs = Input(shape=(None, None, 3))
# NOTE: Here, we do not include the YOLO head because TFLite does not
# NOTE: support custom layers yet. Therefore, we'll need to implement
# NOTE: the YOLO head ourselves.
outputs, config = darknet_base(inputs, include_yolo_head=False)

model = Model(inputs, outputs)
model_path = 'yolo.h5'

tf.keras.models.save_model(model, model_path, overwrite=True)
model.summary()
# Sanity check to see if model loads properly
# NOTE: See https://github.com/keras-team/keras/issues/4609#issuecomment-329292173
# on why we have to pass in `tf: tf` in `custom_objects`
model = tf.keras.models.load_model(model_path,
                                   custom_objects={'tf': tf})

converter = tf.contrib.lite.TFLiteConverter.from_keras_model_file(model_path,
                                                     input_shapes={'input_1': [1, config['width'], config['height'], 3]})
#converter.post_training_quantize = True
tflite_model = converter.convert()
open("../yolo.tflite", "wb").write(tflite_model)
