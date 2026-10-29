import streamlit as st
import json
import pandas as pd
import pydeck as pdk

# ---------------------------------------------------------
# 1. Sayfa Yapılandırması
# ---------------------------------------------------------
st.set_page_config(page_title="Osmanlı Ordusundaki Polonyalı Paşalar", layout="wide", page_icon="🇵🇱")
st.title("🇵🇱🇹🇷 Osmanlı Ordusundaki Polonyalı Paşalar")
st.caption("1795'te Polonya haritadan silindikten sonra Osmanlı'ya sığınan ve paşa olan 5 isim | Kaynak: Polonyarehber reel + TR/PL Wikipedia")

# ---------------------------------------------------------
# 2. Navigasyon
# ---------------------------------------------------------
st.sidebar.header("Paşalar")
secim = st.sidebar.radio(
    "Bir paşa seçin:",
    [
        "Michał Czajkowski / Mehmed Sadık Paşa",
        "Józef Bem / Murad Paşa",
        "Antoni Iliński / Mehmed İskender Paşa",
        "Konstanty Borzęcki / Mustafa Celaleddin Paşa",
        "Władysław Czajkowski / Muzaffer Paşa"
    ]
)

# ---------------------------------------------------------
# 3. GeoJSON Veri Tanımları (Yaşam Yolları)
# ---------------------------------------------------------
geojson_data = {
    "Michał Czajkowski / Mehmed Sadık Paşa": {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [28.5, 50.0]},"properties": {"ad": "Halczyniec / Volhinya (Doğum)", "aciklama": "29 Eylül 1804 doğumlu, szlachta ailesi"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [28.9784, 41.0082]},"properties": {"ad": "İstanbul", "aciklama": "1841'de Prens Czartoryski'nin Şark Ajansı için geldi; Aralık 1850'de İslam'ı kabul etti, Mehmed Sadık oldu"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [29.11, 41.11]},"properties": {"ad": "Polonezköy / Adampol", "aciklama": "19 Mart 1842'de ilk kulübe kutsandı, köyün kurucularından ve 1842-1850 ilk müdürü"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [32.0, 44.5]},"properties": {"ad": "Kırım Cephesi", "aciklama": "Kırım Savaşı'nda Sultan Kazak Alayı komutanı, hilal+haç sancak"}},
            {"type": "Feature","geometry": {"type": "LineString", "coordinates": [[29.11, 41.11],[28.9784, 41.0082],[31.5, 50.5]]},"properties": {"ad": "Dönüş Yolu", "aciklama": "1872'de Çar'ın affıyla Ukrayna Borki'ye döndü, 1886'da vefat"}}
        ]
    },
    "Józef Bem / Murad Paşa": {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [20.96, 50.01]},"properties": {"ad": "Tarnów, Polonya", "aciklama": "14 Mart 1794 doğumlu"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [21.01, 52.23]},"properties": {"ad": "Varşova", "aciklama": "1830-31 Kasım Ayaklanması, Iganie ve Ostrołęka muharebeleri"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [19.04, 47.50]},"properties": {"ad": "Macaristan / Transilvanya", "aciklama": "1848-49 Macar Devrimi, Erdel Ordusu Başkomutanı"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [28.9784, 41.0082]},"properties": {"ad": "İstanbul / Kütahya", "aciklama": "1849'da Osmanlı'ya sığındı, İslam'ı kabul edip Murad Paşa oldu"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [37.17, 36.20]},"properties": {"ad": "Halep", "aciklama": "Halep Valisi, 10 Aralık 1850'de vefat, naaşı 1929'da Tarnów'a nakledildi"}},
            {"type": "Feature","geometry": {"type": "LineString", "coordinates": [[20.96, 50.01],[21.01,52.23],[19.04,47.5],[28.9784,41.0082],[37.17,36.2],[20.96,50.01]]},"properties": {"ad": "Yaşam Rotası", "aciklama": "Tarnów -> Varşova -> Budapeşte -> İstanbul -> Halep -> Tarnów"}}
        ]
    },
    "Antoni Iliński / Mehmed İskender Paşa": {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [27.1, 49.1]},"properties": {"ad": "Yarmolyntsi, Podolya", "aciklama": "1812 doğumlu, Kasım Ayaklanması'na katıldı"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [28.9784, 41.0082]},"properties": {"ad": "İstanbul", "aciklama": "1844'te Osmanlı hizmetine girdi, tutukluyken İslam'ı kabul edip Mehmed İskender oldu"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [33.5, 44.5]},"properties": {"ad": "Kırım (Karakul / Gözleve)", "aciklama": "28 Mayıs 1854 Karakul galibi, Gözleve'de mirliva / paşa rütbesi"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [44.36, 33.32]},"properties": {"ad": "Bağdat", "aciklama": "Bağdat Valiliği, Arap aşiretleri arasında 'Ebû'n-nar / Ateş Babası' lakabı"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [28.94, 41.03]},"properties": {"ad": "Edirnekapı Şehitliği", "aciklama": "2 Temmuz 1861'de İstanbul'da vefat, mezarı burada"}},
            {"type": "Feature","geometry": {"type": "LineString", "coordinates": [[27.1, 49.1], [28.9784, 41.0082], [33.5, 44.5], [44.36, 33.32], [28.94, 41.03]]},"properties": {"ad": "Yaşam Rotası", "aciklama": "Podolya -> İstanbul -> Kırım -> Bağdat -> İstanbul (Edirnekapı)"}}
        ]
    },
    "Konstanty Borzęcki / Mustafa Celaleddin Paşa": {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [19.69, 51.40]},"properties": {"ad": "Modrzewiec, Polonya", "aciklama": "10 Nisan 1826 doğumlu"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [28.9784, 41.0082]},"properties": {"ad": "İstanbul", "aciklama": "1849'da geldi, harita şubesinde yüzbaşı, Ömer Paşa'nın kızıyla evlendi"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [28.9784, 41.0082]},"properties": {"ad": "Edebi Miras", "aciklama": "1869'da Les Turcs Anciens et Modernes - Türkçülüğün ilk manifestosu, Atatürk'ün kütüphanesinde"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [19.26, 42.44]},"properties": {"ad": "Karadağ Cephesi / Novosela", "aciklama": "9 Ekim 1876'da Karadağ'da yaralandı, Novosela'da şehit oldu"}},
            {"type": "Feature","geometry": {"type": "LineString", "coordinates": [[19.69, 51.40], [28.9784, 41.0082], [19.26, 42.44]]},"properties": {"ad": "Yaşam Rotası", "aciklama": "Polonya -> İstanbul -> Karadağ Cephesi"}}
        ]
    },
    "Władysław Czajkowski / Muzaffer Paşa": {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [2.35, 48.85]},"properties": {"ad": "Paris / Saint-Cyr", "aciklama": "1837/40 doğumlu, Michał Czajkowski'nin oğlu, 1861'de Saint-Cyr mezunu"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [28.9784, 41.0082]},"properties": {"ad": "İstanbul", "aciklama": "Fuad Paşa ve Sultan Abdülaziz yaverliği, 93 Harbi Plevne savunması, müşir"}},
            {"type": "Feature","geometry": {"type": "Point", "coordinates": [35.50, 33.89]},"properties": {"ad": "Cebel-i Lübnان", "aciklama": "1902-1907 mutasarrıf, uluslararası anlaşmayla Katolik Osmanlı valisi, 1907 Beyrut'ta vefat"}},
            {"type": "Feature","geometry": {"type": "LineString", "coordinates": [[2.35, 48.85], [28.9784, 41.0082], [35.50, 33.89]]},"properties": {"ad": "Yaşam Rotası", "aciklama": "Paris -> İstanbul -> Cebel-i Lübnan (Beyrut)"}}
        ]
    }
}

