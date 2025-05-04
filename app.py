import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import os
import requests

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes por Técnico y Tramo")

# Diccionario para asociar imágenes a técnicos usando URLs directas (ejemplo con Imgur)
tecnico_imagenes = {
'K1': 'https://drive.google.com/uc?export=view&id=1NpNDjygRb6gZwxPBuyDaT2_hAeThcdv5',
	        'K2': 'https://drive.google.com/uc?export=view&id=1AS1snf4F4yCONF9BN2vmTmjGC5vaRk53',
        	'K3': 'https://drive.google.com/uc?export=view&id=1Ghw1iA0TfYX5naSz1b2mkPlfuNJjTUM9',
		'K4': 'https://drive.google.com/uc?export=view&id=1F9vESvpGljaTcEqqEqQoqRB_JSVCbaUZ',
		'K5': 'https://drive.google.com/uc?export=view&id=1BnsJeMSjEbRJ8vX_52XgBkwxBgJ4wtJ3',
		'K6': 'https://drive.google.com/uc?export=view&id=18ADh7OZ5py9laTnr0k0B6pGw5XIA8Nwk',
		'K7': 'https://drive.google.com/uc?export=view&id=1kUv6F03Zp63O6fwqBzxwdZpPb4v5XzeQ',
		'K8': 'https://drive.google.com/uc?export=view&id=1eEBDlMeENLECMt1vepJzE3E6Zqty-MYE',
		'K9': 'https://drive.google.com/uc?export=view&id=1abcpovvhPpntk6kNPs5TLYquUvQq3q3j',
		'K10': 'https://drive.google.com/uc?export=view&id=1HrmnkZ7l2NpnQAxHW7b8MeUelvm00qWL',
		'K11': 'https://drive.google.com/uc?export=view&id=1kamN6mL1gwt2BL0JgUakZTExo626WMEr',
		'K12': 'https://drive.google.com/uc?export=view&id=16Ii9V3XHatErez-NRsn-qxC42feEb7zb',
		'K13': 'https://drive.google.com/uc?export=view&id=1K0LAqdYddDee_vMJ-nEeY8p39gWuE8jc',
		'K14': 'https://drive.google.com/uc?export=view&id=1CGp7w8-LO7qusd57WdndTW0wFQil6zMy',
		'K15': 'https://drive.google.com/uc?export=view&id=10pPTQ34Ax1i9-FrHnq0ThExW5LkqZara',
		'K16': 'https://drive.google.com/uc?export=view&id=16SITfKok6hAuVdKVZvYDCYINAOYTv-EN',
		'K17': 'https://drive.google.com/uc?export=view&id=1Mq1pZic4mapegl8WYVTirx1Vx_7-POQS',
		'K18': 'https://drive.google.com/uc?export=view&id=1iQ5tpHYi_lbo0MTszxIG4wkLiSfrtEqF',
		'K19': 'https://drive.google.com/uc?export=view&id=1jliqrwLx-wRn_jExnKWm-LviYlUTP5EV',
		'K20': 'https://drive.google.com/uc?export=view&id=1pi6GeHkJyz0IFv5IEGGWH6d-TPVCKQPq',
		'K21': 'https://drive.google.com/uc?export=view&id=15N6YoK4vXjuxqUGKxSnJYIG0Guj0uUUk',
		'K22': 'https://drive.google.com/uc?export=view&id=1xzvpe-YxM5N2Y1CyxFPNfizNELQrKLMT',
		'K23': 'https://drive.google.com/uc?export=view&id=1V6Mu5TFlhO2ksN4QCBvLNwg1VeCKLyzQ',
		'K24': 'https://drive.google.com/uc?export=view&id=1sq5AItRn3v3QABsjuzWOu1sz1fCVtL3_',
		'K25': 'https://drive.google.com/uc?export=view&id=1fLHo53ShJckct5103myJK0R3MSmeo7wD',
		'K26': 'https://drive.google.com/uc?export=view&id=1Piz7MDaSyhtVY0nWoxkV_X0lcLNtjnSQ'
    # Agrega más técnicos e imágenes según necesites
}

# Ícono por defecto si no hay imagen o falla la carga
DEFAULT_ICON_URL = 'https://i.imgur.com/default_icon.png'  # Reemplaza con un enlace a un ícono genérico

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

                # Usar imagen como ícono del marcador
                if imagen_url and row['CodigoTecnico'] != 'SIN_TECNICO' and is_valid_image_url(imagen_url):
                    icon = folium.CustomIcon(
                        icon_image=imagen_url,
                        icon_size=(30, 30),  # Tamaño del ícono en el mapa
                        icon_anchor=(15, 15),  # Punto de anclaje del ícono (centro)
                        popup_anchor=(0, -15)  # Posición del popup respecto al ícono
                    )
                else:
                    # Ícono por defecto si no hay imagen, es SIN_TECNICO, o la URL no es válida
                    if is_valid_image_url(DEFAULT_ICON_URL):
                        icon = folium.CustomIcon(
                            icon_image=DEFAULT_ICON_URL,
                            icon_size=(30, 30),
                            icon_anchor=(15, 15),
                            popup_anchor=(0, -15)
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
