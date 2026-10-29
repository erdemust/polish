
from __future__ import annotations

import re
import time
import zipfile
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
import streamlit as st


# ============================================================
# AYARLAR
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
FOTO_DIR = BASE_DIR / "fotolar"
ZIP_PATH = FOTO_DIR / "pasalar_fotograflari.zip"

FOTO_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "https://commons.wikimedia.org/w/api.php"

HEADERS = {
    "User-Agent": (
        "PasalarPhotoArchive/1.0 "
        "(educational image downloader; Python requests)"
    )
}

# Orijinal bağlantılar ve alternatif arama terimleri.
FOTOLAR = [
    {
        "id": "sadik",
        "isim": "Michał Czajkowski / Mehmed Sadık Paşa",
        "dosya": "Michal_Czajkowski_Mehmed_Sadik_Pasa",
        "url": (
            "https://upload.wikimedia.org/wikipedia/commons/1/1a/"
            "Micha%C5%82_Czajkowski_by_Kieszkowski.jpg"
        ),
        "arama": [
            "Michał Czajkowski Sadyk Pasha",
            "Michał Czajkowski portrait",
        ],
    },
    {
        "id": "bem",
        "isim": "Józef Bem / Murad Paşa",
        "dosya": "Jozef_Bem_Murad_Pasa",
        "url": (
            "https://upload.wikimedia.org/wikipedia/commons/c/c9/"
            "J%C3%B3zef_Bem_by_Klimowicz.jpg"
        ),
        "arama": [
            "Józef Bem portrait",
            "Józef Bem by Klimowicz",
        ],
    },
    {
        "id": "ilinski",
        "isim": "Antoni Iliński / Mehmed İskender Paşa",
        "dosya": "Antoni_Ilinski_Mehmed_Iskender_Pasa",
        "url": (
            "https://upload.wikimedia.org/wikipedia/commons/5/5a/"
            "Antoni_Ili%C5%84ski.jpg"
        ),
        "arama": [
            "Antoni Iliński",
            "Antoni Ilinski portrait",
        ],
    },
    {
        "id": "borzecki",
        "isim": "Konstanty Borzęcki / Mustafa Celaleddin Paşa",
        "dosya": "Konstanty_Borzecki_Mustafa_Celaleddin_Pasa",
        "url": (
            "https://upload.wikimedia.org/wikipedia/commons/3/36/"
            "Mustafa_Celaleddin_Pasha.jpg"
        ),
        "arama": [
            "Mustafa Celaleddin Pasha",
            "Konstanty Borzecki",
        ],
    },
    {
        "id": "muzaffer",
        "isim": "Władysław Czajkowski / Muzaffer Paşa",
        "dosya": "Wladyslaw_Czajkowski_Muzaffer_Pasa",
        "url": (
            "https://upload.wikimedia.org/wikipedia/commons/2/22/"
            "W%C5%82adys%C5%82aw_Czajkowski_%28Muzaffar_Pasha%29.jpg"
        ),
        "arama": [
            "Władysław Czajkowski Muzaffar Pasha",
            "Wladyslaw Czajkowski Muzaffer Pasha",
        ],
    },
]


# ============================================================
# HTTP VE GÖRSEL DOĞRULAMA
# ============================================================

def yeni_oturum():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def istek_yap(session, url, params=None, stream=False):
    """Geçici HTTP hatalarında yeniden dener."""
    son_hata = None

    for deneme in range(4):
        try:
            response = session.get(
                url,
                params=params,
                timeout=(10, 45),
                stream=stream,
            )

            if response.status_code == 429 or response.status_code in (
                500, 502, 503, 504
            ):
                bekleme = min(5 * (2 ** deneme), 40)
                response.close()
                time.sleep(bekleme)
                continue

            response.raise_for_status()
            return response

        except requests.RequestException as exc:
            son_hata = exc
            if deneme < 3:
                time.sleep(min(2 ** deneme, 8))

    raise RuntimeError(f"HTTP isteği başarısız: {son_hata}")


