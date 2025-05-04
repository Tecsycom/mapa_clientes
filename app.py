import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium
import os

# Título y descripción de la app
st.title("Mapa de Clientes por Técnico y Tramo")
st.write("Carga tu archivo Excel y visualiza las ubicaciones en el mapa")

# Botón para cargar el archivo Excel
archivo = st.file_uploader("📂 Selecciona tu archivo Excel", type=["xlsx", "xls"])

# --- Si se carga un archivo, procesarlo y mostrar el mapa ---
if archivo is not None:
    # Leer el archivo Excel
    df = pd.read_excel(archivo)

    # Verificar que el archivo tiene las columnas necesarias
    columnas_necesarias = ['Location', 'Tecnico', 'Tramo']
    if not all(col in df.columns for col in columnas_necesarias):
        st.error(f"❌ El archivo debe tener las columnas: {', '.join(columnas_necesarias)}")
    else:
        # Procesar coordenadas (extraer Latitud y Longitud)
        df[['Latitud', 'Longitud']] = df['Location'].str.split(',', expand=True)
        df['Latitud'] = df['Latitud'].astype(float)
        df['Longitud'] = df['Longitud'].astype(float)

        # Colores para los técnicos
        colores = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'cadetblue', 'darkgreen']
        df['CodigoTecnico'] = df['Tecnico'].str.extract(r'(K\d+)')

        # Crear mapa
        lat_mean = df['Latitud'].mean()
        lon_mean = df['Longitud'].mean()
        mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)

        # Agrupar por tramo
        tramos = {
            '08AM-12PM': folium.FeatureGroup(name='Tramo 1: 08AM-12PM', show=True),
            '12PM-16PM': folium.FeatureGroup(name='Tramo 2: 12PM-16PM', show=True),
            '16PM-20PM': folium.FeatureGroup(name='Tramo 3: 16PM-20PM', show=True)
        }

        tecnicos = df['CodigoTecnico'].unique()
        color_map = {tec: colores[i % len(colores)] for i, tec in enumerate(tecnicos)}

        # Añadir marcadores al mapa
        for _, row in df.iterrows():
            tramo = row['Tramo']
            capa = tramos.get(tramo)
            if not capa:
                continue

            popup_text = f"""
            <b>Código:</b> {row['Codigo']}<br>
            <b>Cliente:</b> {row['Cliente']}<br>
            <b>Dirección:</b> {row['Direccion']}<br>
            <b>Distrito:</b> {row['Distrito']}<br>
            <b>Negocio:</b> {row['Negocio']}<br>
            <b>Estado:</b> {row['Estado']}<br>
            <b>Observaciones:</b> {row['Observaciones']}<br>
            <b>Tramo:</b> {row['Tramo']}<br>
            <b>Técnico:</b> {row['Tecnico']}
            """
            folium.Marker(
                location=[row['Latitud'], row['Longitud']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color_map.get(row['CodigoTecnico'], 'gray'))
            ).add_to(capa)

            # Marcadores con iniciales del técnico
            folium.Marker(
                location=[row['Latitud'], row['Longitud']],
                icon=folium.DivIcon(
                    html=f"""<div style="font-size: 10pt; color:{color_map.get(row['CodigoTecnico'], 'black')};
                            background-color:white; padding:2px; border-radius:3px;">
                            <b>{row['CodigoTecnico']}</b>
                            </div>"""
                )
            ).add_to(capa)

        # Agregar capas al mapa
        for capa in tramos.values():
            mapa.add_child(capa)

        folium.LayerControl().add_to(mapa)

        # Mostrar mapa en Streamlit
        st.subheader("🗺️ Mapa generado")
        st_folium(mapa, width=1200, height=600)

        # Mensaje de éxito
        st.success("✅ Mapa generado correctamente")

        # Opcional: guardar el mapa en la carpeta de Descargas
        ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
        archivo_salida = os.path.join(ruta_descargas, "mapa_tramos_tecnicos.html")
        mapa.save(archivo_salida)
        st.write(f"El mapa se ha guardado en: {archivo_salida}")