biyografiler = {
    "Michał Czajkowski / Mehmed Sadık Paşa": """
    **Michał Czajkowski (Mehmed Sadık Paşa) (1804–1886)** - Polonezköy'ün kurucusu.
    Prens Adam Czartoryski'nin Paris'teki Hotel Lambert hükümetinin İstanbul temsilcisi. Beykoz'da Lazarist papazlardan orman satın alıp 19 Mart 1842'de Adampol'ü kurdu.
    1850'de Müslüman olup Sadık adını aldı. Kırım Savaşı'nda Kazak Alayları'nı kurdu, hilal ve haçlı sancağıyla savaştı.
    """,
    "Józef Bem / Murad Paşa": """
    **Józef Bem (Murad Tevfik Paşa) (1794–1850)** - Üç milletin kahramanı (Polonya, Macaristan, Türkiye).
    Topçu generali, roket birliklerinin kurucusu. 1831 ve 1848 devrimlerinde efsane. 1849'da Osmanlı'ya sığındı, Avusturya-Rusya iade talebi reddedildi.
    Murad adıyla Halep Valisi oldu, 1850'de sıtmadan vefat etti. Lahdinde Osmanlıca "Ferîk Murad Paşa" yazıyor. Naaşı 1929'da Tarnów'a taşındı.
    """,
    "Antoni Iliński / Mehmed İskender Paşa": """
    **Antoni Iliński (Mehmed İskender Paşa) (1812–1861)** - Leh Aslanı.
    Podolya asıllı, Kasım Ayaklanması sonrası sürgün, Hôtel Lambert ajanı, Bem'in Macaristan'da yaveri.
    1844'te Rus baskısıyla tutuklanınca Müslüman olup kurtuldu. Kırım'da Karakul ve Gözleve kahramanı, 1855'te paşa. Bağdat'ta aşiretlerce "Ebû'n-nar" (Ateş Babası) denildi.
    Mezarı İstanbul Edirnekapı Şehitliği'nde.
    """,
    "Konstanty Borzęcki / Mustafa Celaleddin Paşa": """
    **Konstanty Borzęcki (Mustafa Celaleddin Paşa) (1826–1876)** - İlk Türkçülerden, Nâzım Hikmet'in büyük dedesi.
    1848 Poznan Ayaklanması sonrası hapse atıldı, Fransa üzerinden 1849'da İstanbul'a geldi. Çok dilli ve harita yeteneğiyle paşa oldu.
    1869'da *Les Turcs Anciens et Modernes* kitabında Türklerin Aryen kökenli olduğunu, Latin alfabesine geçilmesi gerektiğini savundu. Atatürk'ün not aldığı nüsha Anıtkabir'de.
    1876 Karadağ Savaşı'nda şehit.
    """,
    "Władysław Czajkowski / Muzaffer Paşa": """
    **Władysław Czajkowski (Muzaffer Paşa) (1837/40–1907)** - Lübnan Valisi.
    Sadık Paşa'nın oğlu, Saint-Cyr mezunu. Sultan Abdülaziz ile Avrupa turuna katıldı, Plevne savunmasında süvari komutanı.
    1902'de uluslararası antlaşma gereği Katolik Osmanlı olarak Cebel-i Lübnan Mutasarrıfı atandı. 1907'ye kadar Beyrut'tan Lübnan'ı yönetti.
    """
}

