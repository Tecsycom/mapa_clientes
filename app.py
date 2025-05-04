import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import os
import base64

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes por Técnico y Tramo")

# Colores para técnicos
colores = [
    'red', 'blue', 'green', 'orange', 'purple', 'darkred', 'cadetblue', 'darkgreen',
    'pink', 'lightblue', 'beige', 'gray', 'black'
]

# Diccionario para asociar imágenes a técnicos (puedes personalizar las rutas de las imágenes)
tecnico_imagenes = {
    'K1': 'https://drive.google.com/uc?export=view&id=1NpNDjygRb6gZwxPBuyDaT2_hAeThcdv5',
    'K2': 'https://drive.google.com/uc?export=view&id=1AS1snf4F4yCONF9BN2vmTmjGC5vaRk53',
    'K3': 'https://drive.google.com/uc?export=view&id=1Ghw1iA0TfYX5naSz1b2mkPlfuNJjTUM9',
    # Agrega más técnicos e imágenes según necesites
}

archivo = st.file_uploader("📂 Sube tu archivo Excel con coordenadas", type=[".xlsx", ".xls"])

if archivo:
    try:
        df = pd.read_excel(archivo)

        # Validación de columnas
        columnas_requeridas = ['latitud_Y', 'longitud_X', 'Tramo', 'Tecnico', 'Location']
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"❌ El archivo debe contener las columnas: {', '.join(columnas_requeridas)}")
        else:
            # Asignar latitud y longitud
            df['Latitud'] = df['latitud_Y'].astype(float)
            df['Longitud'] = df['longitud_X'].astype(float)

            # Extraer código de técnico, si existe
            df['CodigoTecnico'] = df['Tecnico'].fillna('SIN_TECNICO').str.extract(r'(K\d+)')
            df['CodigoTecnico'].fillna('SIN_TECNICO', inplace=True)
            
            # Asignar tramo si está vacío
            df['Tramo'] = df['Tramo'].fillna('Sin Tramo')

            # Colores únicos por técnico
            tecnicos = df['CodigoTecnico'].unique()
            color_map = {tec: colores[i % len(colores)] for i, tec in enumerate(tecnicos)}

            # Selección de tipo de agrupación
            agrupacion = st.radio(
                "📊 Selecciona el tipo de agrupación:",
                ["Por Tramo", "Por Técnico"],
                horizontal=True
            )

            # Crear mapa
            lat_mean = df['Latitud'].mean()
            lon_mean = df['Longitud'].mean()
            mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)
            Fullscreen().add_to(mapa)

            if agrupacion == "Por Tramo":
                # Crear grupos por tramo
                tramos_unicos = df['Tramo'].unique()
                grupos = {tramo: folium.FeatureGroup(name=f"🕒 {tramo}") for tramo in tramos_unicos}
                grupo_key = 'Tramo'
            else:
                # Crear grupos por técnico
                grupos = {tec: folium.FeatureGroup(name=f"👷 {tec}") for tec in tecnicos}
                grupo_key = 'CodigoTecnico'

            for _, row in df.iterrows():
                key = row[grupo_key]
                grupo = grupos[key]
                
                # Obtener imagen del técnico si existe
                imagen_url = tecnico_imagenes.get(row['CodigoTecnico'], '')
                imagen_html = f'<img src="{imagen_url}" width="100" height="100" style="border-radius: 10px;"><br>' if imagen_url else ''

                popup_text = f"""
                {imagen_html}
                <b>Código:</b> {row.get('Codigo', '')}<br>
                <b>Cliente:</b> {row.get('Cliente', '')}<br>
                <b>Dirección:</b> {row.get('Direccion', '')}<br>
                <b>Distrito:</b> {row.get('Distrito', '')}<br>
                <b>Negocio:</b> {row.get('Negocio', '')}<br>
                <b>Estado:</b> {row.get('Estado', '')}<br>
                <b>Observaciones:</b> {row.get('Observaciones', '')}<br>
                <b>Tramo:</b> {row.get('Tramo', '')}<br>
                <b>Técnico:</b> {row.get('Tecnico', '')}<br>
                <b>Ubicación:</b> {row.get('Location', '')}
                """

                color = color_map.get(row['CodigoTecnico'], 'gray')

                folium.Marker(
                    location=[row['Latitud'], row['Longitud']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color)
                ).add_to(grupo)

                folium.Marker(
                    location=[row['Latitud'], row['Longitud']],
                    icon=folium.DivIcon(
                        html=f"""<div style='font-size: 10pt; color:{color};
                                background-color:white; padding:2px; border-radius:3px;'>
                                <b>{row['CodigoTecnico']}</b></div>"""
                    )
                ).add_to(grupo)

            # Agregar todos los grupos al mapa
            for capa in grupos.values():
                mapa.add_child(capa)

            folium.LayerControl(collapsed=False).add_to(mapa)

            st_folium(mapa, width=1500, height=800)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
