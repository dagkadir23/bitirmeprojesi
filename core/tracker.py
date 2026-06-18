import time
import uuid

class AnomalyTracker:
    def __init__(self, timeout=2.0):
        """
        Olay (Incident) Takipçisi. Saniyelik frame'lerden gelen anomali sinyallerini
        tek bir anlamlı vakaya dönüştürür.
        :param timeout: Kaç saniye anomali kesilirse olayın bittiği kabul edilsin (Yalancı kopmaları önlemek için)
        """
        self.timeout = timeout
        self.active_event = None
        self.completed_events = []

    def update(self, is_anomaly, score, behavior_type="Bilinmiyor"):
        """
        Kamera döngüsündeki her frame için çağrılır.
        """
        current_time = time.time()
        
        if is_anomaly:
            if self.active_event is None:
                # Yeni olay başlat
                self.active_event = {
                    "id": str(uuid.uuid4())[:8].upper(),
                    "start_time": current_time,
                    "last_seen_time": current_time,
                    "max_score": score,
                    "behavior_type": behavior_type,
                    "duration": 0.0
                }
            else:
                # Olay güncelleniyor
                self.active_event["last_seen_time"] = current_time
                self.active_event["duration"] = current_time - self.active_event["start_time"]
                
                # En yüksek tehlike skorunu kaydet
                if score > self.active_event["max_score"]:
                    self.active_event["max_score"] = score
                    
                # Eğer farklı bir davranış geldiyse tipini güncelle (En tehlikelisine doğru)
                if behavior_type != "Bilinmiyor" and behavior_type != "Normal":
                    self.active_event["behavior_type"] = behavior_type
                    
        else:
            # Şu an normal ama önceden süren bir olay varsa, bitmiş mi diye kontrol et
            if self.active_event is not None:
                if current_time - self.active_event["last_seen_time"] > self.timeout:
                    # Olay zaman aşımına uğradı, tamamlananlara ekle
                    event_copy = self.active_event.copy()
                    event_copy["end_time"] = event_copy["last_seen_time"]
                    self.completed_events.insert(0, event_copy) # En yeni en başa (Stack)
                    self.active_event = None

    def get_all_reports(self):
        """Tüm tamamlanmış vakaları döndürür (Arayüz ve Dışa Aktarım için)"""
        return self.completed_events
