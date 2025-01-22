from ultralytics import YOLO
import torch
print(torch.cuda.is_available(), torch.cuda.device_count(), torch.cuda.get_device_name(0))

model = YOLO("yolo11n_HIT_V1.pt")
model.export(format="engine")


