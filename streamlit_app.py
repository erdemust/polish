from pathlib import Path
import zipfile, textwrap, json, os

base = Path("/mnt/data/polonyali_pasalar_streamlit")
(base / "tests").mkdir(parents=True, exist_ok=True)

app_code = r'''from __future__ import annotations

import csv
import html
import io
import json
from typing import Any

import folium
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen, MiniMap
from streamlit_folium import st_folium

# ============================================================
# Osmanlı Ordusundaki Polonyalı Paşalar
# Fotoğraflar, GitHub'daki mevcut dosyalardan önce yüklenir.
# ============================================================

st.set_page_config(
    page_title="Osmanlı Ordusundaki Polonyalı Paşalar",
    page_icon="🇵🇱",
    layout="wide",
)

GITHUB_RAW = "https://raw.githubusercontent.com/erdemust/polish/main"

PASALAR: dict[str, dict[str, Any]] = {
    "Michał Czajkowski / Mehmed Sadık Paşa": {
        "dates": "1804–1886",
        "portrait_caption": "Michał Czajkowski",
        "images": [
            f"{GITHUB_RAW}/Michal_Czajkowski_Mehmed_Sadik_Pasa.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Micha%C5%82_Czajkowski_by_Kieszkowski.jpg/440px-Micha%C5%82_Czajkowski_by_Kieszkowski.jpg",
        ],
        "bio": """**Michał Czajkowski (Mehmed Sadık Paşa) (1804–1886)**, Polonezköy/Adampol tarihinin önemli isimlerindendir.

Prens Adam Czartoryski'nin çevresiyle ilişkili olarak Osmanlı başkentinde faaliyet gösterdi. Adampol yerleşiminin kurulması ve gelişmesiyle anılır. 1850'de İslam'ı kabul ederek Mehmed Sadık adını aldı. Kırım Savaşı sırasında Osmanlı hizmetinde Kazak birlikleriyle bağlantılı görevler üstlendi.

**Tarih notu:** Yerleşimin kuruluşundaki kişisel rolü ve askerî görevlerin ayrıntıları için arşiv ve akademik kaynaklarla ayrıca karşılaştırma yapılmalıdır.""",
        "features": [
            ("Halczyniec / Volhinya (doğum yeri yaklaşık)", 50.0, 28.5,
             "29 Eylül 1804 doğumlu olduğu aktarılır. Koordinat, tarihsel bölgeyi yaklaşık gösterir."),
            ("İstanbul", 41.0082, 28.9784,
             "1841'de İstanbul'a geldiği ve 1850'de İslam'ı kabul ederek Mehmed Sadık adını aldığı aktarılır."),
            ("Polonezköy / Adampol", 41.11, 29.11,
             "Adampol yerleşiminin kuruluşu ve erken dönem yönetimiyle ilişkilidir."),
            ("Kırım Cephesi (bölgesel işaret)", 44.5, 32.0,
             "Kırım Savaşı sırasında Osmanlı hizmetindeki Kazak birlikleriyle ilişkilendirilir; nokta kesin muharebe konumu değildir."),
            ("Borki / Ukrayna (yaklaşık)", 50.5, 31.5,
             "1872'de bölgeye döndüğü, 1886'da öldüğü aktarılır. Konum yaklaşık işaretlenmiştir."),
        ],
        "route": [ [41.11, 29.11], [41.0082, 28.9784], [44.5, 32.0] ],
        "route_name": "Şematik yaşam rotası",
        "route_note": "Çizgi, seçilmiş tarihsel durakları görselleştiren şematik bir bağlantıdır; belgelenmiş seyahat güzergâhı değildir.",
    },
    "Józef Bem / Murad Paşa": {
        "dates": "1794–1850",
        "portrait_caption": "Józef Bem",
        "images": [
            f"{GITHUB_RAW}/Jozef_Bem_Murad_Pasa.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/J%C3%B3zef_Bem_by_Klimowicz.jpg/440px-J%C3%B3zef_Bem_by_Klimowicz.jpg",
        ],
        "bio": """**Józef Bem (1794–1850)** Polonyalı topçu subayı ve 1830–1831 Polonya Ayaklanması ile 1848–1849 Macar Devrimi'nin önde gelen askerî isimlerindendir.

1849'da Osmanlı topraklarına sığındı. Osmanlı hizmetine girdikten sonra Murad Paşa adıyla anıldı ve Halep'te görev yaptı. 10 Aralık 1850'de Halep'te öldü; naaşı 1929'da Tarnów'a nakledildi.

**Adlandırma notu:** Bu uygulamada yaygın kullanılan “Murad Paşa” adı tercih edilmiştir. Ayrıntılı unvanlar ve ölüm nedeni için biyografik kaynaklarla karşılaştırma önerilir.""",
        "features": [
            ("Tarnów, Polonya (doğum)", 50.0125, 20.9858,
             "14 Mart 1794'te Tarnów'da doğdu."),
            ("Varşova", 52.2297, 21.0122,
             "1830–1831 Kasım Ayaklanması sırasında Polonya ordusunda görev yaptı."),
            ("Macaristan / Transilvanya (bölgesel işaret)", 47.4979, 19.0402,
             "1848–1849 Macar Devrimi ve Transilvanya harekâtıyla ilişkilidir; nokta bölgesel gösterimdir."),
            ("İstanbul / Kütahya (genel durak)", 41.0082, 28.9784,
             "1849'da Osmanlı topraklarına sığındı ve Osmanlı hizmetine girdi."),
            ("Halep", 36.2021, 37.1343,
             "Halep'te görev yaptı ve 10 Aralık 1850'de burada öldü."),
        ],
        "route": [[50.0125, 20.9858], [52.2297, 21.0122], [47.4979, 19.0402], [41.0082, 28.9784], [36.2021, 37.1343]],
        "route_name": "Şematik yaşam rotası",
        "route_note": "Çizgi, seçilmiş tarihsel durakları görselleştiren şematik bir bağlantıdır; belgelenmiş seyahat güzergâhı değildir.",
    },
    "Antoni Iliński / Mehmed İskender Paşa": {
        "dates": "1812–1861",
        "portrait_caption": "Antoni Iliński",
        "images": [
            f"{GITHUB_RAW}/Antoni_Ilinski_Mehmed_Iskender_Pasa.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Antoni_Ili%C5%84ski.jpg/440px-Antoni_Ili%C5%84ski.jpg",
        ],
        "bio": """**Antoni Iliński (Mehmed İskender Paşa) (1812–1861)**, Polonya bağımsızlık hareketi ve 1848–1849 Avrupa devrimleriyle bağlantılı askerî-siyasi bir figürdür.

1844'te Osmanlı hizmetine girdiği aktarılır. Kırım Savaşı sırasında görev yaptı; daha sonra Bağdat'ta valilik yaptığı bilgisi biyografilerde yer alır. 2 Temmuz 1861'de İstanbul'da öldü ve Edirnekapı Şehitliği'ne defnedildiği belirtilir.

**Tarih notu:** “Ebû'n-nar” lakabı, rütbe ve görev tarihlerinin ayrıntıları bağımsız kaynaklarla doğrulanmalıdır.""",
        "features": [
            ("Yarmolyntsi / Podolya (yaklaşık)", 49.1, 27.1,
             "1812 doğumlu olduğu aktarılır; işaret tarihsel bölgeyi yaklaşık gösterir."),
            ("İstanbul", 41.0082, 28.9784,
             "1844'te Osmanlı hizmetine girmesiyle ilişkilendirilen merkez."),
            ("Kırım (bölgesel işaret)", 44.5, 33.5,
             "Kırım Savaşı'ndaki askerî faaliyetleriyle ilişkilidir; nokta kesin muharebe alanı değildir."),
            ("Bağdat", 33.3152, 44.3661,
             "Bağdat'taki idari göreviyle ilişkilendirilir."),
            ("Edirnekapı Şehitliği, İstanbul (yaklaşık)", 41.03, 28.94,
             "2 Temmuz 1861'de İstanbul'da öldüğü ve burada defnedildiği aktarılır; nokta yaklaşık konumdur."),
        ],
        "route": [[49.1, 27.1], [41.0082, 28.9784], [44.5, 33.5], [33.3152, 44.3661], [41.03, 28.94]],
        "route_name": "Şematik yaşam rotası",
        "route_note": "Çizgi, seçilmiş tarihsel durakları görselleştiren şematik bir bağlantıdır; belgelenmiş seyahat güzergâhı değildir.",
    },
    "Konstanty Borzęcki / Mustafa Celaleddin Paşa": {
        "dates": "1826–1876",
        "portrait_caption": "Konstanty Borzęcki",
        "images": [
            f"{GITHUB_RAW}/Konstanty_Borzecki_Mustafa_Celaleddin_Pasa.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Mustafa_Celaleddin_Pasha.jpg/440px-Mustafa_Celaleddin_Pasha.jpg",
        ],
        "bio": """**Konstanty Borzęcki (Mustafa Celaleddin Paşa) (1826–1876)**, Osmanlı subayı ve *Les Turcs anciens et modernes* (1869) kitabının yazarıdır. Eser, 19. yüzyıldaki Türk kimliği ve tarih düşüncesi tartışmaları açısından önem taşır.

1848 Poznan Ayaklanması sonrasında Avrupa'dan Osmanlı topraklarına geldiği, Osmanlı ordusunda görev yaptığı ve 1876'da Karadağ harekâtı sırasında öldüğü aktarılır. Nâzım Hikmet'in ailesiyle akrabalık bağı da biyografilerinde anılır.

**Tarih notu:** Kitabın Türkçülük tarihindeki yeri, Atatürk'ün kütüphanesindeki nüsha iddiası ve ölümünün ayrıntıları akademik kaynaklarla ayrıca doğrulanmalıdır.""",
        "features": [
            ("Modrzewiec, Polonya (yaklaşık)", 51.4, 19.69,
             "10 Nisan 1826 doğumlu olduğu aktarılır; koordinat yaklaşık gösterimdir."),
            ("İstanbul", 41.0082, 28.9784,
             "1849'da İstanbul'a geldiği ve Osmanlı ordusunda görev yaptığı aktarılır."),
            ("Karadağ / Novosela (bölgesel işaret)", 42.44, 19.26,
             "1876 Karadağ harekâtı sırasında öldüğü aktarılır; işaret kesin savaş alanı değildir."),
        ],
        "route": [[51.4, 19.69], [41.0082, 28.9784], [42.44, 19.26]],
        "route_name": "Şematik yaşam rotası",
        "route_note": "Çizgi, seçilmiş tarihsel durakları görselleştiren şematik bir bağlantıdır; belgelenmiş seyahat güzergâhı değildir.",
    },
    "Władysław Czajkowski / Muzaffer Paşa": {
        "dates": "1837/1840–1907",
        "portrait_caption": "Władysław Czajkowski",
        "images": [
            f"{GITHUB_RAW}/Wladyslaw_Czajkowski_Muzaffer_Pasa.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/W%C5%82adys%C5%82aw_Czajkowski_%28Muzaffar_Pasha%29.jpg/440px-W%C5%82adys%C5%82aw_Czajkowski_%28Muzaffar_Pasha%29.jpg",
        ],
        "bio": """**Władysław Czajkowski (Muzaffer Paşa) (1837/1840–1907)**, Mehmed Sadık Paşa'nın oğludur ve Fransız askerî eğitim kurumlarından Saint-Cyr ile ilişkilendirilir.

Osmanlı hizmetinde bulundu; 1902'de Cebel-i Lübnan Mutasarrıflığına atandı ve 1907'de öldü. Lübnan yönetimi, dönemin uluslararası düzenlemeleri ve Osmanlı idaresi bağlamında değerlendirilmelidir.

**Tarih notu:** Doğum yılı kaynaklarda farklı verilebildiğinden burada iki olası yıl aralığı korunmuştur. Plevne'deki görevi ve atama koşulları için kaynak karşılaştırması önerilir.""",
        "features": [
            ("Paris / Saint-Cyr (eğitim durağı)", 48.8566, 2.3522,
             "Saint-Cyr askerî eğitim kurumuyla ilişkilendirilir; doğum yeri olarak sunulmamaktadır."),
            ("İstanbul", 41.0082, 28.9784,
             "Osmanlı sarayı ve askerî hizmetiyle ilişkili merkez."),
            ("Cebel-i Lübnan / Beyrut çevresi (yaklaşık)", 33.89, 35.5,
             "1902–1907 döneminde Cebel-i Lübnan Mutasarrıflığıyla ilişkilidir; işaret yaklaşık bölgesel konumdur."),
        ],
        "route": [[48.8566, 2.3522], [41.0082, 28.9784], [33.89, 35.5]],
        "route_name": "Şematik yaşam rotası",
        "route_note": "Çizgi, seçilmiş tarihsel durakları görselleştiren şematik bir bağlantıdır; belgelenmiş seyahat güzergâhı değildir.",
    },
}

PALETA = ["#1677ff", "#4666d5", "#8055c7", "#c04a9a", "#dc3030"]


def validate_person(person: dict[str, Any]) -> None:
    """Kişi verisinde gerekli alanları ve koordinatları kontrol et."""
    required = {"dates", "images", "bio", "features", "route", "route_name", "route_note"}
    missing = required.difference(person)
    if missing:
        raise ValueError(f"Eksik kişi alanları: {', '.join(sorted(missing))}")
    if not person["features"]:
        raise ValueError("En az bir harita durağı bulunmalıdır.")
    for feature in person["features"]:
        if len(feature) != 4:
            raise ValueError("Her durak (ad, enlem, boylam, açıklama) biçiminde olmalıdır.")
        name, lat, lon, description = feature
        if not isinstance(name, str) or not isinstance(description, str):
            raise ValueError("Durak adı ve açıklaması metin olmalıdır.")
        if not (-90 <= float(lat) <= 90 and -180 <= float(lon) <= 180):
            raise ValueError(f"Geçersiz koordinat: {name}")


def make_geojson(person: dict[str, Any], person_name: str) -> dict[str, Any]:
    """Kişinin duraklarını ve şematik rotasını GeoJSON'a çevir."""
    validate_person(person)
    features = []
    for index, (name, lat, lon, description) in enumerate(person["features"], start=1):
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
            "properties": {
                "name": name,
                "description": description,
                "order": index,
                "person": person_name,
                "location_precision": "approximate_or_historical_region",
            },
        })
    route = person["route"]
    if len(route) >= 2:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[float(lon), float(lat)] for lat, lon in route],
            },
            "properties": {
                "name": person["route_name"],
                "description": person["route_note"],
                "person": person_name,
                "route_type": "schematic_not_verified_itinerary",
            },
        })
    return {"type": "FeatureCollection", "name": person_name, "features": features}


def make_map(person: dict[str, Any], person_name: str, show_route: bool = True) -> folium.Map:
    """Duraklar, popup'lar, rota ve katman kontrolleriyle Folium haritası oluştur."""
    validate_person(person)
    locations = [(float(lat), float(lon)) for _, lat, lon, _ in person["features"]]
    center = [
        sum(lat for lat, _ in locations) / len(locations),
        sum(lon for _, lon in locations) / len(locations),
    ]
    fmap = folium.Map(location=center, zoom_start=4, control_scale=True, tiles="OpenStreetMap")
    folium.TileLayer("CartoDB positron", name="Açık renkli harita").add_to(fmap)
    Fullscreen(position="topright", title="Tam ekran", title_cancel="Tam ekrandan çık").add_to(fmap)
    MiniMap(toggle_display=True, position="bottomright").add_to(fmap)

    points_layer = folium.FeatureGroup(name="Yaşam durakları", show=True)
    count = len(person["features"])
    for index, (name, lat, lon, description) in enumerate(person["features"], start=1):
        color = PALETA[min(index - 1, len(PALETA) - 1)]
        popup_html = f"""
        <div style="width:260px; font-family:Arial,sans-serif;">
          <h4 style="margin:0 0 8px 0;">{index}. {html.escape(name)}</h4>
          <p style="margin:0 0 8px 0;">{html.escape(description)}</p>
          <small>Koordinat: {float(lat):.4f}, {float(lon):.4f}</small>
          <hr style="margin:8px 0;">
          <small><b>{html.escape(person_name)}</b></small>
        </div>
        """
        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=8,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=f"{index}. {name}",
            popup=folium.Popup(popup_html, max_width=320),
        ).add_to(points_layer)
    points_layer.add_to(fmap)

    if show_route and len(person["route"]) >= 2:
        route_layer = folium.FeatureGroup(name="Şematik yaşam rotası", show=True)
        folium.PolyLine(
            locations=person["route"],
            color="#244c9a",
            weight=4,
            opacity=0.8,
            tooltip=person["route_name"],
            popup=folium.Popup(html.escape(person["route_note"]), max_width=360),
        ).add_to(route_layer)
        route_layer.add_to(fmap)

    folium.LayerControl(collapsed=False).add_to(fmap)
    if len(locations) > 1:
        fmap.fit_bounds(locations, padding=(24, 24))
    return fmap


def build_csv(person: dict[str, Any], person_name: str) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["paşa", "sıra", "durak", "enlem", "boylam", "açıklama", "konum kesinliği"])
    for index, (name, lat, lon, description) in enumerate(person["features"], start=1):
        writer.writerow([person_name, index, name, lat, lon, description, "yaklaşık/bölgesel olabilir"])
    return output.getvalue().encode("utf-8-sig")


def show_portrait(person: dict[str, Any], caption: str) -> None:
    """GitHub fotoğrafını önce, Wikimedia yedeğini sonra dene."""
    for image_url in person["images"]:
        try:
            st.image(image_url, caption=caption, use_container_width=True)
            st.caption("Görsel kaynağı: GitHub/Wikimedia bağlantısı")
            return
        except Exception:
            continue
    st.warning("Portre yüklenemedi. İnternet bağlantısını veya görsel bağlantılarını kontrol edin.")


# --------------------------- UI ---------------------------
st.title("🇵🇱🇹🇷 Osmanlı Ordusundaki Polonyalı Paşalar")
st.caption(
    "Osmanlı hizmetinde bulunan beş Polonya kökenli tarihsel figürün biyografileri ve "
    "seçilmiş yaşam durakları. Konumlar ve rotalar, kaynaklarla doğrulanmadıkça yaklaşık/şematik kabul edilmelidir."
)

with st.sidebar:
    st.header("Paşalar")
    secim = st.radio("Bir paşa seçin:", list(PASALAR.keys()))
    st.divider()
    st.subheader("Harita seçenekleri")
    rota_goster = st.checkbox("Şematik rotayı göster", value=True)
    durak_tablosu = st.checkbox("Durak tablosunu göster", value=True)
    st.caption("Haritadaki katmanlar sağ üstteki katman kontrolünden açılıp kapatılabilir.")

person = PASALAR[secim]
try:
    validate_person(person)
except (ValueError, TypeError) as exc:
    st.error(f"Veri doğrulama hatası: {exc}")
    st.stop()

st.header(secim)
st.caption(f"Tarih aralığı: {person['dates']}")
col_bio, col_img = st.columns([2, 1], gap="large")
with col_bio:
    st.markdown(person["bio"])
with col_img:
    show_portrait(person, person["portrait_caption"])

st.divider()
st.subheader("🗺️ Yaşam yolu haritası")
st.info("Haritadaki çizgiler seçilmiş duraklar arasındaki şematik bağlantılardır; doğrulanmış tarihsel seyahat rotası olarak yorumlanmamalıdır.")
try:
    fmap = make_map(person, secim, show_route=rota_goster)
    st_folium(
        fmap,
        use_container_width=True,
        height=610,
        key=f"map_{list(PASALAR).index(secim)}_{int(rota_goster)}",
        returned_objects=[],
    )
except Exception as exc:
    st.error("Harita oluşturulamadı. Lütfen paket kurulumunu ve uygulama günlüklerini kontrol edin.")
    with st.expander("Teknik hata ayrıntısı"):
        st.code(str(exc))

rows = [
    {"Sıra": i, "Durak": name, "Enlem": lat, "Boylam": lon, "Açıklama": desc}
    for i, (name, lat, lon, desc) in enumerate(person["features"], start=1)
]
df = pd.DataFrame(rows)

st.subheader("📍 Haritadaki duraklar")
if durak_tablosu:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    for row in rows:
        st.markdown(f"**{row['Sıra']}. {row['Durak']}** — {row['Açıklama']}")

st.subheader("📦 İndirmeler")
geojson = make_geojson(person, secim)
slug = (
    secim.split("/")[0].strip()
    .replace(" ", "_")
    .replace("ł", "l").replace("Ł", "L")
    .replace("ó", "o").replace("Ó", "O")
    .replace("ą", "a").replace("ę", "e")
    .replace("ś", "s").replace("Ś", "S")
    .replace("ć", "c").replace("ź", "z").replace("ż", "z")
)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.download_button(
        "📥 GeoJSON indir",
        data=json.dumps(geojson, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"{slug}_rota.geojson",
        mime="application/geo+json",
        use_container_width=True,
    )
with c2:
    st.download_button(
        "📊 CSV indir",
        data=build_csv(person, secim),
        file_name=f"{slug}_duraklar.csv",
        mime="text/csv",
        use_container_width=True,
    )
with c3:
    st.download_button(
        "📄 Biyografi TXT",
        data=(f"{secim}\nTarih aralığı: {person['dates']}\n\n" + person["bio"].replace("**", "").replace("*", "")).encode("utf-8"),
        file_name=f"{slug}_biyografi.txt",
        mime="text/plain",
        use_container_width=True,
    )
with c4:
    try:
        map_html = make_map(person, secim, show_route=rota_goster).get_root().render().encode("utf-8")
        st.download_button(
            "🌐 Etkileşimli HTML harita",
            data=map_html,
            file_name=f"{slug}_harita.html",
            mime="text/html",
            use_container_width=True,
        )
    except Exception as exc:
        st.warning(f"HTML harita hazırlanamadı: {exc}")

with st.expander("Kaynakça ve tarihsel doğrulama notları"):
    st.markdown("""
    **Başlangıç kaynakları (iddialar için tek başına nihai kanıt sayılmamalıdır):**
    - Türkçe ve Lehçe Wikipedia biyografi maddeleri.
    - Jerzy Łątka, *Adampol-Polska wieś nad Bosforem* (1981).
    - Jerzy Łątka, *Lew Nasz, Lew Polski* (1996).
    - Jerzy Łątka, *Pasza z Lechistanu* (1993).
    - Polonezköy yerel tarih yayınları ve Beykoz Belediyesi arşiv materyalleri.

    **Kaynak kullanımı:** Bu sürümdeki biyografiler, sağlanan başlangıç metninin temkinli bir editoryal düzenlemesidir; her tarihsel iddia bağımsız birincil/akademik kaynak üzerinden doğrulanmış değildir. Koordinatlar yaklaşık olabilir. Harita rotaları gerçek seyahat çizgisi iddiası taşımaz.
    """)

st.divider()
st.caption("Streamlit + Folium. Harita döşemelerinin görünmesi için internet bağlantısı gerekir.")
'''

