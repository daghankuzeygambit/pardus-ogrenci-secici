# Pardus Öğrenci Seçici - Sınıf Listesi Yönetimi

import json
import csv
from pathlib import Path

import openpyxl

VERI_KLASORU = Path.home() / '.pardus-ogrenci-secici'
SINIFLAR_DOSYASI = VERI_KLASORU / 'siniflar.json'


class SinifListesiYoneticisi:
    def __init__(self):
        VERI_KLASORU.mkdir(exist_ok=True)
        self.siniflar = self._yukle()  # {sinif_adi: [ogrenci1, ogrenci2, ...]}

    def _yukle(self):
        if SINIFLAR_DOSYASI.exists():
            try:
                with open(SINIFLAR_DOSYASI, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def kaydet(self):
        with open(SINIFLAR_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(self.siniflar, f, ensure_ascii=False, indent=2)

    def sinif_olustur(self, sinif_adi):
        if sinif_adi not in self.siniflar:
            self.siniflar[sinif_adi] = []
            self.kaydet()

    def sinif_sil(self, sinif_adi):
        if sinif_adi in self.siniflar:
            del self.siniflar[sinif_adi]
            self.kaydet()

    def ogrenci_ekle(self, sinif_adi, ad):
        ad = ad.strip()
        if not ad:
            return
        self.siniflar.setdefault(sinif_adi, [])
        if ad not in self.siniflar[sinif_adi]:
            self.siniflar[sinif_adi].append(ad)
            self.kaydet()

    def ogrenci_sil(self, sinif_adi, ad):
        if sinif_adi in self.siniflar and ad in self.siniflar[sinif_adi]:
            self.siniflar[sinif_adi].remove(ad)
            self.kaydet()

    def ogrencileri_getir(self, sinif_adi):
        return list(self.siniflar.get(sinif_adi, []))

    def sinif_adlarini_getir(self):
        return sorted(self.siniflar.keys())

    def dosyadan_ice_aktar(self, sinif_adi, dosya_yolu):
        """CSV ya da Excel dosyasından isim listesi okur, sınıfa ekler.
        Dönüş: kaç yeni öğrenci eklendiğini bildirir."""
        dosya_yolu = str(dosya_yolu)
        isimler = []

        if dosya_yolu.lower().endswith('.csv'):
            isimler = self._csv_oku(dosya_yolu)
        elif dosya_yolu.lower().endswith(('.xlsx', '.xlsm')):
            isimler = self._excel_oku(dosya_yolu)
        else:
            raise ValueError("Desteklenmeyen dosya türü. Sadece .csv veya .xlsx kabul edilir.")

        onceki_sayi = len(self.ogrencileri_getir(sinif_adi))
        for isim in isimler:
            self.ogrenci_ekle(sinif_adi, isim)
        yeni_sayi = len(self.ogrencileri_getir(sinif_adi))

        return yeni_sayi - onceki_sayi

    @staticmethod
    def _csv_oku(dosya_yolu):
        isimler = []
        with open(dosya_yolu, 'r', encoding='utf-8-sig', newline='') as f:
            okuyucu = csv.reader(f)
            for satir in okuyucu:
                for hucre in satir:
                    hucre = hucre.strip()
                    if hucre:
                        isimler.append(hucre)
        return isimler

    @staticmethod
    def _excel_oku(dosya_yolu):
        isimler = []
        wb = openpyxl.load_workbook(dosya_yolu, read_only=True, data_only=True)
        sayfa = wb.active
        for satir in sayfa.iter_rows(values_only=True):
            for hucre in satir:
                if hucre is not None and str(hucre).strip():
                    isimler.append(str(hucre).strip())
        wb.close()
        return isimler
