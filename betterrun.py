from collections import defaultdict
from threading import Thread
import time
import argparse

import cv2
import numpy as np
from ultralytics import YOLO
import os


print("test")

model = YOLO("yolo11m_v6.pt")
print("test2")

cap = cv2.VideoCapture(cv2.CAP_MSMF)

print("test3")

track_history = defaultdict(lambda: [])

# connection = mavutil.mavlink_connection('0.0.0.0:14550')
# connection.wait_heartbeat()
# print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

# with open("people.txt", "w") as file:
# counter = 0
# while True:
#     ret, frame = cap.read()
#     counter+= 1
#     if not counter % 6:
#         if cv2.waitKey(1) == ord("q"):
#             break
#         continue
#     counter = 0
#     print(cap.isOpened())

#     print("next")

#     # if ret:
#     results = model.track(frame, persist=True, )
#     annotated_frame = results[0].plot()

#     try:
#         boxes = results[0].boxes.xywh.cpu()
#         track_ids = results[0].boxes.id.int().cpu().tolist()
#         classes = results[0].boxes.cls.cpu()
#         print("Detection")
#     except:
#         print("None")
#         cv2.imshow("YOLO11 Tracking", annotated_frame) 
#         continue

#     for box, track_id, cls in zip(boxes, track_ids, classes):
#         x, y, w, h = box
#         track = track_history[track_id]
#         track.append((float(x), float(y))) 
#         if len(track) > 10 and cls == 4: 
#             track.pop(0)
#             print("POSSIBLE PERSONM!!!!")
#             # msg = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
#             # print(msg)
#             # file.write(str(track_id) + "\t" + str(msg.lat) + "\t" + str(msg.lon) + "\n")


#         points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
#         cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

#     cv2.imshow("YOLO11 Tracking", annotated_frame)
#     if cv2.waitKey(1) == ord("q"):
#         break

#         # Break the loop if 'q' is pressed
#     # else:
#     #     # Break the loop if the end of the video is reached
#     #     break

#     # Release the video capture object and close the display window
# cap.release()
# cv2.destroyAllWindows()



class ThreadedCamera(object):
    def __init__(self):
        self.video_capture = cv2.VideoCapture(cv2.CAP_DSHOW)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
       
        # FPS = 1/X
        # X = desired FPS
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)
        
        # Start frame retrieval thread
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

if __name__ == '__main__':
    cap = ThreadedCamera()
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
                    # msg = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
                    # print(msg)
                    # file.write(str(track_id) + "\t" + str(msg.lat) + "\t" + str(msg.lon) + "\n")
                
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            cap.show_frame(annotated_frame)
        except AttributeError:
            pass