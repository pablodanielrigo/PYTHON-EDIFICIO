import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from threading import Thread
import pandas as pd
import serial
import time
import re
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
import csv
from datetime import datetime

# Tabla de coordenadas de los puntos centrales de las habitaciones
tabla_coordenadas = {
    "As , 3": (1.4, 1.4),
    "As , 2": (1.4, 4.15),
    "As , 1": (1.4, 8.1),
    "C , 1": (1.4, 11.3),
    "An , 1": (1.4, 15.5),
    "An , 2": (1.4, 18.4),
    "An , 3": (1.4, 21.2),
    "Bs , 3": (8.6, 1.4),
    "Bs , 2": (8.6, 4.15),
    "Bs , 1": (8.6, 8.1),
    "Bn , 1": (8.6, 15.5),
    "Bn , 2": (8.6, 18.5),
    "Bn , 3": (8.6, 21.2),
}

# Configuración del edificio
altura_piso = 2.55  # Altura de cada piso
posicion_tag = [0, 0, 0]  # Coordenadas iniciales del TAG

# Función para extraer el perímetro y las caras
def extract_perimeter(msp, height_per_floor=2.55, floors=6):
    perimeter_3d = []
    base_points = []
    total_height = height_per_floor * floors

    for entity in msp:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            length = np.linalg.norm([end.x - start.x, end.y - start.y])
            if length > 5:
                perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base Z=0
                perimeter_3d.append([(start.x, start.y, total_height), (end.x, end.y, total_height)])  # Techo
                base_points.append((start.x, start.y))

        elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            if entity.is_closed:
                points = entity.vertices
                base_polygon = [(p.dxf.location.x, p.dxf.location.y, 0) for p in points]
                techo_polygon = [(p.dxf.location.x, p.dxf.location.y, total_height) for p in points]
                perimeter_3d.append(base_polygon)
                perimeter_3d.append(techo_polygon)
                base_points.extend([(p.dxf.location.x, p.dxf.location.y) for p in points])

    poly3d = []
    for i in range(floors + 1):
        z = height_per_floor * i
        poly3d.append([(x, y, z) for (x, y) in base_points])

    return perimeter_3d, poly3d, base_points, floors, height_per_floor

# Función para identificar la habitación más cercana
def encontrar_habitacion(x, y):
    habitacion_cercana = None
    distancia_minima = float('inf')
    
    for habitacion, (x_centro, y_centro) in tabla_coordenadas.items():
        distancia = np.sqrt((x - x_centro) ** 2 + (y - y_centro) ** 2)
        if distancia < distancia_minima:
            distancia_minima = distancia
            habitacion_cercana = habitacion

    return habitacion_cercana

# Cargar el archivo DXF
file_path = r'C:\Users\Pablo\Desktop\Grafrica de Planta\Edificio.dxf'
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

# Extraer perímetro y crear caras
perimeter_3d, poly3d, base_points, floors, height_per_floor = extract_perimeter(msp, height_per_floor=2.55, floors=6)

# Preparar el modelo Machine Learning
dataset = pd.read_csv('dataset_knn.csv', encoding='latin-1')
X = dataset[['ANCLA', 'RSSI']]
y = dataset['Departamento'] + "_" + dataset['Habitacion'].astype(str) + "_" + dataset['Piso'].astype(str)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', XGBClassifier(n_estimators=500, random_state=42, max_depth=20, learning_rate=0.1, subsample=0.8))
])
pipeline.fit(X_train, y_train)

# Crear archivo CSV para guardar las mediciones
csv_filename = 'Mediciones_Posicion.csv'
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Fecha', 'Hora', 'Departamento', 'Piso', 'Habitacion', 'Coordenada X', 'Coordenada Y', 'Coordenada Z'])

# Leer desde el puerto serial y actualizar la posición
serial_port = 'COM1'
baud_rate = 9600
mediciones = []
max_mediciones = 15

