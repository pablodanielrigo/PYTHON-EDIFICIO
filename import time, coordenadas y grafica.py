import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import time
import datetime

# Función para calcular la posición del tag usando RSSI
def calcular_posicion(rssi, puntos):
    distancias = [10 ** ((-rssi[i] - 30) / 20) for i in range(len(rssi))]
    x, y, z = 0, 0, 0
    total_distancia = 0

    for i in range(len(puntos)):
        peso = 1 / distancias[i] if distancias[i] != 0 else 0
        x += puntos[i][0] * peso
        y += puntos[i][1] * peso
        z += puntos[i][2] * peso
        total_distancia += peso

    if total_distancia > 0:
        x /= total_distancia
        y /= total_distancia
        z /= total_distancia

    return x, y, z

# Función para extraer el perímetro y las caras del edificio
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
                perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base
                perimeter_3d.append([(start.x, start.y, total_height), (end.x, end.y, total_height)])  # Techo
                base_points.append((start.x, start.y))

    poly3d = []
    for i in range(floors + 1):
        z = height_per_floor * i
        if len(base_points) > 2:  # Asegurarse de que haya suficientes puntos
            poly3d.append([(x, y, z) for (x, y) in base_points])

    return perimeter_3d, poly3d, base_points

# Función para guardar las coordenadas, hora, minutos, segundos y fecha en un archivo .txt
def guardar_datos(nombre_tag, x, y, z):
    with open('coordenadas_tag.txt', mode='a') as file:
        now = datetime.datetime.now()  # Obtener la fecha y hora actual
        file.write(f"{nombre_tag}, x: {x}, y: {y}, z: {z}, Fecha: {now.strftime('%Y-%m-%d')}, Hora: {now.strftime('%H:%M:%S')}\n")

# Nombre del TAG
nombre_tag = "TAG 1"

# Cargar el archivo DXF
file_path = r'C:\Users\Pablo\Desktop\Grafrica de Planta\Edificio.dxf'
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

# Extraer el perímetro del edificio
perimeter_3d, poly3d, base_points = extract_perimeter(msp, height_per_floor=2.55, floors=6)

# Definir los puntos en el espacio (esquinas del edificio)
postes = [
    (0, 0, 0),     # Poste 1
    (0, 25, 0),    # Poste 2
    (15, 0, 0),    # Poste 3
    (15, 25, 0)    # Poste 4
]

# RSSI de cada punto (ejemplo)
rssi = [-60, -70, -55, -90]  # Valores de RSSI

# Visualización usando matplotlib
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Dibujar líneas de perímetro con mayor grosor
for line in perimeter_3d:
    xs, ys, zs = zip(*line)
    ax.plot(xs, ys, zs, color='r', linewidth=3)

# Añadir las caras 3D
for face in poly3d:
    if len(face) >= 3:  # Asegurarse de que la cara tiene al menos 3 puntos
        ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))
    else:
        print(f"Advertencia: Cara con solo {len(face)} puntos, omitiendo...")

# Graficar los puntos del edificio con etiquetas numeradas
for i, punto in enumerate(postes):
    ax.scatter(*punto, color='blue', s=60)
    ax.text(punto[0], punto[1], punto[2] + 1, f'{i + 1}', color='black', fontsize=11, ha='center')

# Mostrar la gráfica en segundo plano
plt.show(block=False)

# Inicializar un punto anterior para el TAG
tag_point = ax.scatter(0, 0, 0, color='red', s=150, label='Posición del tag')
tag_label = ax.text(0, 0, 1, nombre_tag, color='black', fontsize=12, ha='center')

# Graficar la posición del tag y guardar los datos cada 2 segundos
while True:
    # Calcular la posición del tag
    posicion = calcular_posicion(rssi, postes)

    # Verificar si la posición es válida antes de actualizar
    if all(isinstance(coord, (int, float)) for coord in posicion):
        # Actualizar la posición del TAG
        tag_point._offsets3d = (posicion[0], posicion[1], posicion[2])
        tag_label.set_position((posicion[0], posicion[1]))  # Actualizar etiqueta del TAG
        tag_label.set_3d_properties(posicion[2] + 1)  # Mover etiqueta un poco arriba

        # Actualizar la gráfica
        plt.draw()
        plt.pause(0.001)

        # Guardar las coordenadas y el tiempo actual en el archivo
        guardar_datos(nombre_tag, *posicion)

    # Esperar 2 segundos antes de la siguiente iteración
    time.sleep(2)