requirements = """streamlit>=1.36
folium>=0.16
streamlit-folium>=0.20
pandas>=2.0
pytest>=8.0
"""

readme = r'''# Osmanlı Ordusundaki Polonyalı Paşalar — Streamlit

## Özellikler
- Beş paşa için biyografi ve portre
- GitHub ham dosya bağlantıları önce, Wikimedia görseli yedek olarak
- Folium haritası, açılır pencereler, katman kontrolü ve şematik rotalar
- GeoJSON, CSV, TXT ve etkileşimli HTML indirme
- Koordinat ve veri yapısı kontrolleri

## Kurulum

Python 3.10 veya üstü önerilir.

```bash
python -m venv .venv
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## GitHub Codespaces
Proje dosyalarını depoya ekledikten sonra terminalde:

```bash
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```

Codespaces port yönlendirme ekranında Streamlit'in kullandığı 8501 portunu açın.

## Test

```bash
pytest -q
```

## Fotoğraflar
Fotoğraflar, mevcut depodaki şu GitHub ham bağlantılarından yüklenir:
- `Michal_Czajkowski_Mehmed_Sadik_Pasa.png`
- `Jozef_Bem_Murad_Pasa.jpg`
- `Antoni_Ilinski_Mehmed_Iskender_Pasa.jpg`
- `Konstanty_Borzecki_Mustafa_Celaleddin_Pasa.jpg`
- `Wladyslaw_Czajkowski_Muzaffer_Pasa.png`

Fotoğraf dosyalarını yeniden yüklemeniz gerekmez. Uygulama GitHub bağlantısını önce dener; başarısız olursa Wikimedia bağlantısına geçer.

## Tarihsel hassasiyet
Haritadaki bazı koordinatlar tarihsel bölgeleri yaklaşık temsil eder. Çizgiler şematik görselleştirmelerdir; gerçek seyahat güzergâhları olarak kabul edilmemelidir. Biyografilerdeki özel iddiaları akademik/ birincil kaynaklarla ayrıca doğrulayın.
'''