def actualizar_posicion_automatica():
    global posicion_tag
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        print(f"Conectado al puerto {serial_port} a {baud_rate} baudios")
        while True:
            line = ser.readline().decode(errors='replace').strip()
            if line:
                print(f"Lectura del puerto serial: {line.split(chr(65533))[0]}")  # Mostrar lectura del puerto serial
                line = re.sub(r'[^0-9a-zA-Z,:\s]', '', line)
                match_data = re.search(r'ANCLA: (?P<ancla>\d+), RSSI: (?P<rssi>-?\d+)', line, re.IGNORECASE)
                if match_data:
                    ancla = int(match_data.group('ancla'))
                    rssi_str = re.sub(r'[^0-9-]', '', match_data.group('rssi'))  # Eliminar caracteres no numéricos del RSSI
                    try:
                        rssi = int(rssi_str)
                    except ValueError:
                        print(f"Error al convertir RSSI: {rssi_str}")
                        continue
                    mediciones.append((ancla, rssi))
                    if len(mediciones) == max_mediciones:
                        mediciones_dict = {}
                        for ancla, rssi in mediciones:
                            if ancla not in mediciones_dict:
                                mediciones_dict[ancla] = []
                            mediciones_dict[ancla].append(rssi)

                        anclas = list(mediciones_dict.keys())
                        rssis = [np.mean(rssis) for rssis in mediciones_dict.values()]
                        input_data = pd.DataFrame(list(zip(anclas, rssis)), columns=['ANCLA', 'RSSI'])

                        if not input_data.empty:
                            y_pred_encoded = pipeline.predict(input_data)
                            departamento_habitacion_piso = label_encoder.inverse_transform([y_pred_encoded[0]])[0]
                            departamento, habitacion, piso = departamento_habitacion_piso.split("_")

                            posicion_tag = [
                                tabla_coordenadas[f"{departamento} , {habitacion}"][0],
                                tabla_coordenadas[f"{departamento} , {habitacion}"][1],
                                (int(piso) * altura_piso) - 1
                            ]
                            print(f"Predicción del modelo: Departamento: {departamento}, Habitación: {habitacion}, Piso: {piso}")  # Mostrar predicciones del modelo

                            # Guardar en el archivo CSV
                            with open(csv_filename, mode='a', newline='') as file:
                                writer = csv.writer(file)
                                fecha = datetime.now().strftime('%Y-%m-%d')
                                hora = datetime.now().strftime('%H:%M:%S')
                                writer.writerow([fecha, hora, departamento, piso, habitacion, posicion_tag[0], posicion_tag[1], posicion_tag[2]])

                        mediciones.clear()
    except serial.SerialException as e:
        print(f"Error al leer el puerto serial: {e}")
    except KeyboardInterrupt:
        print("Interrupción del usuario.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

Thread(target=actualizar_posicion_automatica, daemon=True).start()

# Visualización usando matplotlib
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for line in perimeter_3d:
    xs, ys, zs = zip(*line)
    ax.plot(xs, ys, zs, color='r', linewidth=3)

for face in poly3d:
    ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

for (x, y) in base_points:
    for i in range(floors + 1):
        ax.plot([x, x], [y, y], [0, height_per_floor * i], color='g', linestyle='--', linewidth=3)

scatter_tag = None
tag_label = None

def actualizar_grafica():
    global scatter_tag, tag_label
    while plt.fignum_exists(fig.number):
        if scatter_tag:
            scatter_tag.remove()
        if tag_label:
            tag_label.remove()

        x, y, z-1 = posicion_tag
        habitacion = encontrar_habitacion(x, y)

        scatter_tag = ax.scatter(*posicion_tag, color='red', s=150, label='Posición del TAG')

        etiqueta = f"Dept, Hab: {habitacion}" if habitacion else "Habitación no encontrada"
        tag_label = ax.text(
            posicion_tag[0], posicion_tag[1], posicion_tag[2] + 1, etiqueta, color='black', fontsize=12, ha='center'
        )

        plt.pause(1)

actualizar_grafica()
