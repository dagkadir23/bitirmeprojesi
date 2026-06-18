import cv2
import hashlib
import json
import time

class CyberSecurityDefense:
    def __init__(self, apply_blur=True, blur_kernel=(5, 5)):
        """
        Adversarial zafiyetleri gidermek ve log güvenliği sağlamak için Siber Güvenlik modülü.
        :param apply_blur: Görüntü ön isleme (defense) uygulansin mi?
        """
        self.apply_blur = apply_blur
        self.blur_kernel = blur_kernel

    def apply_attack(self, frame):
        """
        Etkili Adversarial Saldırı Simülasyonu: 
        YOLO modelleri CNN (Evrişimli Sinir Ağı) tabanlıdır. 
        Suni rastgele gürültü yerine "Yüksek Frekanslı Çizgi/Grid Paraziti" Convolution filtrelerini mahveder.
        İnsan gözü hala kişiyi görür ancak yapay zeka körleşir!
        """
        import numpy as np
        attacked_frame = frame.astype(np.float32)
        h, w = frame.shape[:2]
        
        # Düzenli aralıklarla sert yoğunluk değişimleri (Modelin kenar algısını kırar)
        for i in range(0, h, 6):
            attacked_frame[i:i+3, :] *= 0.3
        for j in range(0, w, 6):
            attacked_frame[:, j:j+3] *= 1.8
            
        return np.clip(attacked_frame, 0, 255).astype('uint8')

    def apply_defense(self, frame):
        """
        Siber Savunma Algoritması (Anti-Adversarial):
        Düşman tarafından eklenen yapısal gürültüleri Median Filtresi ve Keskinleştirme 
        dizisiyle temizler ve YOLO'nun tekrar çalışmasını sağlar.
        """
        if not self.apply_blur:
            return frame
        
        import numpy as np
        
        # 1. Aşama: Median Blur (Sert/Grid gürültüleri mükemmel temizler)
        defended = cv2.medianBlur(frame, 7)
        
        # 2. Aşama: Hafif Gaussian yumuşatma
        defended = cv2.GaussianBlur(defended, self.blur_kernel, 0)
        
        # 3. Aşama: Keskinleştirme (Sharpening) - YOLO nesne kenarlarını tekrar belirginleştirir
        kernel = np.array([[-1,-1,-1], 
                           [-1, 9,-1], 
                           [-1,-1,-1]])
        defended = cv2.filter2D(defended, -1, kernel)
        
        return defended

    def generate_log_hash(self, log_data):
        """
        Gelen log bilgisinin (Anomali detayları) değiştirilemezliğinden (Integrity) emin olmak için
        SHA-256 kriptografik hash değeri üretir.
        """
        # Veriyi json stringine çevir ve hash'le
        data_string = json.dumps(log_data, sort_keys=True).encode('utf-8')
        log_hash = hashlib.sha256(data_string).hexdigest()
        return log_hash

    def verify_log_hash(self, log_data, original_hash):
        """
        Veritabanından alınan bir logun değiştirilip değiştirilmediğini (veri zehirleme / poisoning) kontrol eder.
        """
        return self.generate_log_hash(log_data) == original_hash
