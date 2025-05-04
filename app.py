import pandas as pd
import folium
import tkinter as tk
from tkinter import filedialog
import random

# --- Selección del archivo Excel ---
root = tk.Tk()
root.withdraw()
archivo_excel = filedialog.askopenfilename(
    title="Selecciona tu archivo Excel",
    filetypes=[("Archivos Excel", "*.xlsx *.xls")]
)

if not archivo_excel:
    raise ValueError("No seleccionaste ningún archivo.")

# Leer los datos
df = pd.read_excel(archivo_excel)

# Validar columnas necesarias
if 'Location' not in df.columns or 'Tecnico' not in df.columns:
    raise ValueError("El archivo debe contener las columnas 'Location' y 'Tecnico'.")

# Convertir 'Location' en latitud y longitud
df[['Latitud', 'Longitud']] = df['Location'].str.split(',', expand=True)
df['Latitud'] = df['Latitud'].astype(float)
df['Longitud'] = df['Longitud'].astype(float)

# Obtener el código del técnico (por ejemplo, "K16" de "K16 DIEGO CHERO")
df['CodigoTecnico'] = df['Tecnico'].str.extract(r'(K\d+)')

# Crear mapa centrado
lat_mean = df['Latitud'].mean()
lon_mean = df['Longitud'].mean()
mapa = folium.Map(location=[lat_mean, lon_mean], zoom_start=13)

# Colores únicos por técnico
tecnicos = df['CodigoTecnico'].unique()
colores = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'cadetblue', 'darkgreen']
color_map = {tec: colores[i % len(colores)] for i, tec in enumerate(tecnicos)}

# Agregar marcadores
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
    folium.Marker(
        location=[row['Latitud'], row['Longitud']],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color=color_map.get(row['CodigoTecnico'], 'gray'))
    ).add_to(mapa)

    # Agregar etiqueta con el código del técnico al lado izquierdo del marcador
    folium.map.Marker(
        [row['Latitud'], row['Longitud']],
        icon=folium.DivIcon(
            html=f"""
            <div style="font-size: 10pt; color:{color_map.get(row['CodigoTecnico'], 'black')}; 
                        background-color:white; padding:2px; border-radius:3px;">
                <b>{row['CodigoTecnico']}</b>
            </div>
            """,
        )
    ).add_to(mapa)

# Guardar el mapa
mapa.save('mapa_estatico_todos_los_clientes.html')
print("✅ Mapa generado como 'mapa_estatico_todos_los_clientes.html'")
