import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import os
import requests

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes por Técnico y Tramo")

# Diccionario para asociar imágenes a técnicos usando Jimdo
tecnico_imagenes = {
    'K1': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/if93daac84054c671/version/1746398817/image.png',  # Reemplaza con tu URL de Cloudinary
    'K2': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/iccda9cb82229f3a9/version/1746398817/image.png',
    'K3': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/ica5337bd931d58f9/version/1746398817/image.png',  # Reemplaza con tu URL de Cloudinary
    'K4': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i9c58900a6cbbe4e4/version/1746398817/image.png',
	'K5': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/ic08644f6b1a25134/version/1746398817/image.png',
	'K6': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/ie8564e470660430d/version/1746401498/image.png',
	'K7': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/ibebc9083af63990b/version/1746398817/image.png',
	'K8': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/ifebee64e613bdea0/version/1746398817/image.png',
	'K9': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i58a6e61a4783a1eb/version/1746398817/image.png',
	'K10': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i48e986e631933c3f/version/1746398817/image.png',
	'K11': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/ib06a5828cc072b3d/version/1746398817/image.png',
	'K12': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i218d3ce8195e7994/version/1746398817/image.png',
	'K13': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/id7a1c4b7867542dc/version/1746398817/image.png',
	'K14': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i1a66ce73e6284876/version/1746398818/image.png',
	'K15': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i0f974406e94fcfe7/version/1746398818/image.png',
	'K16': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i08212dcf7a94ec8d/version/1746398818/image.png',
	'K17': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/ia962840892943571/version/1746398818/image.png',
	'K18': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i25e1788c21593e17/version/1746398818/image.png',
	'K19': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i332f827167971787/version/1746398818/image.png',
	'K20': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i5639ff4ca3689021/version/1746401775/image.png',
	'K21': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i4431b80025c7cb0b/version/1746401775/image.png',
	'K22': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i78169bc289f9bb16/version/1746401775/image.png',
	'K23': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i72747b666a54435a/version/1746401498/image.png',
	'K24': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i14c4e9f66122db79/version/1746401775/image.png',
	'K25': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i5b8685a3dfa3c887/version/1746401775/image.png',
	'K26': 'https://image.jimcdn.com/app/cms/image/transf/none/path/sa3d970c4958873be/image/i00783c0365de577b/version/1746401775/image.png',
    # Agrega más técnicos e imágenes según necesites
}

def is_valid_image_url(url):
    """Verifica si la URL de la imagen es válida y accesible."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200 and 'image' in response.headers.get('Content-Type', '')
    except:
        return False

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

                # Usar imagen como ícono del marcador
                if imagen_url and row['CodigoTecnico'] != 'SIN_TECNICO' and is_valid_image_url(imagen_url):
                    icon = folium.CustomIcon(
                        icon_image=imagen_url,
                        icon_size=(30, 30),  # Tamaño del ícono en el mapa
                        icon_anchor=(15, 15),  # Punto de anclaje del ícono (centro)
                        popup_anchor=(0, -15)  # Posición del popup respecto al ícono
                    )
                else:
                    icon = folium.Icon(color='gray')

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
