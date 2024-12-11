import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from threading import Thread
import time

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
actualizar = True

# Función para extraer el perímetro y las caras
def extract_perimeter(msp, height_per_floor=2.55, floors=6):
    perimeter_3d = []
    base_points = []
    total_height = height_per_floor * floors  # Altura total del edificio

    for entity in msp:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            length = np.linalg.norm([end.x - start.x, end.y - start.y])
            if length > 5:  # Filtrar líneas cortas
                perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base Z=0
                perimeter_3d.append([(start.x, start.y, total_height), (end.x, end.y, total_height)])  # Techo
                base_points.append((start.x, start.y))

        elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            if entity.is_closed:
                points = entity.vertices  # Obtener los vértices
                base_polygon = [(p.dxf.location.x, p.dxf.location.y, 0) for p in points]
                techo_polygon = [(p.dxf.location.x, p.dxf.location.y, total_height) for p in points]
                perimeter_3d.append(base_polygon)  # Base
                perimeter_3d.append(techo_polygon)  # Techo
                base_points.extend([(p.dxf.location.x, p.dxf.location.y) for p in points])

    poly3d = []
    for i in range(floors + 1):  # Pisos + techo
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
file_path = r'C:\Users\Pablo\Desktop\Grafrica de Planta\Edificio.dxf'  # Ruta del archivo DXF
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

# Extraer perímetro y crear caras
perimeter_3d, poly3d, base_points, floors, height_per_floor = extract_perimeter(msp, height_per_floor=2.55, floors=6)

# Función para pedir coordenadas del TAG en un hilo separado
def actualizar_posicion():
    global posicion_tag, actualizar
    while actualizar:
        print("Ingrese las coordenadas del TAG (use coma para los decimales, por ejemplo, 1,4):")
        x_tag = float(input("Coordenada X: ").replace(',', '.'))
        y_tag = float(input("Coordenada Y: ").replace(',', '.'))
        z_tag = float(input("Coordenada Z: ").replace(',', '.'))
        posicion_tag = [x_tag, y_tag, z_tag]

# Iniciar hilo para capturar coordenadas
thread = Thread(target=actualizar_posicion)
thread.daemon = True
thread.start()

# Visualización usando matplotlib
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Dibujar líneas de perímetro
for line in perimeter_3d:
    xs, ys, zs = zip(*line)
    ax.plot(xs, ys, zs, color='r', linewidth=3)

# Añadir las caras 3D
for face in poly3d:
    ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

# Dibujar las líneas de conexión entre pisos
for (x, y) in base_points:
    for i in range(floors + 1):
        ax.plot([x, x], [y, y], [0, height_per_floor * i], color='g', linestyle='--', linewidth=3)

# Función de actualización de la posición del TAG
scatter_tag = None
tag_label = None

def actualizar_grafica():
    global scatter_tag, tag_label
    while plt.fignum_exists(fig.number):
        # Eliminar el marcador anterior si existe
        if scatter_tag:
            scatter_tag.remove()
        if tag_label:
            tag_label.remove()

        # Calcular la habitación más cercana
        x, y, z = posicion_tag
        habitacion = encontrar_habitacion(x, y)

        # Dibujar el nuevo marcador
        scatter_tag = ax.scatter(*posicion_tag, color='red', s=150, label='Posición del TAG')

        # Añadir etiqueta al TAG
        etiqueta = f"Dept, Hab: {habitacion}" if habitacion else "Habitación no encontrada"
        tag_label = ax.text(
            posicion_tag[0], posicion_tag[1], posicion_tag[2] + 1, etiqueta, color='black', fontsize=12, ha='center'
        )

        # Pausa para actualizar la gráfica
        plt.pause(1)

# Ejecutar la actualización de la gráfica en el hilo principal
actualizar_grafica()

# Detener el programa limpiamente al cerrar la gráfica
actualizar = False
thread.join
            

