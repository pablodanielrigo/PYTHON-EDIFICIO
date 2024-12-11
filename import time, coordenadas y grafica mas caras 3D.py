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

# Cargar el archivo DXF
file_path = r'C:\Users\Pablo\Desktop\Grafrica de Planta\Edificio.dxf'
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

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
                perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base
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

    return perimeter_3d, poly3d, base_points

# Extraer perímetro y crear caras
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

# Inicializar la figura y el eje
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Función para graficar el edificio
def graficar_edificio():
    # Dibujar líneas de perímetro
    for line in perimeter_3d:
        xs, ys, zs = zip(*line)
        ax.plot(xs, ys, zs, color='r', linewidth=3)

    # Añadir las caras 3D
    for face in poly3d:
        ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

    # Graficar los puntos del edificio con etiquetas
    for i, punto in enumerate(postes):
        ax.scatter(*punto, color='blue', s=60)
        ax.text(punto[0], punto[1], punto[2] + 1, f'{i + 1}', color='black', fontsize=11, ha='center')

# Graficar el edificio
graficar_edificio()

# Calcular la posición inicial del tag
posicion = calcular_posicion(rssi, postes)
tag_point = ax.scatter(*posicion, color='red', s=150, label='Posición del tag')
tag_label = ax.text(posicion[0], posicion[1], posicion[2] + 1, "TAG 1", color='black', fontsize=12, ha='center')

# Configurar los ejes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Posición del Tag en 3D')
ax.legend()

plt.show(block=False)  # Mostrar la gráfica sin bloquear el hilo

# Función para guardar las coordenadas, hora, minutos, segundos y fecha en un archivo .txt
def guardar_datos(nombre_tag, x, y, z):
    with open('coordenadas_tag.txt', mode='a') as file:
        now = datetime.datetime.now()
        file.write(f"{nombre_tag}, x: {x:.2f}, y: {y:.2f}, z: {z:.2f}, Fecha: {now.strftime('%Y-%m-%d')}, Hora: {now.strftime('%H:%M:%S')}\n")

# Inicializar la posición anterior del TAG
posicion_anterior = None

# Rutina de actualización de la posición del TAG y almacenamiento
while True:
    # Calcular la nueva posición del tag
    nueva_posicion = calcular_posicion(rssi, postes)

    # Comprobar si la posición ha cambiado
    if posicion_anterior is None or nueva_posicion != posicion_anterior:
        # Actualizar la posición del TAG en la gráfica
        tag_point._offsets3d = (nueva_posicion[0], nueva_posicion[1], nueva_posicion[2])
        tag_label.set_position((nueva_posicion[0], nueva_posicion[1]))  # Actualizar etiqueta del TAG
        tag_label.set_3d_properties(nueva_posicion[2] + 1)  # Mover etiqueta un poco arriba

        # Actualizar la gráfica
        plt.draw()

        # Guardar las coordenadas y el tiempo actual en el archivo
        guardar_datos("TAG 1", *nueva_posicion)

        # Actualizar la posición anterior
        posicion_anterior = nueva_posicion

    # Esperar 5 segundos antes de la siguiente iteración
    time.sleep(5)
    plt.pause(0.1)  # Añadir un breve pausa para la actualización visual
