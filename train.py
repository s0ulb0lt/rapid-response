from ultralytics import YOLO

model = YOLO("yolo11m_v6.pt")


if __name__ == '__main__':
    results = model.train(data="v5.yaml", epochs=80, imgsz=640, device=0, cache=False, plots=True, workers=16, optimizer="AdamW", lr0=5.23559e-05, momentum=0.9)