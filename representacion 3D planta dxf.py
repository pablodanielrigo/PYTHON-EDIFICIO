import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


# Cargar el archivo DXF
file_path = r'C:\Users\Pablo\Desktop\Edificio.dxf'
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

# Función para extraer el perímetro y las caras
def extract_perimeter(msp, height=10, floors=5):
    perimeter_3d = []
    base_points = []
    
    for entity in msp:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            length = np.linalg.norm([end.x - start.x, end.y - start.y])
            if length > 5:  # Filtrar líneas cortas
                perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base Z=0
                perimeter_3d.append([(start.x, start.y, height), (end.x, end.y, height)])  # Altura Z
                base_points.append((start.x, start.y))

        elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            if entity.is_closed:
                points = entity.vertices  # Obtener los vértices
                # Agregar puntos de la polilínea cerrada
                perimeter_3d.append([(p.dxf.location.x, p.dxf.location.y, 0) for p in points])  # Base
                perimeter_3d.append([(p.dxf.location.x, p.dxf.location.y, height) for p in points])  # Altura
                base_points.extend([(p.dxf.location.x, p.dxf.location.y) for p in points])  # Agregar puntos base

    # Crear caras de los pisos
    poly3d = []
    for i in range(floors + 1):  # Pisos + techo
        z = height * i
        poly3d.append([(x, y, z) for (x, y) in base_points])  # Crear cara del piso o techo

    return perimeter_3d, poly3d, base_points, floors, height  # Devolver también height

# Extraer perímetro y crear caras
perimeter_3d, poly3d, base_points, floors, height = extract_perimeter(msp, height=20, floors=5)

# Visualización usando matplotlib
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Dibujar líneas de perímetro
for line in perimeter_3d:
    xs, ys, zs = zip(*line)
    ax.plot(xs, ys, zs, color='b')

# Añadir las caras 3D
for face in poly3d:
    ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

# Agregar líneas que conectan cada piso en el eje Y
for (x, y) in base_points:
    for i in range(floors + 1):
        ax.plot([x, x], [y, y], [0, height * i], color='g', linestyle='--')  # Líneas en el eje Y

# Configurar los ejes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

#plt.show()
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Función para calcular la posición del tag usando RSSI
def calcular_posicion(rssi, puntos):
    # Convertir RSSI a distancia (simplificación)
    distancias = [10 ** ((-rssi[i] - 30) / 20) for i in range(len(rssi))]  # Fórmula simple
    x = 0
    y = 0
    z = 0
    total_distancia = 0
    
    # Calcular las coordenadas
    for i in range(len(puntos)):
        peso = 1 / distancias[i] if distancias[i] != 0 else 0
        x += puntos[i][0] * peso
        y += puntos[i][1] * peso
        z += puntos[i][2] * peso
        total_distancia += peso
    
    # Normalizar las coordenadas
    if total_distancia > 0:
        x /= total_distancia
        y /= total_distancia
        z /= total_distancia
    
    return x, y, z

# Definir los puntos en el espacio (esquinas del edificio)
postes = [
    (0, 0, 0),  # Poste 1
    (0, 25, 0),  # Poste 2
    (15, 0, 0),  # Poste 3
    (15, 25, 0)   # Poste 4
]

# RSSI de cada punto (ejemplo)
rssi = [-50, -60, -55, -70]  # Valores de RSSI

# Calcular la posición del tag
posicion = calcular_posicion(rssi, postes)

# Graficar
fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

# Graficar los puntos del edificio
for punto in postes:
    ax.scatter(*punto, color='blue', s=100, label='Postes en el edificio')

# Graficar la posición del tag
ax.scatter(*posicion, color='red', s=200, label='Posición del tag')

# Etiquetas y título
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Posición del tag en 3D')
ax.legend()

plt.show()
