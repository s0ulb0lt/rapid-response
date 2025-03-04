# from collections import defaultdict

# import cv2
# import numpy as np

# from ultralytics import YOLO

# # Load the YOLO11 model
# model = YOLO("yolo11m_v6.pt")
# track_history = defaultdict(lambda: [])

# cap = cv2.VideoCapture(0)

# def getColours(cls_num):
#     base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
#     color_index = cls_num % len(base_colors)
#     increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
#     color = [base_colors[color_index][i] + increments[color_index][i] * 
#     (cls_num // len(base_colors)) % 256 for i in range(3)]
#     return tuple(color)

# while cap.isOpened():
#     success, frame = cap.read()
#     if success:
#         results = model.track(frame, persist=True)
#         boxes = results[0].boxes.xywh.cpu()
#         track_ids = results[0].boxes.id.int().cpu().tolist()
#         annotated_frame = results[0].plot()
#         for box, track_id in zip(boxes, track_ids):
#             x, y, w, h = box
#             track = track_history[track_id]
#             track.append((float(x), float(y)))
#             if len(track) > 30:
#                 track.pop(0)
#             points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
#             cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)
#         cv2.imshow("YOLO11 Tracking", annotated_frame)
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break
#     else:
#         break
# cap.release()
# cv2.destroyAllWindows()

from collections import defaultdict

import cv2
import numpy as np
from pymavlink import mavutil
from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("yolo11m_v6.pt")

# Open the video file
video_path = "path/to/video.mp4"
cap = cv2.VideoCapture(0)

# Store the track history
track_history = defaultdict(lambda: [])

# connection = mavutil.mavlink_connection('0.0.0.0:14550')
# connection.wait_heartbeat()
# print("Heartbeat from system (system %u component %u)" % (connection.target_system, connection.target_component))

# Loop through the video frames
with open("people.txt", "w") as file:
    while cap.isOpened():
        # Read a frame from the video
        ret, frame = cap.read()
        print("next")

        if ret:
            # Run YOLO11 tracking on the frame, persisting tracks between frames
            results = model.track(frame, persist=True, )
            annotated_frame = results[0].plot()

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            # Get the boxes and track IDs
            try:
                boxes = results[0].boxes.xywh.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                classes = results[0].boxes.cls.cpu()
                print("Detection")
            except:
                print("None")
                cv2.imshow("YOLO11 Tracking", annotated_frame) 
                continue;

            # Plot the tracks
            for box, track_id, cls in zip(boxes, track_ids, classes):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))  # x, y center point
                if len(track) > 10 and cls == 4:  # retain 90 tracks for 90 frames
                    track.pop(0)
                    print("POSSIBLE PERSONM!!!!")
                    # msg = connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
                    # print(msg)
                    # file.write(str(track_id) + "\t" + str(msg.lat) + "\t" + str(msg.lon) + "\n")

                # Draw the tracking lines
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            # Display the annotated frame
            cv2.imshow("YOLO11 Tracking", annotated_frame)

            # Break the loop if 'q' is pressed
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()