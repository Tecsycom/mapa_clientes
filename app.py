import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
from folium.features import CustomIcon

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes por Técnico y Tramo")

# --- Cargar archivo Excel ---
archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx", "xls"])

if archivo:
    try:
        df = pd.read_excel(archivo)

        # Verificar columnas necesarias
        columnas_requeridas = ['latitud_Y', 'longitud_X', 'Tramo', 'Tecnico']
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"❌ El archivo debe tener las columnas: {', '.join(columnas_requeridas)}")
            st.stop()

        # Convertir coordenadas
        df['Latitud'] = df['latitud_Y'].astype(float)
        df['Longitud'] = df['longitud_X'].astype(float)

        # Tramo vacío => "Sin Tramo"
        df['Tramo'] = df['Tramo'].fillna("Sin Tramo")
        
        # Técnico vacío => "Sin Técnico"
        df['Tecnico'] = df['Tecnico'].fillna("Sin Técnico")

        # Extraer código técnico (ej: K1, K2)
        df['CodigoTecnico'] = df['Tecnico'].str.extract(r'(K\d+)')
        df['CodigoTecnico'] = df['CodigoTecnico'].fillna("SIN")

        # --- Íconos personalizados por técnico (puedes cambiar los links aquí) ---
        iconos_tecnicos = {
            "K1": "https://drive.google.com/uc?export=view&id=1NpNDjygRb6gZwxPBuyDaT2_hAeThcdv5",
            "K2": "https://drive.google.com/uc?export=view&id=1AS1snf4F4yCONF9BN2vmTmjGC5vaRk53",
            "K3": "https://drive.google.com/uc?export=view&id=1Ghw1iA0TfYX5naSz1b2mkPlfuNJjTUM9",
            # Agrega todos los técnicos que tengas...
            "SIN": "https://cdn-icons-png.flaticon.com/512/565/565547.png"  # Ícono por defecto
        }

        # Crear el mapa centrado
        mapa = folium.Map(location=[df['Latitud'].mean(), df['Longitud'].mean()], zoom_start=13)
        Fullscreen().add_to(mapa)

        # Agrupar por Tramos
        grupos_tramos = {}
        for tramo in df['Tramo'].unique():
            grupos_tramos[tramo] = folium.FeatureGroup(name=f"🕒 {tramo}")
            mapa.add_child(grupos_tramos[tramo])

        # Agrupar por Técnicos
        grupos_tecnicos = {}
        for cod in df['CodigoTecnico'].unique():
            grupos_tecnicos[cod] = folium.FeatureGroup(name=f"🧑‍🔧 Técnico {cod}", show=False)
            mapa.add_child(grupos_tecnicos[cod])

        # Crear marcadores
        for _, row in df.iterrows():
            popup_info = f"""
            <b>Cliente:</b> {row.get('Cliente', '')}<br>
            <b>Dirección:</b> {row.get('Direccion', '')}<br>
            <b>Tramo:</b> {row.get('Tramo')}<br>
            <b>Técnico:</b> {row.get('Tecnico')}
            """

            icon_url = iconos_tecnicos.get(row['CodigoTecnico'], iconos_tecnicos["SIN"])
            icono = CustomIcon(icon_url, icon_size=(30, 30))

            marcador = folium.Marker(
                location=[row['Latitud'], row['Longitud']],
                popup=folium.Popup(popup_info, max_width=300),
                icon=icono
            )

            # Agregar marcador al grupo de tramo y técnico
            if row['Tramo'] in grupos_tramos:
                grupos_tramos[row['Tramo']].add_child(marcador)
            else:
                grupos_tramos["Sin Tramo"].add_child(marcador)

            if row['CodigoTecnico'] in grupos_tecnicos:
                grupos_tecnicos[row['CodigoTecnico']].add_child(marcador)
            else:
                grupos_tecnicos["SIN"].add_child(marcador)

        # Control de capas
        folium.LayerControl(collapsed=False).add_to(mapa)

        # Mostrar en Streamlit
        st_folium(mapa, width=1500, height=800)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
