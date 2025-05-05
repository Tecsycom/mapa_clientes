import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes Tecsycom PeruFibra")

# Colores expandidos para cubrir 25 técnicos
colores = [
    'red', 'blue', 'green', 'orange', 'purple', 'darkred', 'cadetblue', 'darkgreen',
    'pink', 'lightblue', 'beige', 'gray', 'black', 'lightgreen', 'darkblue', 'lightred',
    'darkpurple', 'lightgray', 'darkorange', 'lightpurple', 'goldenrod', 'teal', 'maroon',
    'olive', 'navy'
]

# Diccionario para asociar emojis de reloj a tramos
emoji_tramos = {
    '08AM-12PM': '🕗',  # Reloj a las 8:00
    '12PM-16PM': '🕛',  # Reloj a las 12:00
    '16PM-20PM': '🕓',   # Reloj a las 16:00
    'SIN TRAMO': '⏳'  # Emoji genérico para tramos no especificados
}

# Configuración de Google Sheets API
SPREADSHEET_ID = '1H4h18-bmIPe6k3UdjRZKqd7jsWE2pP5H'
SHEET_NAME = 'MAPS'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_sheets_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

def update_google_sheet(spreadsheet_id, sheet_name, data):
    try:
        service = get_sheets_service()
        # Convertir el DataFrame a una lista de listas
        values = [data.columns.tolist()] + data.values.tolist()
        body = {'values': values}
        # Usar el nombre de la hoja (MAPS!A1)
        range_name = f"{sheet_name}!A1"
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        st.success(f"Hoja de Google Sheets 'MAPS' actualizada: {result.get('updatedCells')} celdas modificadas")
    except HttpError as e:
        st.error(f"Error al actualizar Google Sheets: {e}")

# Interfaz de Streamlit
archivo = st.file_uploader("📂 Sube tu archivo Excel con coordenadas", type=[".xlsx", ".xls"])

if archivo:
    try:
        df = pd.read_excel(archivo)

        # Validación de columnas
        columnas_requeridas = ['latitud_Y', 'longitud_X', 'Tramo', 'Tecnico', 'Location']
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"❌ El archivo debe contener las columnas: {', '.join(columnas_requeridas)}")
        else:
            # Actualizar Google Sheets
            update_google_sheet(SPREADSHEET_ID, SHEET_NAME, df)

            # Procesamiento para el mapa
            df['Latitud'] = df['latitud_Y'].astype(float)
            df['Longitud'] = df['longitud_X'].astype(float)
            df['CodigoTecnico'] = df['Tecnico'].fillna('SIN_TECNICO').str.extract(r'(K\d+)')
            df['CodigoTecnico'].fillna('SIN_TECNICO', inplace=True)
            df['Tramo'] = df['Tramo'].fillna('Sin Tramo')

            tecnicos = df['CodigoTecnico'].unique()
            color_map = {tec: colores[i % len(colores)] for i, tec in enumerate(tecnicos)}

            agrupacion = st.radio(
                "📊 Selecciona el tipo de agrupación:",
                ["Por Tramo", "Por Técnico"],
                horizontal=True
            )

            lat_mean = df['Latitud'].mean()
            lon_mean = df['Longitud'].mean()
            mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)
            Fullscreen().add_to(mapa)

            if agrupacion == "Por Tramo":
                tramos_unicos = df['Tramo'].unique()
                grupos = {
                    tramo: folium.FeatureGroup(name=f"{emoji_tramos.get(tramo, '⏳')} {tramo}")
                    for tramo in tramos_unicos
                }
                grupo_key = 'Tramo'
            else:
                grupos = {tec: folium.FeatureGroup(name=f"👷 {tec}") for tec in tecnicos}
                grupo_key = 'CodigoTecnico'

            for _, row in df.iterrows():
                key = row[grupo_key]
                grupo = grupos[key]
                
                popup_text = f"""
                <b>Código:</b> {row.get('Codigo', '')}<br>
                <b>Cliente:</b> {row.get('Cliente', '')}<br>
                <b>Dirección:</b> {row.get('Direccion', '')}<br>
                <b>Distrito:</b> {row.get('Distrito', '')}<br>
                <b>Negocio:</b> {row.get('Negocio', '')}<br>
                <b>Estado:</b> {row.get('Estado2', '')}<br>
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

            for capa in grupos.values():
                mapa.add_child(capa)

            folium.LayerControl(collapsed=False).add_to(mapa)

            st_folium(mapa, width=1500, height=800)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
