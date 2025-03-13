from collections import defaultdict
from threading import Thread
import time
import argparse
from pymavlink import mavutil

import cv2
import numpy as np
from ultralytics import YOLO
import os


print("test")

parser = argparse.ArgumentParser(description='ML Script')
parser.add_argument('-rc','--run_connection', help='Run the MAVLINK connection or not? (y/n)', required=True)
args = vars(parser.parse_args())

model = YOLO("yolo11m_v6.pt")

track_history = defaultdict(lambda: [])

if args["run_connection"] == "y":
    connection = mavutil.mavlink_connection('0.0.0.0:14550')
    connection.wait_heartbeat()
    print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

class TCam(object):
    def __init__(self):
        self.video_capture = cv2.VideoCapture(cv2.CAP_DSHOW)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
       
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)
        
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def update(self):
        while True:
            if self.video_capture.isOpened():
                (self.ret, self.frame) = self.video_capture.read()
            time.sleep(self.FPS)
            
    def show_frame(self, ret_frame):
        cv2.imshow('RapidResponse', ret_frame)
        cv2.waitKey(self.FPS_MS)

with open("people.txt", "w") as file:
    if __name__ == '__main__':
        cap = TCam()
        while True:
            try:
                results = model.track(cap.frame, persist=True, )
                annotated_frame = results[0].plot()
                try:
                    boxes = results[0].boxes.xywh.cpu()
                    track_ids = results[0].boxes.id.int().cpu().tolist()
                    classes = results[0].boxes.cls.cpu()
                    print("Detection")
                except:
                    print("None")
                    cap.show_frame(annotated_frame) 
                    continue

                for box, track_id, cls in zip(boxes, track_ids, classes):
                    x, y, w, h = box
                    track = track_history[track_id]
                    track.append((float(x), float(y))) 
                    if len(track) > 10 and cls == 4: 
                        track.pop(0)
                        print("POSSIBLE PERSONM!!!!")
                        if args["run_connection"] == "y":
                            msg = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
                            print(msg)
                            file.write(str(track_id) + "\t" + str(msg.lat) + "\t" + str(msg.lon) + "\n")
                    
                    points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                    cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

                cap.show_frame(annotated_frame)
            except AttributeError:
                pass