# Paşalara ait Wikimedia portre görselleri
fotolar = {
    "Michał Czajkowski / Mehmed Sadık Paşa": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Micha%C5%82_Czajkowski_by_Kieszkowski.jpg/440px-Micha%C5%82_Czajkowski_by_Kieszkowski.jpg",
    "Józef Bem / Murad Paşa": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/J%C3%B3zef_Bem_by_Klimowicz.jpg/440px-J%C3%B3zef_Bem_by_Klimowicz.jpg",
    "Antoni Iliński / Mehmed İskender Paşa": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Antoni_Ili%C5%84ski.jpg/440px-Antoni_Ili%C5%84ski.jpg",
    "Konstanty Borzęcki / Mustafa Celaleddin Paşa": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Mustafa_Celaleddin_Pasha.jpg/440px-Mustafa_Celaleddin_Pasha.jpg",
    "Władysław Czajkowski / Muzaffer Paşa": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/W%C5%82adys%C5%82aw_Czajkowski_%28Muzaffar_Pasha%29.jpg/440px-W%C5%82adys%C5%82aw_Czajkowski_%28Muzaffar_Pasha%29.jpg"
}

# ---------------------------------------------------------
# 5. Ana İçerik
# ---------------------------------------------------------
st.header(secim)

# İki sütunlu yapı: Sol tarafta biyografi metni, sağ tarafta paşanın fotoğrafı
col_bio, col_img = st.columns([2, 1])

