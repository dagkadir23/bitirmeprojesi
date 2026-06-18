from ultralytics import YOLO

class HumanDetector:
    def __init__(self, model_name="yolov8n.pt"):
        """
        YOLOv8 ile insan tespiti yapacak sınıf.
        :param model_name: Kullanılacak YOLO modeli. 'yolov8n.pt' genel kullanım için hızlıdır.
        """
        print(f"[{model_name}] modeli yükleniyor...")
        self.model = YOLO(model_name)
    
    def detect(self, frame):
        """
        Verilen frame üzerinde sadece insanları (sınıf 0) tespit eder.
        :param frame: OpenCV'den alınan BGR formatında görüntü.
        :return: Tespit edilen insanların koordinatları ve kırpılmış bölgeleri.
                 List of dictionaries -> [{'box': [x1, y1, x2, y2], 'crop': image_array}, ...]
        """
        
        # YOLO'nun 'classes=[0]' parametresi sadece insan (person) sınıfını tespit etmesini sağlar.
        results = self.model.predict(source=frame, classes=[0], verbose=False)
        
        humans = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Koordinatları tam sayı olarak alıyoruz
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Güven skoru (confidence)
                conf = float(box.conf[0])
                
                # Sınırların geçerli olduğundan emin olalım (out of bounds hatasını önlemek için)
                h, w, _ = frame.shape
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                # Sadece mantıklı boyuttaki tespitleri işleyelim
                if (x2 - x1) > 10 and (y2 - y1) > 10:
                    crop = frame[y1:y2, x1:x2]
                    humans.append({
                        "box": (x1, y1, x2, y2),
                        "conf": conf,
                        "crop": crop
                    })
        
        return humans
