import time
import cv2
import numpy as np

from tensorflow.contrib.lite.python import interpreter as interpreter_wrapper
from tensorflow.keras import Input

from predict import *
from yolo_head import yolo_head

import matplotlib.pyplot as plt

model_path = 'yolo.tflite'

interpreter = interpreter_wrapper.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
print(input_details)
print(output_details)

inputs = Input(shape=(None, None, 3))
outputs, config = darknet_base(inputs, include_yolo_head=False)

# check the type of the input tensor
if input_details[0]['dtype'] == np.float32:
    floating_model = True

orig = cv2.imread('dog-cycle-car.png')
print(orig.shape)
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

image, image_data = preprocess_image(orig, (height, width))

start = time.time()
interpreter.set_tensor(input_details[0]['index'], image_data)
interpreter.invoke()
end = time.time()

a = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
print(len(a))
b = yolo_head(a, num_classes=80, input_dims=(width, height))
print(b.shape)
boxes, classes, scores = handle_predictions(b,
                                            confidence=0.5,
                                            iou_threshold=0.4)
#draw_boxes(image, boxes, classes, scores, config)
print("Inference time: {:.2f}s".format((end - start)))
#plt.imshow(image)
#plt.show()
