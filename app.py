import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(layout="wide")

st.title("📍 Mapa de Clientes por Técnico y Tramo")
st.markdown("Sube un archivo Excel con las columnas necesarias para visualizar las ubicaciones de los técnicos y clientes.")

# Cargar archivo
archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Verificar columnas necesarias
    columnas_necesarias = ['latitud_Y', 'longitud_X', 'Tecnico', 'Tramo']
    if not all(col in df.columns for col in columnas_necesarias):
        st.error(f"❌ El archivo debe contener las columnas: {', '.join(columnas_necesarias)}")
    else:
        # Renombrar columnas para usar en el mapa
        df = df.rename(columns={'latitud_Y': 'Latitud', 'longitud_X': 'Longitud'})
        df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
        df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
        df = df.dropna(subset=['Latitud', 'Longitud'])

        # Extraer código de técnico (ej. "K16")
        df['CodigoTecnico'] = df['Tecnico'].str.extract(r'(K\d+)')

        # Colores únicos por técnico
        colores = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'cadetblue', 'darkgreen', 'darkblue']
        tecnicos = df['CodigoTecnico'].dropna().unique()
        color_map = {tec: colores[i % len(colores)] for i, tec in enumerate(tecnicos)}

        # Crear mapa
        mapa = folium.Map(location=[df['Latitud'].mean(), df['Longitud'].mean()], zoom_start=13)

        # Grupos por tramo
        tramos = {
            '08AM-12PM': folium.FeatureGroup(name='Tramo 1: 08AM-12PM', show=True),
            '12PM-16PM': folium.FeatureGroup(name='Tramo 2: 12PM-16PM', show=True),
            '16PM-20PM': folium.FeatureGroup(name='Tramo 3: 16PM-20PM', show=True)
        }

        # Agregar marcadores
        for _, row in df.iterrows():
            tramo = row['Tramo']
            capa = tramos.get(tramo)
            if capa is None:
                continue

            popup_text = f"""
            <b>Código:</b> {row.get('Codigo', '')}<br>
            <b>Cliente:</b> {row.get('Cliente', '')}<br>
            <b>Dirección:</b> {row.get('Direccion', '')}<br>
            <b>Distrito:</b> {row.get('Distrito', '')}<br>
            <b>Negocio:</b> {row.get('Negocio', '')}<br>
            <b>Estado:</b> {row.get('Estado', '')}<br>
            <b>Observaciones:</b> {row.get('Observaciones', '')}<br>
            <b>Tramo:</b> {row.get('Tramo', '')}<br>
            <b>Técnico:</b> {row.get('Tecnico', '')}
            """

            # Marcador
            folium.Marker(
                location=[row['Latitud'], row['Longitud']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color_map.get(row['CodigoTecnico'], 'gray'))
            ).add_to(capa)

            # Inicial del técnico en el mapa
            folium.Marker(
                location=[row['Latitud'], row['Longitud']],
                icon=folium.DivIcon(
                    html=f"""<div style="font-size: 10pt; color:{color_map.get(row['CodigoTecnico'], 'black')};
                            background-color:white; padding:2px; border-radius:3px;">
                            <b>{row['CodigoTecnico']}</b>
                            </div>"""
                )
            ).add_to(capa)

        # Añadir capas de tramos al mapa
        for capa in tramos.values():
            mapa.add_child(capa)

        folium.LayerControl(collapsed=False).add_to(mapa)

        # Mostrar mapa en Streamlit
        st_folium(mapa, width=1400, height=700)

        st.success("✅ Mapa generado correctamente.")