with col_bio:
    st.markdown(biyografiler[secim])

with col_img:
    if secim in fotolar:
        st.image(fotolar[secim], caption=secim.split('/')[0].strip(), use_container_width=True)

st.divider()

# Harita verileri ve Dinamik Nokta Renklendirmesi
secili_geojson = geojson_data[secim]
points = [f for f in secili_geojson["features"] if f["geometry"]["type"] == "Point"]
lines = [f for f in secili_geojson["features"] if f["geometry"]["type"] == "LineString"]

# Rota çizgisiyle uyumlu renk geçişleri (Mavi/Mor/Kırmızı tonları)
colors = [
    [50, 150, 250, 200],   # 1. Durak (Başlangıç)
    [80, 120, 220, 200],   # 2. Durak
    [120, 80, 200, 200],   # 3. Durak
    [180, 50, 150, 200],   # 4. Durak
    [220, 30, 30, 200]     # 5. Durak (Bitiş)
]

points_list = []
for i, f in enumerate(points):
    c = colors[i] if i < len(colors) else [220, 30, 30, 200]
    points_list.append({
        "lat": f["geometry"]["coordinates"][1],
        "lon": f["geometry"]["coordinates"][0],
        "ad": f["properties"]["ad"],
        "aciklama": f["properties"]["aciklama"],
        "renk": c
    })

df_points = pd.DataFrame(points_list)

st.subheader("🗺️ Yaşam Yolu Haritası")

# Pydeck Katmanları
layer_points = pdk.Layer(
    "ScatterplotLayer",
    df_points,
    get_position='[lon, lat]',
    get_radius=22000,
    get_fill_color='renk',  # Dinamik renk ataması
    pickable=True
)

path_data = []
for line in lines:
    path_data.append({"path": line["geometry"]["coordinates"], "name": line["properties"]["ad"]})

layer_path = pdk.Layer(
    "PathLayer",
    path_data,
    get_path="path",
    get_width=4,
    get_color=[30, 90, 200, 180],
    width_min_pixels=3
)

view_state = pdk.ViewState(
    latitude=float(df_points["lat"].mean()) if not df_points.empty else 41.0,
    longitude=float(df_points["lon"].mean()) if not df_points.empty else 28.9,
    zoom=3.5,
    pitch=10
)

tooltip = {"html": "<b>{ad}</b><br/>{aciklama}", "style": {"color": "white"}}

st.pydeck_chart(pdk.Deck(
    layers=[layer_path, layer_points] if path_data else [layer_points],
    initial_view_state=view_state,
    tooltip=tooltip
))

st.write("**Haritadaki Konumlar:**")
for _, row in df_points.iterrows():
    st.write(f"- **{row['ad']}**: {row['aciklama']}")

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button(
        label="📥 GeoJSON İndir",
        data=json.dumps(secili_geojson, ensure_ascii=False, indent=2),
        file_name=f"{secim.split('/')[0].strip().replace(' ', '_')}_rota.geojson",
        mime="application/geo+json"
    )
with col_dl2:
    st.download_button(
        label="📄 Biyografi (TXT)",
        data=biyografiler[secim],
        file_name=f"{secim.split('/')[0].strip().replace(' ', '_')}.txt",
        mime="text/plain"
    )

st.divider()
st.caption("""
**Kaynaklar:** TR Wikipedia - Michał Czajkowski, Józef Bem, Mehmed İskender Paşa, Mustafa Celâleddin Paşa, Muzaffer Paşa |
PL Wikipedia - Michał Czajkowski vel Sadyk Pasza, Józef Bem, Antoni Aleksander Iliński, Konstanty Borzęcki, Władysław Czajkowski |
Jerzy Łątka: *Adampol-Polska wieś nad Bosforem* (1981), *Lew Nasz, Lew Polski* (1996), *Pasza z Lechistanu* (1993) |
Polonezköy Muzeum & Beykoz Belediyesi Arşivi
""")
