
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from urllib.request import Request, urlopen

import streamlit as st

st.set_page_config(
    page_title="Paşalar Fotoğraf Arşivi",
    page_icon="🖼️",
    layout="centered",
)

# app.py dosyasının bulunduğu dizinin altındaki fotolar klasörü
BASE_DIR = Path(__file__).resolve().parent
FOTO_DIR = BASE_DIR / "fotolar"
FOTO_DIR.mkdir(parents=True, exist_ok=True)

ZIP_PATH = FOTO_DIR / "pasalar_fotograflari.zip"

FOTOLAR = {
    "Michal_Czajkowski_Mehmed_Sadik_Pasa.jpg": (
        "Michał Czajkowski / Mehmed Sadık Paşa",
        "https://upload.wikimedia.org/wikipedia/commons/1/1a/Micha%C5%82_Czajkowski_by_Kieszkowski.jpg",
    ),
    "Jozef_Bem_Murad_Pasa.jpg": (
        "Józef Bem / Murad Paşa",
        "https://upload.wikimedia.org/wikipedia/commons/c/c9/J%C3%B3zef_Bem_by_Klimowicz.jpg",
    ),
    "Antoni_Ilinski_Mehmed_Iskender_Pasa.jpg": (
        "Antoni Iliński / Mehmed İskender Paşa",
        "https://upload.wikimedia.org/wikipedia/commons/5/5a/Antoni_Ili%C5%84ski.jpg",
    ),
    "Konstanty_Borzecki_Mustafa_Celaleddin_Pasa.jpg": (
        "Konstanty Borzęcki / Mustafa Celaleddin Paşa",
        "https://upload.wikimedia.org/wikipedia/commons/3/36/Mustafa_Celaleddin_Pasha.jpg",
    ),
    "Wladyslaw_Czajkowski_Muzaffer_Pasa.jpg": (
        "Władysław Czajkowski / Muzaffer Paşa",
        "https://upload.wikimedia.org/wikipedia/commons/2/22/W%C5%82adys%C5%82aw_Czajkowski_%28Muzaffar_Pasha%29.jpg",
    ),
}


def fotograf_indir(url):
    request = Request(
        url,
        headers={"User-Agent": "PasalarPhotoArchive/1.0"},
    )

    with urlopen(request, timeout=30) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "")

    if not content_type.lower().startswith("image/"):
        raise ValueError(f"Görsel yanıtı alınmadı: {content_type}")

    if not data.startswith(b"\xff\xd8\xff"):
        raise ValueError("İndirilen dosya geçerli JPEG değil.")

    return data


def dosyalari_indir():
    basarili = []
    hatalar = []

    for dosya_adi, (isim, url) in FOTOLAR.items():
        hedef = FOTO_DIR / dosya_adi

        try:
            # Geçerli dosya zaten varsa tekrar indirme
            if hedef.exists() and hedef.stat().st_size > 0:
                data = hedef.read_bytes()
                if data.startswith(b"\xff\xd8\xff"):
                    basarili.append((dosya_adi, isim, url))
                    continue

            data = fotograf_indir(url)
            hedef.write_bytes(data)

            basarili.append((dosya_adi, isim, url))

        except Exception as exc:
            hatalar.append(f"{isim}: {exc}")

    return basarili, hatalar


def zip_olustur(basarili):
    # ZIP önce bellekte hazırlanır
    buffer = BytesIO()

    with ZipFile(buffer, "w", ZIP_DEFLATED) as arsiv:
        kaynaklar = []

        for dosya_adi, isim, url in basarili:
            dosya_yolu = FOTO_DIR / dosya_adi

            if dosya_yolu.exists():
                arsiv.write(dosya_yolu, arcname=dosya_adi)
                kaynaklar.append(f"{isim}\n{url}\n")

        arsiv.writestr(
            "KAYNAKLAR.txt",
            "\n".join(kaynaklar),
        )

    # ZIP dosyasını da fotolar klasörüne kaydet
    ZIP_PATH.write_bytes(buffer.getvalue())
    return ZIP_PATH.read_bytes()


st.title("🖼️ Paşalar Fotoğraf Arşivi")

st.write(
    "Fotoğrafları indir, bilgisayarda fotolar klasörüne kaydet "
    "ve ZIP arşivini hazırla."
)

if st.button("📥 Fotoğrafları indir ve kaydet", type="primary"):
    with st.spinner("Fotoğraflar indiriliyor..."):
        basarili, hatalar = dosyalari_indir()

    if basarili:
        zip_data = zip_olustur(basarili)

        st.success(
            f"{len(basarili)}/{len(FOTOLAR)} fotoğraf kaydedildi."
        )
        st.code(str(FOTO_DIR), language=None)

        st.subheader("Kaydedilen fotoğraflar")

        for dosya_adi, isim, url in basarili:
            dosya_yolu = FOTO_DIR / dosya_adi

            with st.expander(f"🖼️ {isim}"):
                st.image(
                    str(dosya_yolu),
                    caption=isim,
                    use_container_width=True,
                )
                st.caption(f"Dosya: {dosya_yolu}")

                st.download_button(
                    "⬇️ JPG indir",
                    data=dosya_yolu.read_bytes(),
                    file_name=dosya_adi,
                    mime="image/jpeg",
                    key=f"jpg_{dosya_adi}",
                )

        st.download_button(
            "📦 Tüm fotoğrafları ZIP olarak indir",
            data=zip_data,
            file_name="pasalar_fotograflari.zip",
            mime="application/zip",
            type="primary",
        )

    if hatalar:
        st.warning("Bazı fotoğraflar indirilemedi:")
        for hata in hatalar:
            st.write(f"- {hata}")

    if not basarili:
        st.error("Hiçbir fotoğraf kaydedilemedi.")
