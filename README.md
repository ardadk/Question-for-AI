
# Question for AI (QfAI)

**Question for AI (QfAI)**, Python ve PyQt5 ile oluşturulmuş, kullanıcı dostu bir yapay zeka uygulamasıdır. Bu uygulama, videolar üzerinde metin tabanlı sorgulamalara cevaplar üretip, sesli yanıtlarla geri dönüş yapar. Ayrıca, karakter oluşturma ve bunlara özel ses/medya yönetimi gibi özellikler sunar.

## Özellikler

- **Karakter Yönetimi**:
  - Kullanıcı tanımlı karakterler ekleyebilir.
  - Fotoğraf ve ses dosyalarını karakterlerle ilişkilendirme.
  - Karakterleri düzenleme veya silme.

- **API Entegrasyonu**:
  - Google Gemini API'si ile entegrasyon.
  - Kullanıcılar, projeye özel API anahtarlarını girerek sorulara yapay zeka yanıtları alabilir.

- **TTS (Text-to-Speech)**:
  - Yanıtlar, kullanıcının karakterine özgü seslerle seslendirilebilir.

- **Video Yönetimi**:
  - Video oynatma ve karakterlerin dudak hareketlerini içeren özel çıktılar oluşturma.

## Gereksinimler

Bu proje için aşağıdaki yazılım ve kütüphaneler gereklidir:

- Python 3.8 veya üzeri
- PyQt5
- OpenCV
- PyTorch
- [TTS API](https://github.com/coqui-ai/TTS)
- Google Generative AI Kitaplığı

## Kurulum

1. **Gereksinimleri Yükleme**:
   - Gerekli kütüphaneleri yüklemek için aşağıdaki komutu çalıştırın:
     ```bash
     pip install -r requirements.txt
     ```

2. **API Key Ayarları**:
   - `config.json` dosyasına Google Gemini API anahtarınızı girin veya uygulama içerisinden API-Key ayarlarını yapın.

3. **Karakter Veritabanı**:
   - Uygulama, karakter bilgilerini `characters.json` dosyasında saklar. Dosya mevcut değilse, ilk çalıştırmada otomatik oluşturulur.

## Kullanım

1. **Uygulamayı Çalıştırma**:
   ```bash
   python QfAI.py
   ```

2. **Karakter Ekleme**:
   - Sağ menüdeki `Karakter Ekle` butonunu kullanarak yeni bir karakter ekleyebilirsiniz.

3. **Sorgu Çalıştırma**:
   - Karakter seçimi yapıp, alt kısımdaki metin alanına sorgunuzu yazın ve `Çalıştır` butonuna tıklayın.

4. **Videoyu Oynatma**:
   - Uygulama, dudak senkronizasyonu yapılmış videoyu oluşturur ve otomatik oynatır.

## Dosya Yapısı

- `QfAI.py`: Ana uygulama dosyası.
- `config.json`: API ayarlarını içeren yapılandırma dosyası.
- `characters.json`: Karakter bilgilerini saklar.
- `outputs/`: Uygulama tarafından oluşturulan çıktı dosyalarının kaydedileceği klasör.

## Lisans

Bu proje, MIT Lisansı ile lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına göz atın.

## Katkıda Bulunma

Katkıda bulunmak için lütfen aşağıdaki adımları takip edin:
1. Projeyi forklayın.
2. Yeni bir branch oluşturun (`git checkout -b feature-isim`).
3. Değişikliklerinizi yapın ve commit edin (`git commit -m 'Yeni özellik'`).
4. Branch'i push edin (`git push origin feature-isim`).
5. Bir Pull Request oluşturun.

---

### İletişim
Eğer herhangi bir sorunuz veya öneriniz varsa, lütfen benimle iletişime geçin.
