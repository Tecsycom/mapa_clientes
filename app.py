import streamlit as st
import pandas as pd
import folium
from folium import FeatureGroup
from folium.plugins import MarkerCluster
from folium.features import CustomIcon
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes por Técnico y Tramo")

archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    columnas_requeridas = ['Codigo', 'Cliente', 'Direccion', 'Distrito', 'Negocio', 'Estado',
                           'Observaciones', 'Tramo', 'Tecnico', 'Location']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("❌ El archivo debe tener todas las columnas requeridas.")
        st.stop()

    # Procesar coordenadas
    df[['Latitud', 'Longitud']] = df['Location'].astype(str).str.strip().str.split(',', expand=True)
    df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
    df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
    df = df.dropna(subset=['Latitud', 'Longitud'])

    df['Tramo'] = df['Tramo'].fillna("SIN TRAMO")
    df['Tecnico'] = df['Tecnico'].fillna("SIN TECNICO")
    df['CodigoTecnico'] = df['Tecnico'].str.extract(r'(K\d+)')
    df['CodigoTecnico'] = df['CodigoTecnico'].fillna("SIN")

    # Emojis para tramos
    emoji_tramos = {
        "08AM-12PM": "🕗",
        "12PM-16PM": "🕛",
        "16PM-20PM": "🕓",
        "SIN TRAMO": "❓"
    }

    # Íconos personalizados para técnicos
    iconos_por_tecnico = {
        "K9": "https://drive.google.com/uc?export=view&id=1abcpovvhPpntk6kNPs5TLYquUvQq3q3j",
        "SIN": "https://drive.google.com/uc?export=view&id=ID_ICONO_DEFAULT"
        # Agrega más técnicos aquí...
    }

    mapa = folium.Map(location=[df['Latitud'].mean(), df['Longitud'].mean()], zoom_start=13)

    grupos_tramos = {}
    for tramo in df['Tramo'].unique():
        emoji = emoji_tramos.get(tramo, "📍")
        grupos_tramos[tramo] = FeatureGroup(name=f"{emoji} {tramo}")
        mapa.add_child(grupos_tramos[tramo])

    grupos_tecnicos = {}
    for codigo in df['CodigoTecnico'].unique():
        grupos_tecnicos[codigo] = FeatureGroup(name=f"🛠️ Técnico {codigo}", show=False)
        mapa.add_child(grupos_tecnicos[codigo])

    for _, row in df.iterrows():
        popup_text = f"""
        <b>Código:</b> {row['Codigo']}<br>
        <b>Cliente:</b> {row['Cliente']}<br>
        <b>Dirección:</b> {row['Direccion']}<br>
        <b>Distrito:</b> {row['Distrito']}<br>
        <b>Negocio:</b> {row['Negocio']}<br>
        <b>Estado:</b> {row['Estado2']}<br>
        <b>Observaciones:</b> {row['Observaciones']}<br>
        <b>Tramo:</b> {row['Tramo']}<br>
        <b>Técnico:</b> {row['Tecnico']}
        """

        icon_url = iconos_por_tecnico.get(row['CodigoTecnico'], iconos_por_tecnico["SIN"])
        custom_icon = CustomIcon(icon_url, icon_size=(30, 30))

        marker = folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=custom_icon
        )

        grupos_tramos.get(row['Tramo'], grupos_tramos["SIN TRAMO"]).add_child(marker)
        grupos_tecnicos.get(row['CodigoTecnico'], grupos_tecnicos["SIN"]).add_child(marker)

    folium.LayerControl(collapsed=False).add_to(mapa)
    st_data = st_folium(mapa, width=1200, height=700)