test_code = r'''from app import PASALAR, make_geojson, validate_person


def test_five_people_exist():
    assert len(PASALAR) == 5


def test_each_person_has_valid_coordinates_and_required_data():
    for person in PASALAR.values():
        validate_person(person)


def test_geojson_has_points_and_route():
    for name, person in PASALAR.items():
        geojson = make_geojson(person, name)
        assert geojson["type"] == "FeatureCollection"
        assert sum(f["geometry"]["type"] == "Point" for f in geojson["features"]) == len(person["features"])
        assert any(f["geometry"]["type"] == "LineString" for f in geojson["features"])


def test_invalid_coordinates_are_rejected():
    bad = {
        "dates": "x", "images": [], "bio": "", "features": [("bad", 100, 20, "x")],
        "route": [], "route_name": "x", "route_note": "x"
    }
    try:
        validate_person(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid latitude should raise ValueError")
'''

(base / "app.py").write_text(app_code, encoding="utf-8")
(base / "requirements.txt").write_text(requirements, encoding="utf-8")
(base / "README.md").write_text(readme, encoding="utf-8")
(base / "tests" / "test_app_data.py").write_text(test_code, encoding="utf-8")

zip_path = Path("/mnt/data/osmanli_polonyali_pasalar_streamlit.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in base.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(base.parent))

print(f"Proje oluşturuldu: {zip_path}")
print("Dosyalar:")
for p in sorted(base.rglob("*")):
    if p.is_file():
        print(f"- {p.relative_to(base)} ({p.stat().st_size:,} bytes)")
