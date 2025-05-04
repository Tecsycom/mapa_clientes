import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import os
import requests

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes por Técnico y Tramo")

# Diccionario para asociar imágenes a técnicos usando Cloudinary
tecnico_imagenes = {
    'K1': 'https://res.cloudinary.com/tu-nombre-de-cloud/image/upload/v1/tecnico_k1.png',  # Reemplaza con tu URL de Cloudinary
    'K2': 'https://i.imgur.com/zYxDCtc.png',  # Reemplaza con tu URL
    'K3': 'https://res.cloudinary.com/tu-nombre-de-cloud/image/upload/v1/tecnico_k3.png',  # Reemplaza con tu URL
    # Agrega más técnicos e imágenes según necesites
}

# Ruta para imágenes locales (opcional, si las tienes localmente)
LOCAL_IMAGES_PATH = 'imagenes/'

def is_valid_image_url(url):
    """Verifica si la URL de la imagen es válida y accesible."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200 and 'image' in response.headers.get('Content-Type', '')
    except:
        return False

def get_icon_image(codigo_tecnico):
    """Obtiene la imagen para el técnico, primero desde URL, luego desde local, o usa ícono por defecto."""
    imagen_url = tecnico_imagenes.get(codigo_tecnico, '')
    
    # Intentar con URL de Cloudinary
    if imagen_url and is_valid_image_url(imagen_url):
        st.write(f"✅ Imagen cargada para {codigo_tecnico}: {imagen_url}")
        return folium.CustomIcon(
            icon_image=imagen_url,
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            popup_anchor=(0, -15)
        )
    
    # Intentar con imagen local
    local_image_path = os.path.join(LOCAL_IMAGES_PATH, f"{codigo_tecnico}.png")
    if os.path.exists(local_image_path):
        st.write(f"✅ Imagen local encontrada para {codigo_tecnico}: {local_image_path}")
        return folium.CustomIcon(
            icon_image=local_image_path,
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            popup_anchor=(0, -15)
        )
    
    # Usar ícono por defecto de Folium
    st.warning(f"⚠️ No se encontró imagen para {codigo_tecnico}. Usando ícono por defecto.")
    return folium.Icon(color='gray')

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

            # Crear mapa
            lat_mean = df['Latitud'].mean()
            lon_mean = df['Longitud'].mean()
            mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)
            Fullscreen().add_to(mapa)

            # Selección de tipo de agrupación
            agrupacion = st.radio(
                "📊 Selecciona el tipo de agrupación:",
                ["Por Tramo", "Por Técnico"],
                horizontal=True
            )

            if agrupacion == "Por Tramo":
                # Crear grupos por tramo
                tramos_unicos = df['Tramo'].unique()
                grupos = {tramo: folium.FeatureGroup(name=f"🕒 {tramo}") for tramo in tramos_unicos}
                grupo_key = 'Tramo'
            else:
                # Crear grupos por técnico
                tecnicos = df['CodigoTecnico'].unique()
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

                # Obtener ícono para el marcador
                icon = get_icon_image(row['CodigoTecnico'])

                folium.Marker(
                    location=[row['Latitud'], row['Longitud']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=icon
                ).add_to(grupo)

                # Agregar etiqueta con el código del técnico
                folium.Marker(
                    location=[row['Latitud'], row['Longitud']],
                    icon=folium.DivIcon(
                        html=f"""<div style='font-size: 10pt; color:black;
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
