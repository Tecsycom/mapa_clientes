import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from folium.features import CustomIcon
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📍 Mapa de Clientes por Técnico y Tramo")

# Íconos personalizados por técnico (puedes añadir más Kx si lo necesitas)
iconos_tecnicos = {
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
	"K23": "https://drive.google.com/uc?export=view&id=1V6Mu5TFlhO2ksN4QCBvLNwg1VeCKLyzQ",
	"K24": "https://drive.google.com/uc?export=view&id=1sq5AItRn3v3QABsjuzWOu1sz1fCVtL3_",
	"K25": "https://drive.google.com/uc?export=view&id=1fLHo53ShJckct5103myJK0R3MSmeo7wD",
	"K26": "https://drive.google.com/uc?export=view&id=1Piz7MDaSyhtVY0nWoxkV_X0lcLNtjnSQ",
    "SIN_TECNICO": "https://drive.google.com/uc?export=view&id=1R3XU3e_default_icon_id"  # ícono por defecto
}

archivo = st.file_uploader("📂 Sube tu archivo Excel con coordenadas", type=[".xlsx", ".xls"])

if archivo:
    try:
        df = pd.read_excel(archivo)

        columnas_requeridas = ['latitud_Y', 'longitud_X', 'Tramo', 'Tecnico', 'Location']
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"❌ El archivo debe contener las columnas: {', '.join(columnas_requeridas)}")
        else:
            df['Latitud'] = df['latitud_Y'].astype(float)
            df['Longitud'] = df['longitud_X'].astype(float)

            df['CodigoTecnico'] = df['Tecnico'].fillna('SIN_TECNICO').str.extract(r'(K\d+)')
            df['CodigoTecnico'].fillna('SIN_TECNICO', inplace=True)
            df['Tramo'] = df['Tramo'].fillna('Sin Tramo')

            mapa = folium.Map(location=[df['Latitud'].mean(), df['Longitud'].mean()], zoom_start=13)
            Fullscreen().add_to(mapa)

            # Agrupaciones
            tramos_unicos = df['Tramo'].unique()
            tecnicos_unicos = df['CodigoTecnico'].unique()

            grupos_tramos = {tramo: folium.FeatureGroup(name=f"🕒 {tramo}") for tramo in tramos_unicos}
            grupos_tecnicos = {tec: folium.FeatureGroup(name=f"🛠️ Técnico {tec}", show=False) for tec in tecnicos_unicos}

            for _, row in df.iterrows():
                tramo = row['Tramo']
                tecnico = row['CodigoTecnico']

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

                icon_url = iconos_tecnicos.get(tecnico, iconos_tecnicos["SIN_TECNICO"])
                icono = CustomIcon(icon_url, icon_size=(30, 30))

                marker = folium.Marker(
                    location=[row['Latitud'], row['Longitud']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=icono
                )

                # Añadir a grupo por tramo y técnico
                grupos_tramos[tramo].add_child(marker)
                grupos_tecnicos[tecnico].add_child(marker)

            # Agregar grupos al mapa
            for grupo in grupos_tramos.values():
                mapa.add_child(grupo)
            for grupo in grupos_tecnicos.values():
                mapa.add_child(grupo)

            folium.LayerControl(collapsed=False).add_to(mapa)
            st_folium(mapa, width=1500, height=800)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
