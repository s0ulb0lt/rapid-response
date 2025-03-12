# from ultralytics import YOLO

# model = YOLO("yolo11m_v6.pt")
# if __name__ == '__main__':
#     results = model.train(data="v5.yaml", 
#                           epochs=80, 
#                           imgsz=640, 
#                           device=0, 
#                           cache=False, 
#                           plots=True,
#                           workers=16, 
#                           optimizer="AdamW", 
#                           lr0=5.23559e-05, 
#                           momentum=0.9)

from ultralytics import YOLO
import os

#v5
model = YOLO("yolo11m.pt")
if __name__ == '__main__':
    results = model.train(data="v4.yaml", 
                          epochs=80, 
                          imgsz=640, 
                          device=0, 
                          cache=False, 
                          plots=False,
                          workers=16)







#v5 2nd
model = YOLO("yolo11m_v4.pt")
if __name__ == '__main__':
    results2nd = results.train(data="v5.yaml", 
                            epochs=80, 
                            imgsz=640, 
                            device=0, 
                            cache=False,
                            lr0=2.48586e-05,
                            plots=True,
                            workers=16)
    
model = YOLO("yolo11m_v5.pt")
if __name__ == '__main__':
    results2nd = results.train(data="v6.yaml", 
                            epochs=80, 
                            imgsz=640, 
                            device=0, 
                            cache=False,
                            lr0=5.23559e-05,
                            plots=True,
                            workers=16)