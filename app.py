import pandas as pd
import folium
import tkinter as tk
from tkinter import filedialog
import os

# --- Crear ventana principal ---
ventana = tk.Tk()
ventana.title("Mapa de Clientes por Técnico y Tramo")
ventana.geometry("400x200")

# --- Colores disponibles por técnico ---
colores = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'cadetblue', 'darkgreen']

def procesar_archivo():
    archivo_excel = filedialog.askopenfilename(
        title="Selecciona tu archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )

    if not archivo_excel:
        return

    df = pd.read_excel(archivo_excel)

    if 'Location' not in df.columns or 'Tecnico' not in df.columns or 'Tramo' not in df.columns:
        tk.messagebox.showerror("Error", "El archivo debe tener 'Location', 'Tecnico' y 'Tramo'.")
        return

    # Procesar coordenadas
    df[['Latitud', 'Longitud']] = df['Location'].str.split(',', expand=True)
    df['Latitud'] = df['Latitud'].astype(float)
    df['Longitud'] = df['Longitud'].astype(float)
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

        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 10pt; color:{color_map.get(row['CodigoTecnico'], 'black')};
                        background-color:white; padding:2px; border-radius:3px;">
                        <b>{row['CodigoTecnico']}</b>
                        </div>"""
            )
        ).add_to(capa)

    for capa in tramos.values():
        mapa.add_child(capa)

    folium.LayerControl().add_to(mapa)

    # Guardar en Descargas
    ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
    archivo_salida = os.path.join(ruta_descargas, "mapa_tramos_tecnicos.html")
    mapa.save(archivo_salida)

    # Abrir en navegador
    os.startfile(archivo_salida)

    resultado_label.config(text="✅ Mapa generado y abierto en navegador.")

# --- Botón para seleccionar archivo ---
boton_cargar = tk.Button(ventana, text="📂 Cargar archivo Excel", command=procesar_archivo, font=("Arial", 12))
boton_cargar.pack(pady=30)

# --- Resultado ---
resultado_label = tk.Label(ventana, text="", fg="green", font=("Arial", 10))
resultado_label.pack()

# --- Ejecutar interfaz ---
ventana.mainloop()
