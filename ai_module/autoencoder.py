import torch
import torch.nn as nn
import numpy as np
import cv2

class SimpleAutoencoder(nn.Module):
    """
    Basit bir evrişimli (Convolutional) Autoencoder mimarisi iskeleti.
    İleride 'normal' video kareleriyle eğitilerek anomali tespitinde kullanılacaktır.
    """
    def __init__(self):
        super(SimpleAutoencoder, self).__init__()
        
        # Encoder: Görüntüyü sıkıştırır
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.ReLU()
        )
        
        # Decoder: Sıkıştırılmış veriden görüntüyü yeniden oluşturur
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 16, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(16, 3, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.Sigmoid() # Görüntü piksel değerlerini 0-1 aralığında döndürür
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

class AnomalyDetector:
    def __init__(self, model_path=None, threshold=0.15):
        """
        Anomali tespiti sınıfı.
        :param model_path: Eğitilmiş PyTorch model `.pth` dosyası yolu (varsa).
        :param threshold: Anomali olarak kabul edilecek MSE hata eşiği.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = SimpleAutoencoder().to(self.device)
        self.threshold = threshold
        self.is_trained = False
        
        if model_path:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.eval()
                self.is_trained = True
                print(f"Autoencoder modeli başarıyla yüklendi: {model_path}")
            except Exception as e:
                print(f"Model yüklenirken hata oluştu: {e}")
        else:
            print("Uyarı: Herhangi bir eğitilmiş Autoencoder modeli verilmedi. Anomali skoru rastgele/test amaçlı üretilecektir.")

    def preprocess_image(self, crop, target_size=(64, 64)):
        """
        Kırpılmış görüntüyü (crop) modele uygun hale getirir.
        """
        # Yeniden boyutlandırma
        resized = cv2.resize(crop, target_size)
        
        # Normalize etme (0-1 arasına)
        normalized = resized.astype(np.float32) / 255.0
        
        # HWC (Height-Width-Channel) formatından CHW (Channel-Height-Width) formatına çevirme
        chw = np.transpose(normalized, (2, 0, 1))
        
        # Batch boyutu (1) ekleme
        tensor = torch.tensor(chw).unsqueeze(0).to(self.device)
        return tensor

    def compute_anomaly_score(self, crop, is_attacked=False):
        """
        Verilen kırpılmış insan görüntüsü için Yeniden Yapılandırma Hatasını ve Davranışını hesaplar.
        """
        if not self.is_trained:
            # Gelişmiş Etkileşimli Mock Analiz
            h, w = crop.shape[:2]
            aspect_ratio = w / (h + 0.001)
            
            # Adversarial müdahale (perturbation) flag'i aktifse
            if is_attacked:
                return np.random.uniform(0.50, 0.99), "Adversarial Perturbation Tespiti"
                
            # Yakınlık (Proximity) bazlı risk analizi
            # Bounding box alanı üzerinden kameraya yakınlık tahmin ediliyor
            crop_area = h * w
            
            if crop_area > 40000:
                # Ekranda büyük alan kaplıyorsa kameraya çok yakındır
                base_score = np.random.uniform(0.75, 0.95)
                desc = "Yüksek Risk: Kameraya Çok Yakın Kişi"
            else:
                # Ekranda küçük alan kaplıyorsa uzaktan geçen biridir
                base_score = np.random.uniform(0.30, 0.55)
                desc = "Orta Risk: Uzaktan Geçen Kişi"
                
            # Eğer kişi yatay duruyorsa (düşme durumu) skoru ez veya yüksek tut
            if aspect_ratio >= 0.70: 
                base_score = max(base_score, np.random.uniform(0.60, 0.85))
                desc = "Yüksek Risk: Olası Düşme Tespiti"
                
            return base_score, desc
        
        input_tensor = self.preprocess_image(crop)
        
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
            
        loss = nn.MSELoss()(output_tensor, input_tensor).item()
        return loss, "Derin Öğrenme Tespiti"

    def is_anomaly(self, score):
        """
        Gelen skor eşik değerinden büyükse anomali (True) döner.
        """
        return score > self.threshold
