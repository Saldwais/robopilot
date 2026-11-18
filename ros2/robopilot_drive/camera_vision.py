"""YOLO-World wrapper adapted from Saleh's RoboRecognizer, for ROS camera frames."""
from base64 import b64encode
from collections import Counter
from threading import Lock

class CameraVision:
    def __init__(self):
        self.lock=Lock(); self.model=None; self.labels=()
    def analyze(self,jpeg,targets='road,tree,person,dog,stairs'):
        labels=tuple(dict.fromkeys(x.strip() for x in targets.split(',') if x.strip()))
        if len(labels)>8 or sum(map(len,labels))>200: raise ValueError('Limit to 8 target labels and 200 characters.')
        if not self.lock.acquire(blocking=False): return None
        try:
            import cv2, numpy as np
            from ultralytics import YOLOWorld
            frame=cv2.imdecode(np.frombuffer(jpeg,np.uint8),cv2.IMREAD_COLOR)
            if frame is None: raise ValueError('Could not decode camera image')
            if self.model is None: self.model=YOLOWorld('yolov8s-worldv2.pt')
            if labels!=self.labels: self.model.set_classes(list(labels)); self.labels=labels
            res=self.model.predict(frame,imgsz=640,conf=.25,max_det=60,device='cpu',verbose=False)[0]
            boxes=[{'label':res.names[int(c)],'confidence':round(float(conf),3),'box':[round(float(v),5) for v in box]} for c,conf,box in zip(res.boxes.cls.tolist(),res.boxes.conf.tolist(),res.boxes.xyxyn.tolist())]
            ok,enc=cv2.imencode('.jpg',res.plot())
            return {'boxes':boxes,'counts':dict(Counter(x['label'] for x in boxes)),'annotated_jpeg':b64encode(enc).decode() if ok else None}
        finally: self.lock.release()