def gorsel_turu(data):
    """Dosyanın gerçek imzasına göre uzantısını belirler."""
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"

    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"

    if (
        len(data) >= 12
        and data[:4] == b"RIFF"
        and data[8:12] == b"WEBP"
    ):
        return ".webp"

    if len(data) >= 12 and data[4:8] == b"ftyp":
        if data[8:12] in (b"avif", b"avis"):
            return ".avif"

    raise ValueError("Sunucudan geçerli bir görsel dosyası gelmedi.")


def indir_gorsel(session, url):
    response = istek_yap(session, url, stream=True)

    try:
        content_type = response.headers.get("Content-Type", "").lower()

        if "text/html" in content_type or "application/json" in content_type:
            raise ValueError(
                f"Görsel yerine başka içerik geldi: {content_type}"
            )

        chunks = []
        boyut = 0
        maksimum = 40 * 1024 * 1024

        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue

            boyut += len(chunk)

            if boyut > maksimum:
                raise ValueError("Görsel 40 MB sınırını aşıyor.")

            chunks.append(chunk)

        data = b"".join(chunks)
        uzanti = gorsel_turu(data)

        return data, uzanti

    finally:
        response.close()


# ============================================================
# WIKIMEDIA COMMONS API
# ============================================================

def commons_dosya_ara(session, arama):
    """
    Commons dosya alanında arama yapar.
    Bulunan dosyanın gerçek orijinal URL'sini döndürür.
    """
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srnamespace": 6,
        "srlimit": 10,
        "srsearch": arama,
    }

    response = istek_yap(session, API_URL, params=params)

    try:
        payload = response.json()
    finally:
        response.close()

    sonuclar = payload.get("query", {}).get("search", [])

    for sonuc in sonuclar:
        baslik = sonuc.get("title", "")

        # Beklenmeyen dosya türlerini ele.
        if not baslik.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
        ):
            continue

        params = {
            "action": "query",
            "format": "json",
            "titles": baslik,
            "prop": "imageinfo",
            "iiprop": "url",
        }

        response = istek_yap(session, API_URL, params=params)

        try:
            payload = response.json()
        finally:
            response.close()

        pages = payload.get("query", {}).get("pages", {})

        for page in pages.values():
            imageinfo = page.get("imageinfo", [])

            if imageinfo:
                return {
                    "title": page.get("title", baslik),
                    "url": imageinfo[0].get("url"),
                }

    return None


# ============================================================
# DOSYAYI İNDİR VE KAYDET
# ============================================================

def fotograf_kaydet(session, foto):
    """
    Önce verilen URL'yi dener.
    Başarısız olursa Commons API üzerinden alternatif arar.
    """
    adaylar = [("Orijinal bağlantı", foto["url"])]

    for arama in foto["arama"]:
        adaylar.append((f"Commons araması: {arama}", arama))

    hatalar = []

    for kaynak, adres in adaylar:
        try:
            if kaynak.startswith("Commons araması:"):
                sonuc = commons_dosya_ara(session, adres)

                if not sonuc or not sonuc.get("url"):
                    hatalar.append(f"{kaynak}: dosya bulunamadı")
                    continue

                url = sonuc["url"]
                kaynak_adi = sonuc["title"]
            else:
                url = adres
                kaynak_adi = adres

            data, uzanti = indir_gorsel(session, url)

            hedef = FOTO_DIR / f"{foto['dosya']}{uzanti}"

            # Önce geçici dosyaya yaz, ardından atomik olarak taşı.
            gecici = hedef.with_suffix(hedef.suffix + ".tmp")
            gecici.write_bytes(data)
            gecici.replace(hedef)

            return {
                "isim": foto["isim"],
                "dosya": hedef,
                "url": url,
                "kaynak": kaynak_adi,
                "bayt": len(data),
            }

        except Exception as exc:
            hatalar.append(f"{kaynak}: {exc}")

        # Commons sunucusuna istekler arasında kısa ara.
        time.sleep(1.5)

    raise RuntimeError(" | ".join(hatalar))


# ============================================================
# ZIP OLUŞTUR
# ============================================================

