import streamlit as st
import pandas as pd
import folium
from folium import FeatureGroup
from folium.plugins import MarkerCluster
from folium.features import CustomIcon
from streamlit_folium import st_folium
import io

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes por Técnico y Tramo")

# --- Subir archivo Excel ---
archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Validación de columnas
    columnas_requeridas = ['Codigo', 'Cliente', 'Direccion', 'Distrito', 'Negocio', 'Estado',
                           'Observaciones', 'Tramo', 'Tecnico', 'Location']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("❌ El archivo debe tener todas las columnas requeridas.")
        st.stop()

    # Procesar coordenadas
    df[['Latitud', 'Longitud']] = df['Location'].astype(str).str.split(',', expand=True)
    df['Latitud'] = df['Latitud'].astype(float)
    df['Longitud'] = df['Longitud'].astype(float)

    # Normalizar tramo y técnico
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

    # Íconos personalizados para técnicos (ejemplo)
    iconos_por_tecnico = {
        "K1": "https://drive.google.com/uc?export=view&id=1NpNDjygRb6gZwxPBuyDaT2_hAeThcdv5",
        "K2": "https://drive.google.com/uc?export=view&id=1AS1snf4F4yCONF9BN2vmTmjGC5vaRk53",
        "K3": "https://drive.google.com/uc?export=view&id=1Ghw1iA0TfYX5naSz1b2mkPlfuNJjTUM9",
		"K4": "https://drive.google.com/uc?export=view&id=1F9vESvpGljaTcEqqEqQoqRB_JSVCbaUZ",
		"K5": "https://drive.google.com/uc?export=view&id=1BnsJeMSjEbRJ8vX_52XgBkwxBgJ4wtJ3",
		"K6": "https://drive.google.com/uc?export=view&id=18ADh7OZ5py9laTnr0k0B6pGw5XIA8Nwk",
		"K7": "https://drive.google.com/uc?export=view&id=1kUv6F03Zp63O6fwqBzxwdZpPb4v5XzeQ",
		"K8": "https://drive.google.com/uc?export=view&id=1eEBDlMeENLECMt1vepJzE3E6Zqty-MYE",
		"K9": "https://drive.google.com/uc?export=view&id=1abcpovvhPpntk6kNPs5TLYquUvQq3q3j",
		"K10": "https://drive.google.com/uc?export=view&id=1HrmnkZ7l2NpnQAxHW7b8MeUelvm00qWL",
		"K11": "https://drive.google.com/uc?export=view&id=1kamN6mL1gwt2BL0JgUakZTExo626WMEr",
		"K12": "https://drive.google.com/uc?export=view&id=16Ii9V3XHatErez-NRsn-qxC42feEb7zb",
		"K13": "https://drive.google.com/uc?export=view&id=1K0LAqdYddDee_vMJ-nEeY8p39gWuE8jc",
		"K14": "https://drive.google.com/uc?export=view&id=1CGp7w8-LO7qusd57WdndTW0wFQil6zMy",
		"K15": "https://drive.google.com/uc?export=view&id=10pPTQ34Ax1i9-FrHnq0ThExW5LkqZara",
		"K16": "https://drive.google.com/uc?export=view&id=16SITfKok6hAuVdKVZvYDCYINAOYTv-EN",
		"K17": "https://drive.google.com/uc?export=view&id=1Mq1pZic4mapegl8WYVTirx1Vx_7-POQS",
		"K18": "https://drive.google.com/uc?export=view&id=1iQ5tpHYi_lbo0MTszxIG4wkLiSfrtEqF",
		"K19": "https://drive.google.com/uc?export=view&id=1jliqrwLx-wRn_jExnKWm-LviYlUTP5EV",
		"K20": "https://drive.google.com/uc?export=view&id=1pi6GeHkJyz0IFv5IEGGWH6d-TPVCKQPq",
		"K21": "https://drive.google.com/uc?export=view&id=15N6YoK4vXjuxqUGKxSnJYIG0Guj0uUUk",
		"K22": "https://drive.google.com/uc?export=view&id=1xzvpe-YxM5N2Y1CyxFPNfizNELQrKLMT",
		"K23": "https://drive.google.com/uc?export=view&id=1V6Mu5TFlhO2ksN4QCBvLNwg1VeCKLyzQ,
		"K24": "https://drive.google.com/uc?export=view&id=1sq5AItRn3v3QABsjuzWOu1sz1fCVtL3_",
		"K25": "https://drive.google.com/uc?export=view&id=1fLHo53ShJckct5103myJK0R3MSmeo7wD",
		"K26": "https://drive.google.com/uc?export=view&id=1Piz7MDaSyhtVY0nWoxkV_X0lcLNtjnSQ",
		
        # Agrega el resto...
        "SIN": "https://drive.google.com/uc?export=view&id=ID_ICONO_DEFAULT"
    }

    # Crear mapa base
    mapa = folium.Map(location=[df['Latitud'].mean(), df['Longitud'].mean()], zoom_start=13)

    # --- Agrupar por tramos ---
    grupos_tramos = {}
    for tramo in df['Tramo'].unique():
        emoji = emoji_tramos.get(tramo, "📍")
        grupos_tramos[tramo] = FeatureGroup(name=f"{emoji} {tramo}")
        mapa.add_child(grupos_tramos[tramo])

    # --- Agrupar por técnico ---
    grupos_tecnicos = {}
    for codigo in df['CodigoTecnico'].unique():
        grupos_tecnicos[codigo] = FeatureGroup(name=f"🛠️ Técnico {codigo}", show=False)
        mapa.add_child(grupos_tecnicos[codigo])

    # --- Añadir marcadores ---
    for _, row in df.iterrows():
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

        icon_url = iconos_por_tecnico.get(row['CodigoTecnico'], iconos_por_tecnico["SIN"])
        custom_icon = CustomIcon(icon_url, icon_size=(30, 30))

        marker = folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=custom_icon
        )

        # Añadir a grupos
        grupos_tramos[row['Tramo']].add_child(marker)
        grupos_tecnicos[row['CodigoTecnico']].add_child(marker)

    folium.LayerControl(collapsed=False).add_to(mapa)

    # Mostrar mapa en Streamlit
    st_data = st_folium(mapa, width=1200, height=700)
