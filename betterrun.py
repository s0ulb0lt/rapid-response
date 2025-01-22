from ultralytics import YOLO
import cv2

model = YOLO("yolo11n_HIT_V1.pt")

results = model.predict(source="0", show=True)

print(results)