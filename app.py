import pandas as pd
import folium
from folium.plugins import MarkerCluster
import tkinter as tk
from tkinter import filedialog
import os
import random

# --- Selección del archivo Excel ---
def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Selecciona tu archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )

archivo_excel = seleccionar_archivo()

if not archivo_excel:
    raise ValueError("No seleccionaste ningún archivo.")

# --- Leer y preparar datos ---
df = pd.read_excel(archivo_excel)

if 'Location' not in df.columns or 'Tecnico' not in df.columns or 'Tramo' not in df.columns:
    raise ValueError("El archivo debe tener las columnas 'Location', 'Tecnico' y 'Tramo'.")

df[['Latitud', 'Longitud']] = df['Location'].str.split(',', expand=True)
df['Latitud'] = df['Latitud'].astype(float)
df['Longitud'] = df['Longitud'].astype(float)
df['CodigoTecnico'] = df['Tecnico'].str.extract(r'(K\d+)')

# --- Crear mapa ---
lat_mean = df['Latitud'].mean()
lon_mean = df['Longitud'].mean()
mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)

# --- Colores por técnico ---
tecnicos = df['CodigoTecnico'].unique()
colores = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'cadetblue', 'darkgreen']
color_map = {tec: colores[i % len(colores)] for i, tec in enumerate(tecnicos)}

# --- Tramos y capas ---
tramos = {
    '08AM-12PM': folium.FeatureGroup(name='Tramo 1: 08AM-12PM', show=True),
    '12PM-16PM': folium.FeatureGroup(name='Tramo 2: 12PM-16PM', show=True),
    '16PM-20PM': folium.FeatureGroup(name='Tramo 3: 16PM-20PM', show=True)
}

for _, row in df.iterrows():
    tramo = row['Tramo']
    capa = tramos.get(tramo)
    if not capa:
        continue  # Si el tramo no es uno de los definidos, lo ignora

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
    # Agregar marcador
    folium.Marker(
        location=[row['Latitud'], row['Longitud']],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color=color_map.get(row['CodigoTecnico'], 'gray'))
    ).add_to(capa)

    # Agregar etiqueta con el código del técnico
    folium.Marker(
        location=[row['Latitud'], row['Longitud']],
        icon=folium.DivIcon(
            html=f"""<div style="font-size: 10pt; color:{color_map.get(row['CodigoTecnico'], 'black')};
                    background-color:white; padding:2px; border-radius:3px;">
                    <b>{row['CodigoTecnico']}</b>
                    </div>"""
        )
    ).add_to(capa)

# Añadir capas al mapa
for capa in tramos.values():
    mapa.add_child(capa)

folium.LayerControl().add_to(mapa)

# --- Guardar archivo en Descargas del usuario ---
ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
archivo_salida = os.path.join(ruta_descargas, "mapa_tramos_tecnicos.html")
mapa.save(archivo_salida)

print(f"✅ Mapa generado en: {archivo_salida}")
