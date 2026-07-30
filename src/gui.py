import sys
import secrets

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QComboBox, QFileDialog, QMessageBox, QInputDialog, QTabWidget,
    QSpinBox, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from src.sinif_listesi import SinifListesiYoneticisi
from src.secici import SeciciMotoru


class OgrenciSeciciPenceresi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎲 Pardus Öğrenci Seçici")
        self.setGeometry(250, 150, 520, 640)
        self.setStyleSheet(self.stil())

        self.yonetici = SinifListesiYoneticisi()
        self.aktif_secici = None  # SeciciMotoru örneği (aktif sınıf seçilince oluşur)
        self._animasyon_timer = QTimer()
        self._animasyon_timer.timeout.connect(self._animasyon_karesi)
        self._animasyon_adimi = 0
        self._animasyon_toplam_adim = 0
        self._animasyon_sonuc = None

        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)
        layout = QVBoxLayout()

        baslik = QLabel("🎲 ÖĞRENCİ & GRUP SEÇİCİ")
        baslik_font = QFont()
        baslik_font.setPointSize(16)
        baslik_font.setBold(True)
        baslik.setFont(baslik_font)
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        sinif_layout = QHBoxLayout()
        sinif_layout.addWidget(QLabel("Sınıf:"))
        self.sinif_secici = QComboBox()
        self.sinif_secici.currentTextChanged.connect(self._sinif_degisti)
        sinif_layout.addWidget(self.sinif_secici)

        yeni_sinif_buton = QPushButton("➕ Yeni Sınıf")
        yeni_sinif_buton.clicked.connect(self._yeni_sinif_olustur)
        sinif_layout.addWidget(yeni_sinif_buton)
        layout.addLayout(sinif_layout)

        sekmeler = QTabWidget()
        sekmeler.addTab(self._secim_sekmesi(), "🎯 Öğrenci Seç")
        sekmeler.addTab(self._grup_sekmesi(), "👥 Grup Oluştur")
        sekmeler.addTab(self._liste_yonetimi_sekmesi(), "📋 Sınıf Listesi")
        layout.addWidget(sekmeler)

        ana_widget.setLayout(layout)
        self._sinif_listesini_yenile()

    def stil(self):
        return """
        QMainWindow { background-color: #1e1e1e; }
        QLabel { color: #ffffff; }
        QComboBox, QLineEdit, QSpinBox {
            background-color: #2d2d2d; color: white; border: 1px solid #444;
            border-radius: 4px; padding: 6px;
        }
        QPushButton {
            background-color: #6a1b9a; color: white; border: none;
            border-radius: 6px; font-size: 13px; font-weight: bold; padding: 10px;
        }
        QPushButton:hover { background-color: #7b1fa2; }
        QListWidget, QTextEdit {
            background-color: #2d2d2d; color: white; border: 1px solid #444;
        }
        QTabWidget::pane { border: 1px solid #444; }
        QTabBar::tab { background-color: #2d2d2d; color: white; padding: 8px 14px; }
        QTabBar::tab:selected { background-color: #6a1b9a; }
        """

    # ---------------- SINIF YÖNETİMİ (ortak) ----------------
    def _sinif_listesini_yenile(self):
        self.sinif_secici.blockSignals(True)
        secili = self.sinif_secici.currentText()
        self.sinif_secici.clear()
        self.sinif_secici.addItems(self.yonetici.sinif_adlarini_getir())
        if secili:
            idx = self.sinif_secici.findText(secili)
            if idx >= 0:
                self.sinif_secici.setCurrentIndex(idx)
        self.sinif_secici.blockSignals(False)
        self._sinif_degisti(self.sinif_secici.currentText())

    def _yeni_sinif_olustur(self):
        ad, ok = QInputDialog.getText(self, "Yeni Sınıf", "Sınıf adı (örn: 9-A):")
        if ok and ad.strip():
            self.yonetici.sinif_olustur(ad.strip())
            self._sinif_listesini_yenile()
            idx = self.sinif_secici.findText(ad.strip())
            if idx >= 0:
                self.sinif_secici.setCurrentIndex(idx)

    def _sinif_degisti(self, sinif_adi):
        if sinif_adi:
            ogrenciler = self.yonetici.ogrencileri_getir(sinif_adi)
            self.aktif_secici = SeciciMotoru(ogrenciler)
        else:
            self.aktif_secici = None
        self._liste_widget_yenile()

    # ---------------- SEÇİM SEKMESİ (slot machine animasyonu) ----------------
    def _secim_sekmesi(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.sonuc_kutusu = QLabel("?")
        sonuc_font = QFont()
        sonuc_font.setPointSize(28)
        sonuc_font.setBold(True)
        self.sonuc_kutusu.setFont(sonuc_font)
        self.sonuc_kutusu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sonuc_kutusu.setMinimumHeight(120)
        self.sonuc_kutusu.setStyleSheet(
            "background-color: #2d2d2d; border: 2px solid #6a1b9a; border-radius: 10px;"
        )
        layout.addWidget(self.sonuc_kutusu)

        sec_buton = QPushButton("🎲 RASTGELE SEÇ")
        sec_buton.setMinimumHeight(50)
        sec_buton.clicked.connect(self._secim_baslat)
        layout.addWidget(sec_buton)

        self.havuz_bilgisi = QLabel("")
        self.havuz_bilgisi.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.havuz_bilgisi.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(self.havuz_bilgisi)

        sifirla_buton = QPushButton("🔄 Havuzu Sıfırla (herkes tekrar aday olsun)")
        sifirla_buton.clicked.connect(self._havuzu_sifirla)
        layout.addWidget(sifirla_buton)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _secim_baslat(self):
        if not self.aktif_secici or not self.aktif_secici.tum_ogrenciler:
            QMessageBox.warning(self, "Liste boş", "Önce bu sınıfa öğrenci ekle.")
            return

        # Gerçek sonucu ÖNCEDEN belirle (kriptografik güvenli), animasyon
        # sadece görsel bir gecikme/heyecan katmanıdır, sonucu etkilemez.
        self._animasyon_sonuc = self.aktif_secici.tekli_sec()
        self._animasyon_adimi = 0
        self._animasyon_toplam_adim = 22  # animasyon kare sayısı

        self._animasyon_timer.start(80)  # başlangıç hızı

    def _animasyon_karesi(self):
        self._animasyon_adimi += 1

        if self._animasyon_adimi >= self._animasyon_toplam_adim:
            self._animasyon_timer.stop()
            self.sonuc_kutusu.setText(f"🎉 {self._animasyon_sonuc}")
            self._liste_widget_yenile()
            return

        # Yavaşlayan efekt: adım ilerledikçe timer aralığını artır
        yeni_hiz = 80 + int((self._animasyon_adimi ** 1.7))
        self._animasyon_timer.setInterval(min(yeni_hiz, 400))

        # Ekranda rastgele bir isim göster (gerçek sonuç değil, sadece görsel)
        rastgele_isim = secrets.choice(self.aktif_secici.tum_ogrenciler)
        self.sonuc_kutusu.setText(rastgele_isim)

    def _havuzu_sifirla(self):
        if self.aktif_secici:
            self.aktif_secici.havuzu_sifirla()
            self._liste_widget_yenile()

    # ---------------- GRUP SEKMESİ ----------------
    def _grup_sekmesi(self):
        widget = QWidget()
        layout = QVBoxLayout()

        mod_layout = QHBoxLayout()
        self.grup_modu = QComboBox()
        self.grup_modu.addItems(["Grup sayısına göre", "Grup başına kişi sayısına göre"])
        mod_layout.addWidget(self.grup_modu)

        self.grup_sayi_kutusu = QSpinBox()
        self.grup_sayi_kutusu.setRange(1, 50)
        self.grup_sayi_kutusu.setValue(4)
        mod_layout.addWidget(self.grup_sayi_kutusu)
        layout.addLayout(mod_layout)

        olustur_buton = QPushButton("👥 GRUPLARI OLUŞTUR")
        olustur_buton.clicked.connect(self._gruplari_olustur)
        layout.addWidget(olustur_buton)

        self.grup_sonuc_kutusu = QTextEdit()
        self.grup_sonuc_kutusu.setReadOnly(True)
        self.grup_sonuc_kutusu.setPlaceholderText("Gruplar burada görünecek...")
        layout.addWidget(self.grup_sonuc_kutusu)

        widget.setLayout(layout)
        return widget

    def _gruplari_olustur(self):
        if not self.aktif_secici or not self.aktif_secici.tum_ogrenciler:
            QMessageBox.warning(self, "Liste boş", "Önce bu sınıfa öğrenci ekle.")
            return

        deger = self.grup_sayi_kutusu.value()
        if self.grup_modu.currentIndex() == 0:
            gruplar = self.aktif_secici.gruplara_ayir(grup_sayisi=deger)
        else:
            gruplar = self.aktif_secici.gruplara_ayir(grup_basina_kisi=deger)

        metin = ""
        for i, grup in enumerate(gruplar, 1):
            metin += f"🔹 Grup {i} ({len(grup)} kişi):\n"
            for kisi in grup:
                metin += f"   • {kisi}\n"
            metin += "\n"

        self.grup_sonuc_kutusu.setPlainText(metin)

    # ---------------- SINIF LİSTESİ YÖNETİMİ SEKMESİ ----------------
    def _liste_yonetimi_sekmesi(self):
        widget = QWidget()
        layout = QVBoxLayout()

        dosya_buton = QPushButton("📁 CSV/Excel Dosyasından Yükle")
        dosya_buton.clicked.connect(self._dosyadan_yukle)
        layout.addWidget(dosya_buton)

        ekle_layout = QHBoxLayout()
        self.yeni_ogrenci_kutusu = QLineEdit()
        self.yeni_ogrenci_kutusu.setPlaceholderText("Öğrenci adı")
        ekle_layout.addWidget(self.yeni_ogrenci_kutusu)
        ekle_buton = QPushButton("➕ Ekle")
        ekle_buton.clicked.connect(self._ogrenci_ekle)
        ekle_layout.addWidget(ekle_buton)
        layout.addLayout(ekle_layout)

        self.ogrenci_liste_widget = QListWidget()
        layout.addWidget(self.ogrenci_liste_widget)

        sil_buton = QPushButton("🗑️ Seçileni Sil")
        sil_buton.clicked.connect(self._ogrenci_sil)
        layout.addWidget(sil_buton)

        widget.setLayout(layout)
        return widget

    def _liste_widget_yenile(self):
        self.ogrenci_liste_widget.clear()
        if not self.aktif_secici:
            self.havuz_bilgisi.setText("")
            return

        havuz = self.aktif_secici._henuz_secilmeyenler
        for ogrenci in self.aktif_secici.tum_ogrenciler:
            durum = "🟢" if ogrenci in havuz else "⚪"
            self.ogrenci_liste_widget.addItem(QListWidgetItem(f"{durum} {ogrenci}"))

        self.havuz_bilgisi.setText(
            f"Havuzda kalan (henüz seçilmeyen): {len(havuz)} / {len(self.aktif_secici.tum_ogrenciler)}"
        )

    def _dosyadan_yukle(self):
        sinif_adi = self.sinif_secici.currentText()
        if not sinif_adi:
            QMessageBox.warning(self, "Sınıf yok", "Önce bir sınıf oluştur.")
            return

        yol, _ = QFileDialog.getOpenFileName(
            self, "Sınıf listesi seç", filter="CSV/Excel dosyaları (*.csv *.xlsx *.xlsm)"
        )
        if not yol:
            return

        try:
            eklenen = self.yonetici.dosyadan_ice_aktar(sinif_adi, yol)
            QMessageBox.information(self, "Tamam", f"{eklenen} yeni öğrenci eklendi.")
            self._sinif_degisti(sinif_adi)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okunamadı: {e}")

    def _ogrenci_ekle(self):
        sinif_adi = self.sinif_secici.currentText()
        ad = self.yeni_ogrenci_kutusu.text().strip()
        if sinif_adi and ad:
            self.yonetici.ogrenci_ekle(sinif_adi, ad)
            self.yeni_ogrenci_kutusu.clear()
            self._sinif_degisti(sinif_adi)

    def _ogrenci_sil(self):
        sinif_adi = self.sinif_secici.currentText()
        madde = self.ogrenci_liste_widget.currentItem()
        if sinif_adi and madde:
            ad = madde.text()[2:].strip()  # emoji önekini at
            self.yonetici.ogrenci_sil(sinif_adi, ad)
            self._sinif_degisti(sinif_adi)


def main():
    app = QApplication(sys.argv)
    pencere = OgrenciSeciciPenceresi()
    pencere.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
