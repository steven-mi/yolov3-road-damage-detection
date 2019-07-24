import numpy as np
import cv2
import tensorflow as tf

from multiprocessing import Process, Queue
import time

import sys
import os
sys.path.append(os.path.abspath('src'))

from predict import preprocess_image
from predict import handle_predictions
from predict import draw_boxes
from yolo_head import yolo_head
from coco_labels import COCOLabels

import warnings
warnings.filterwarnings("ignore")

class Canny_Process(Process):
    
    def __init__(self,frame_queue,output_queue):
        Process.__init__(self)
        self.frame_queue = frame_queue
        self.output_queue = output_queue
        self.stop = False
        model_path = 'yolov3-quant.tflite'
        self.interpreter = tf.contrib.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        print(self.input_details)
        print(self.output_details)

        # check the type of the input tensor
        if self.input_details[0]['dtype'] == np.float32:
            self.floating_model = True

        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.config = {}
        self.config['width'] = self.width
        self.config['height'] = self.height
        self.config['labels'] = COCOLabels.all()
        self.config['colors'] = COCOLabels.colors()

        

    def get_frame(self):
        if not self.frame_queue.empty():
            return True, self.frame_queue.get()
        else:
            return False, None

    def stopProcess(self):
        self.stop = True
            
    def canny_frame(self,frame):
        print("here yet?")
        # some intensive computation...
        image, image_data = preprocess_image(frame, (self.height, self.width))
        self.interpreter.set_tensor(self.input_details[0]['index'], image_data)
        self.interpreter.invoke()
        output = [self.interpreter.get_tensor(self.output_details[i]['index']) for i in range(len(self.output_details))]
        predictions = yolo_head(output, num_classes=80,
                                input_dims=(self.width, self.height))

        boxes, classes, scores = handle_predictions(predictions,
                                                    confidence=0.3,
                                                    iou_threshold=0.4)
        #draw_boxes(image, boxes, classes, scores, self.config)
        #image = np.array(image)

        if self.output_queue.full(): 
            self.output_queue.get_nowait()
        print("predicted")
        self.output_queue.put([boxes, classes, scores])

    def run(self):
        while not self.stop: 
            ret, frame = self.get_frame()
            if ret: 
                self.canny_frame(frame)


if __name__ == '__main__':
    frame_sum = 0
    init_time = time.time()

    def put_frame(frame):
        if Input_Queue.full(): 
            Input_Queue.get_nowait()
        Input_Queue.put(frame)

    def cap_read(cv2_cap):
        ret, frame = cv2_cap.read()
        if ret:
            put_frame(frame)
        
    cap = cv2.VideoCapture(0)
    width = 416
    height = 416
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


    threaded_mode = True

    process_list = []
    Input_Queue = Queue(maxsize = 5)
    Output_Queue = Queue(maxsize = 5)

    canny_process = Canny_Process(frame_queue = Input_Queue,output_queue = Output_Queue)
    canny_process.daemon = True
    canny_process.start()
    process_list.append(canny_process)

    ch = cv2.waitKey(1)
    cv2.namedWindow('Threaded Video', cv2.WINDOW_AUTOSIZE)
    while True:        
        cap_read(cap)
        ret, frame = cap.read()
        if ret:
            image, image_data = preprocess_image(frame, (width, height))

            if not Output_Queue.empty():
                boxes, classes, scores = Output_Queue.get()
                draw_boxes(image, boxes, classes, scores, self.config)
            image = np.array(image)
            cv2.imshow('Threaded Video', image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
