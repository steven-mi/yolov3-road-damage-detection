import time
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.abspath('src'))

from predict import preprocess_image
from predict import handle_predictions
from predict import draw_boxes
from yolo_head import yolo_head
from coco_labels import COCOLabels
#from tensorflow.keras import Input, Model
#from darknet import darknet_base
#from predict import predict, predict_with_yolo_head
import tensorflow as tf

model_path = os.path.join(os.getcwd(), 'yolo.tflite')
interpreter = tf.contrib.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
print(input_details)
print(output_details)

# check the type of the input tensor
if input_details[0]['dtype'] == np.float32:
    floating_model = True

height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
#print(height, width)

config = {}
config['width'] = width
config['height'] = height
config['labels'] = COCOLabels.all()
config['colors'] = COCOLabels.colors()

stream = cv2.VideoCapture(0)
stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cv2.namedWindow("yolo", cv2.WINDOW_AUTOSIZE)
while True:
    # Capture frame-by-frame
    grabbed, frame = stream.read()
    if not grabbed:
        break
    #print("--------------------------------:",frame.shape)
    # Run detection
    start = time.time()

    image, image_data = preprocess_image(frame, (height, width))
    #print(frame.shape, image.shape, image_data.shape)
    interpreter.set_tensor(input_details[0]['index'], image_data)
    interpreter.invoke()
    output = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
    predictions = yolo_head(output, num_classes=80, input_dims=(width, height))

    boxes, classes, scores = handle_predictions(predictions,
                                                confidence=0.3,
                                                iou_threshold=0.5)
    print(boxes, classes, scores)
    draw_boxes(image, boxes, classes, scores, config)
    
    image = np.array(image)

    # output_image = frame
    end = time.time()
    print("Inference time: {:.2f}s".format(end - start))

    # Display the resulting frame
    cv2.imshow("yolo", image)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# When everything done, release the capture
stream.release()
cv2.destroyAllWindows()

