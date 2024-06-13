# KÜTÜPHANELERİ İÇERİ AKTARMA
import cv2 # Görüntü işleme ve video analiz kütüphanesi
import cvzone # OpenCV'yi kullanışlı hale getiren yardımcı kütüphane
from ultralytics import YOLO # Nesne algılama için kullanılan YOLO modelli kütüphane
from time import time # Zaman ölçümü için kullanılan kütüphane
import math # Matematiksel işlemler için kullanılan kütüphane
import numpy as np # Matematiksel hesaplamalar için kullanılan kütüphane
import torch # Derin öğrenme için kullanılan kütüphane
import snap7 # Siemens PLC ile iletişim için kullanılan kütüphane

# PLC'YE BAĞLANMA
plc = snap7.client.Client() #PLC istemci nesnesi oluşturur
plc.connect("192.168.0.1", 0, 1) # Bu komut, belirli bir IP adresine sahip PLC'ye bağlanır, Rack Numarası, Slot Numarası

#DEĞİŞKEN TANIMLARI VE MODEL YÜKLEME
confidence = 0.5 # Algılama için minimum güven puanı
cap = cv2.VideoCapture(0) # İşlenecek olan video dosyasını yükler

model = YOLO("best3.pt") # YOLO modelini "best3.pt" dosyasından yükler
# Modeli CPU üzerinde çalıştır
model.to("cpu")
classNames2 = ['helmet', "no helmet"] # Algılanacak sınıfların isimleri

# VİDEO İŞLEME DÖNGÜSÜ
start_time = time()
while True: # Video kare kare işlenir
    success, frame = cap.read() # Bir sonraki kareyi okur
    # Başarısız olursa döngü kırılır
    if not success:
        break

    results = model(frame, stream=True, verbose=False) # YOLO modeliyle kare üzerinde nesne algılama işlemi yapar.
    is_no_helmet_detected = False # Baret takmayan işçi algılanıp algılanmadığını belirlemek için kullanılan bayrak
    is_human_detected = False # İnsan algılanıp algılanmadığını belirlemek için kullanılan bayrak

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0] # Algılanan nesnenin koordinatlarını alır
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            conf = math.ceil((box.conf[0] * 100)) / 100 # Algılama güven puanını hesaplar

            cls = int(box.cls[0]) # Algılanan nesnenin sınıfını belirler
            label = classNames2[cls]

            if conf > 0.5:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2) # Algılanan nesnenin etrafına dikdörtgen çizer
                cvzone.putTextRect(frame, f'{label} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1) # Algılanan nesneye sınıf etiketi ekler

                if label in ["helmet", "no helmet"]:
                    is_human_detected = True
                if label == "no helmet":
                    is_no_helmet_detected = True # Baret takmayan işçi algılanırsa uyarı mesajı ekler
                    cv2.rectangle(frame, (50, 605), (450, 635), (255, 255, 255), -1)
                    cv2.putText(frame, "UYARI! BARET TAKMAYAN CALISAN TESPIT EDILDI!",
                                (50, 625), 1, 1, (0, 0, 255), 2, cv2.FONT_HERSHEY_DUPLEX)

    # PLC'YE VERİ YAZMA İŞLEMİ
    if is_human_detected:
        if is_no_helmet_detected:
            prod_rate = plc.db_read(1, 2, 4)  #PLC'deki veri bloğu 1'den (DB1), 2. byte adresinden başlayarak 4 byte'lık veri okur
            snap7.util.set_real(prod_rate, 0, 1) # Baret takmayan işçi algılandığında PLC'ye 1 değeri yazılır
            plc.db_write(1, 2, prod_rate) #Değiştirilen prod_rate verisini tekrar PLC'deki veri bloğuna yazar. Bu işlem, DB1'in 2. byte adresine yazma işlemi yapar
            print("PLC'de 1 değeri ataması yapıldı!")
        else:
            prod_rate = plc.db_read(1, 2, 4) #PLC'deki veri bloğu 1'den (DB1), 2. byte adresinden başlayarak 4 byte'lık veri okur
            snap7.util.set_real(prod_rate, 0, 0) # Baret takan işçi algılandığında PLC'ye 0 değeri yazılır
            plc.db_write(1, 2, prod_rate) #Değiştirilen prod_rate verisini tekrar PLC'deki veri bloğuna yazar. Bu işlem, DB1'in 2. byte adresine yazma işlemi yapar
            print("PLC'de 0 değeri ataması yapıldı!")
    else:
        prod_rate = plc.db_read(1, 2, 4) #PLC'deki veri bloğu 1'den (DB1), 2. byte adresinden başlayarak 4 byte'lık veri okur
        snap7.util.set_real(prod_rate, 0, 1) # Hiç insan algılanmadığında PLC'ye 1 değeri yazılır
        plc.db_write(1, 2, prod_rate) #Değiştirilen prod_rate verisini tekrar PLC'deki veri bloğuna yazar. Bu işlem, DB1'in 2. byte adresine yazma işlemi yapar
        print("Hiç insan algılanmadı, PLC'de 1 değeri ataması yapıldı!")

    # PLC'DEN VERİ OKUMA
    db_bytearray = plc.db_read(1, 0, 50) #PLC'deki veri bloğundan (DB) veri okur.(Veri bloğu numarası(DB1), Okumaya başlama adresi,Okunacak miktar(byte))
    total_prod = snap7.util.get_int(db_bytearray, 0) #Byte dizisinden (DB_bytearray) bir tam sayı (integer) okur
    prod_rate = snap7.util.get_real(db_bytearray, 2) #Byte dizisinden bir gerçek sayı (float) okur
    message = snap7.util.get_string(db_bytearray, 6) #Byte dizisinden bir dize (string) okur

    #print("Total Production: ", total_prod, "\nProduction Rate: ", prod_rate, "\nMessage: ", message)

    # FPS HESAPLAMA VE GÖRÜNTÜ GÖSTERME
    end_time = time()
    fps = 1 / (end_time - start_time)
    fps = int(fps) # FPS (saniyedeki kare sayısı) hesaplanır
    start_time = end_time

    cv2.putText(frame, f'FPS: {str(fps)}', (10, 20), 1, 1, (255, 255, 255), 1, cv2.FONT_HERSHEY_DUPLEX) # FPS değerini yazar

    cv2.imshow("Image", frame) # İşlenmiş kareyi gösterir
    if cv2.waitKey(1) & 0xFF == ord("q"): # 'q' tuşuna basıldığında döngü kırılır
        break

# KAYNAKLARI SERBEST BIRAKMA
cap.release() # Video dosyalarını serbest bırakır
cv2.destroyAllWindows() # Tüm OpenCV pencerelerini kapatır
