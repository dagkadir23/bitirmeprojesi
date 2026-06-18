import cv2
import threading

class WebCamera:
    def __init__(self, camera_index=0, frame_skip=2):
        """
        Bilgisayar kamerasından THREAD kullanarak hızlı ve kesintisiz görüntü almak için sınıf.
        :param camera_index: Kamera aygıt indeksi.
        :param frame_skip: Kaç karede bir analiz yapılacağı (FPS Yönetimi / Performans).
        """
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Kamera Çözünürlüğünü stabilize etme (Performans için)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.cap.isOpened():
            raise ValueError(f"Kamera (index: {self.camera_index}) açılamadı!")

        self.ret, self.frame = self.cap.read()
        self.stopped = False
        
        # Frame Atlama Mantığı
        self.frame_skip = frame_skip
        self.frame_count = 0
        
        # Thread'i Başlat
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        """
        Arkaplanda sürekli olarak kameradan en güncel frame'i okur. (Producer)
        Bu sayede I/O bekleme süresi ortadan kalkar, performans artar.
        """
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                self.stopped = True
            else:
                self.ret = ret
                self.frame = frame

    def get_frame(self):
        """
        Kameradan alınan en güncel frame'i döndürür. (Consumer)
        Ayrıca frame skipping (kare atlatma) mantığını işler.
        :return: (is_valid, ought_to_process, frame)
        """
        self.frame_count += 1
        
        process_this_frame = (self.frame_count % self.frame_skip == 0)
        
        return self.ret, process_this_frame, self.frame.copy() if self.ret else None

    def release(self):
        """
        Kamera kaynağını serbest bırakır.
        """
        self.stopped = True
        self.thread.join()
        if self.cap.isOpened():
            self.cap.release()
