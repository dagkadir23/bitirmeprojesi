import cv2
import time
from core.camera import WebCamera
from core.detector import HumanDetector
from core.autoencoder import AnomalyDetector
from core.utils import draw_anomaly_box, log_event

def main():
    print("Sistem başlatılıyor...")
    
    # 1. Modüllerin başlatılması
    try:
        camera = WebCamera(camera_index=0)
    except Exception as e:
        print(e)
        return

    # YOLOv8 nano CPU/GPU'da hızlı çalıştığı için tercih ettik.
    detector = HumanDetector(model_name="yolov8n.pt")
    
    # AnomalyDetector 'model_path' almadan rastgele sahte bir skor üretir (geliştirme aşaması için).
    # İleride eğitilmiş model olunca: AnomalyDetector(model_path="trained_ae.pth", threshold=0.15)
    anomaly_detector = AnomalyDetector(threshold=0.20)

    print("\n[BİLGİ] Çıkmak için 'q' tuşuna basın.")
    
    # Performans ölçümü için
    prev_time = time.time()

    try:
        while True:
            ret, frame = camera.get_frame()
            if not ret:
                print("Kameradan görüntü alınamadı!")
                break

            # FPS Hesaplama
            current_time = time.time()
            fps = 1 / (current_time - prev_time)
            prev_time = current_time

            # 2. İnsan Tespiti (Analysis Module - Object Detection)
            humans = detector.detect(frame)
            
            # 3. Her bir insan bölgesi için anomali skoru hesaplama (Autoencoder)
            for human in humans:
                box = human["box"]
                crop = human["crop"]
                
                # Autoencoder skorlaması
                score = anomaly_detector.compute_anomaly_score(crop)
                is_anomaly = anomaly_detector.is_anomaly(score)
                
                # 4. Haberleşme / Loglama Modülü
                if is_anomaly:
                    log_event(box, score, frame)
                
                # 5. Ekrana Çizdirme
                draw_anomaly_box(frame, box, score, is_anomaly=is_anomaly)

            # Ekranda FPS bilgisini göster
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            # Görüntüyü Kullanıcıya Göster
            cv2.imshow("Akilli Guvenlik Kamerasi - Demo", frame)

            # 'q' tuşuna basılırsa döngüden çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n[BİLGİ] Kullanıcı tarafından durduruldu.")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Sistem güvenli bir şekilde kapatıldı.")

if __name__ == "__main__":
    main()
