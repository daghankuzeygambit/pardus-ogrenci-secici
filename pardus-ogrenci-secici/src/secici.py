# Pardus Öğrenci Seçici - Rastgele Seçim Motoru
#
# Neden `secrets` modülü? Python'un standart `random` modülü Mersenne
# Twister algoritmasını kullanır - bu istatistiksel olarak iyi dağılır
# ama kriptografik olarak GÜVENLİ DEĞİLDİR (dizi çıktısından iç durumu
# tahmin etmek teorik olarak mümkündür). `secrets` modülü işletim
# sisteminin kendi rastgelelik kaynağını (os.urandom) kullanır - "öğretmen
# hile yapıyor" itirazlarına karşı "gerçekten adil/öngörülemez" bir seçim
# yapıldığını iddia edebilmek için doğru araç budur.

import secrets
import random  # sadece SystemRandom (os.urandom tabanlı, kriptografik güvenli) için


class SeciciMotoru:
    def __init__(self, ogrenci_listesi):
        self.tum_ogrenciler = list(ogrenci_listesi)
        self._henuz_secilmeyenler = list(self.tum_ogrenciler)

    def tekli_sec(self):
        """Kriptografik güvenli rastgele bir öğrenci seçer.
        'Havuz' tükenene kadar aynı öğrenci tekrar seçilmez (adil dağılım
        için); havuz tükenirse otomatik olarak sıfırlanır."""
        if not self.tum_ogrenciler:
            return None

        if not self._henuz_secilmeyenler:
            self._henuz_secilmeyenler = list(self.tum_ogrenciler)

        secilen = secrets.choice(self._henuz_secilmeyenler)
        self._henuz_secilmeyenler.remove(secilen)
        return secilen

    def havuzu_sifirla(self):
        self._henuz_secilmeyenler = list(self.tum_ogrenciler)

    def kalan_havuz_boyutu(self):
        return len(self._henuz_secilmeyenler)

    def gruplara_ayir(self, grup_sayisi=None, grup_basina_kisi=None):
        """Öğrencileri rastgele gruplara ayırır. grup_sayisi ya da
        grup_basina_kisi'den biri verilmelidir."""
        if not self.tum_ogrenciler:
            return []

        karisik = list(self.tum_ogrenciler)
        random.SystemRandom().shuffle(karisik)  # os.urandom tabanlı, güvenli karıştırma

        if grup_sayisi:
            n = max(1, int(grup_sayisi))
            gruplar = [[] for _ in range(n)]
            for i, ogrenci in enumerate(karisik):
                gruplar[i % n].append(ogrenci)
        elif grup_basina_kisi:
            k = max(1, int(grup_basina_kisi))
            gruplar = [karisik[i:i + k] for i in range(0, len(karisik), k)]
        else:
            raise ValueError("grup_sayisi ya da grup_basina_kisi belirtilmeli")

        return [g for g in gruplar if g]  # boş grupları at
