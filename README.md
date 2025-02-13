# Baret Tanıma Sistemi

Bu proje, kamera ve görüntü işleme teknikleri kullanarak işçilerin baret takıp takmadığını tespit eden ve bu bilgiyi PLC'ye aktaran bir sistemdir. İşçiler baret takmadığında uyarı verir, kırmızı led yakar ve kapıyı açmaz, baret takıldığında ise yeşil led yakar ve kapıyı açar.

TIA Portal üzerindeki sistemi görmek için "tia_portal_to_pyhton_V18_1.ap18" dosyasını açın. Simule etmek için TIA Portal Advanced kullanabilirsiniz.

Networkler "görseller" içerisinde verilmiştir.
Geliştirilen kodlar "barettanima.py" dosyası içindedir

## Özellikler

- Kamera kullanarak işçilerin baret takıp takmadığını tespit etme
- PLC'ye bilgi gönderme ve kapıyı açma
- Baret takmayan işçileri tespit etme ve uyarı verme
- Kapı açık olduğunda 10 saniye sonra buzzer'ı çalıştırma

## Gereksinimler

- Python 
- OpenCV
- cvzone
- YOLOv8
- snap7
- Siemens S7-1200 PLC
- TIA Portal yazılımı

### Python Kurulumunu Yapın

### PLC Ayarlarını Yapın

1. **TIA Portal**'ı açın ve mevcut projenizi yükleyin.
2. **PLC yapılandırmasını** yapın:
   - IP adresini doğru şekilde ayarlayın.
   - Giriş ve çıkışları (Q0.1, Q0.2) tanımlayın.
   - Zamanlayıcı ve buzzer ayarlarını yapın.

### Kapı Açık ve Buzzer Ayarlarını Yapın

## YAZARLAR:
[@ofarukusta](https://github.com/ofarukusta) <br/>


