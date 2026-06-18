import time
import cv2
def draw_anomaly_box(frame, box, score, is_anomaly=False):
    """
    Tespit edilen alanı (bounding box) ve anomali skorunu çizer.
    """
    x1, y1, x2, y2 = box
    
    # Anomali ise kırmızı (0,0,255), normal ise yeşil (0,255,0)
    color = (0, 0, 255) if is_anomaly else (0, 255, 0)
    label = "ANOMALI!" if is_anomaly else "Normal"
    
    # Kutuyu çiz
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    
    # Arka planıyla birlikte yazıyı çiz
    text = f"{label} | Skor: {score:.3f}"
    
    # Gerekli kütüphane içe aktarımını fonksiyon içine veya en üste eklemek için (utils içinde cv2 gereklidir)
    
    (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
    cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def log_event(box, score, frame):
    """
    İleride Django Backend'e (API) veri yollamak için kullanılacak fonksiyon taslağı.
    Şimdilik sadece konsola loglama yapar.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] KRD: {box} | Hata Skoru: {score:.3f} -> Backend'e LOGLANDI.")
