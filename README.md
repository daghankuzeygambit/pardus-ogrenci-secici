# 🎲 Pardus Öğrenci & Grup Seçici

Sınıf listesini yükleyip "çark/kura" hissi veren bir animasyonla rastgele
öğrenci veya çalışma grubu seçen açık kaynak masaüstü uygulaması.

TEKNOFEST Pardus Hata Yakalama ve Öneri Yarışması (Geliştirme Kategorisi)
kapsamında geliştirilmiştir.

## 🎯 Neden?

Derste sözlüye kaldıracak öğrenci seçerken "hocam hep beni kaldırıyorsunuz"
itirazı sık yaşanır. Bu araç, kriptografik olarak güvenli/öngörülemez bir
rastgele seçim yaparak (ve tüm sınıf bir tur tamamlanmadan kimse ikinci kez
seçilmeden) hem adil hem eğlenceli bir çözüm sunar.

## 🔒 Neden `secrets` Modülü?

Python'un standart `random` modülü Mersenne Twister algoritmasını kullanır;
istatistiksel olarak iyi dağılır ama **kriptografik olarak güvenli
değildir** — çıktı dizisinden iç durum teorik olarak tahmin edilebilir.
`secrets` modülü işletim sisteminin kendi rastgelelik kaynağını
(`os.urandom`) kullanır. "Gerçekten adil/öngörülemez bir seçim yapıldı"
iddiasının arkasında durabilmek için doğru araç budur.

## 📋 Özellikler

- 📁 CSV/Excel (.xlsx) dosyasından sınıf listesi içe aktarma
- ✍️ GUI'den manuel öğrenci ekleme/silme
- 🎰 Yavaşlayan "slot machine" tarzı seçim animasyonu
- 🎯 Kriptografik güvenli rastgele seçim (`secrets.choice`)
- 🔁 "Havuz" mantığı: bir öğrenci, tüm sınıf bir tur tamamlanmadan tekrar
  seçilmez (adil dağılım) — istenirse elle sıfırlanabilir
- 👥 Rastgele grup oluşturma (grup sayısına veya grup başına kişi
  sayısına göre)
- 💾 Birden fazla sınıf listesi kalıcı olarak saklanır

## 🚀 Kurulum

```bash
git clone https://github.com/KULLANICI_ADIN/pardus-ogrenci-secici.git
cd pardus-ogrenci-secici

pip3 install -r requirements.txt --break-system-packages

python3 main.py
```

## 💡 Kullanım

1. **"➕ Yeni Sınıf"** ile bir sınıf oluştur (örn: "9-A")
2. **"📋 Sınıf Listesi"** sekmesinden CSV/Excel yükle ya da manuel öğrenci ekle
3. **"🎯 Öğrenci Seç"** sekmesinden **"🎲 RASTGELE SEÇ"** butonuna bas
4. **"👥 Grup Oluştur"** sekmesinden grup sayısı/boyutu belirleyip grupları oluştur

## 🧩 Proje Yapısı

```
pardus-ogrenci-secici/
├── main.py              # Giriş noktası
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── sinif_listesi.py  # CSV/Excel içe aktarma, kalıcı sınıf yönetimi
│   ├── secici.py         # Kriptografik güvenli rastgele seçim + gruplama
│   └── gui.py            # PyQt6 arayüzü + animasyon
└── README.md
```

## 📜 Lisans

MIT License