def zip_olustur(kayitlar):
    buffer = BytesIO()

    with zipfile.ZipFile(
        buffer, "w", compression=zipfile.ZIP_DEFLATED
    ) as arsiv:
        kaynak_metni = []

        for kayit in kayitlar:
            dosya = kayit["dosya"]

            if dosya.exists() and dosya.stat().st_size > 0:
                arsiv.write(dosya, arcname=dosya.name)
                kaynak_metni.append(
                    f"{kayit['isim']}\n"
                    f"Dosya: {dosya.name}\n"
                    f"Kaynak: {kayit['url']}\n"
                    f"Commons başlığı: {kayit['kaynak']}\n"
                )

        arsiv.writestr(
            "KAYNAKLAR.txt",
            "\n".join(kaynak_metni),
        )

    data = buffer.getvalue()

    with zipfile.ZipFile(BytesIO(data), "r") as kontrol:
        bozuk = kontrol.testzip()

        if bozuk:
            raise RuntimeError(f"ZIP doğrulama hatası: {bozuk}")

    ZIP_PATH.write_bytes(data)
    return data


# ============================================================
# STREAMLIT ARAYÜZÜ
# ============================================================

st.set_page_config(
    page_title="Paşalar Fotoğraf Arşivi",
    page_icon="🖼️",
    layout="wide",
)

st.title("🖼️ Paşalar Fotoğraf Arşivi")

st.write(
    "Beş tarihî şahsiyetin fotoğraflarını Wikimedia Commons'tan "
    "indirir, yerel fotolar klasörüne kaydeder ve ZIP arşivi hazırlar."
)

st.code(str(FOTO_DIR), language=None)

if "kayitlar" not in st.session_state:
    st.session_state["kayitlar"] = []

if st.button("📥 Fotoğrafları indir / eksikleri tamamla", type="primary"):
    session = yeni_oturum()
    kayitlar = []
    hatalar = []

    ilerleme = st.progress(0)
    durum = st.empty()

    for i, foto in enumerate(FOTOLAR, start=1):
        durum.write(f"{i}/{len(FOTOLAR)} — {foto['isim']}")

        try:
            sonuc = fotograf_kaydet(session, foto)
            kayitlar.append(sonuc)
            st.success(
                f"Kaydedildi: {sonuc['dosya'].name} "
                f"({sonuc['bayt']:,} bayt)"
            )

        except Exception as exc:
            hatalar.append((foto["isim"], str(exc)))
            st.error(f"İndirilemedi: {foto['isim']} — {exc}")

        ilerleme.progress(i / len(FOTOLAR))

        # İstekleri birbirinden ayır.
        time.sleep(2)

    st.session_state["kayitlar"] = kayitlar

    if kayitlar:
        try:
            zip_data = zip_olustur(kayitlar)
            st.session_state["zip_data"] = zip_data

            st.success(
                f"{len(kayitlar)}/{len(FOTOLAR)} fotoğraf kaydedildi."
            )
            st.write(f"ZIP dosyası: `{ZIP_PATH}`")

        except Exception as exc:
            st.error(f"ZIP oluşturulamadı: {exc}")

    if hatalar:
        st.warning(
            f"{len(hatalar)} fotoğraf indirilemedi. "
            "Bağlantıları ve Commons arama sonuçlarını kontrol et."
        )

    session.close()


# Daha önce indirilen dosyaları göster.
kayitlar = st.session_state.get("kayitlar", [])

if kayitlar:
    st.subheader("Kaydedilen fotoğraflar")

    for kayit in kayitlar:
        with st.expander(kayit["isim"]):
            st.image(
                str(kayit["dosya"]),
                caption=kayit["isim"],
                use_container_width=True,
            )
            st.caption(f"Dosya: {kayit['dosya']}")
            st.caption(f"Kaynak: {kayit['url']}")

            st.download_button(
                "JPG / görsel dosyasını indir",
                data=kayit["dosya"].read_bytes(),
                file_name=kayit["dosya"].name,
                mime="application/octet-stream",
                key=f"tek_{kayit['dosya'].name}",
            )

    zip_data = st.session_state.get("zip_data")

    if zip_data:
        st.download_button(
            "📦 Beş fotoğrafı ZIP olarak indir",
            data=zip_data,
            file_name="pasalar_fotograflari.zip",
            mime="application/zip",
            type="primary",
        )
