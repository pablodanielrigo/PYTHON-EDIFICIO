import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
# Función para calcular la posición del tag usando RSSI
def calcular_posicion(rssi, puntos):
    """
    Calcula la posición del tag basado en los valores de RSSI de los postes.

    Args:
        rssi (list): Lista de valores RSSI desde cada poste.
        puntos (list): Lista de coordenadas (x, y, z) de cada poste.

    Returns:
        tuple: Coordenadas (x, y, z) calculadas para la posición del tag.
    """
    # Convertir RSSI a distancia (simplificación)
    distancias = [10 ** ((-rssi[i] - 30) / 20) for i in range(len(rssi))]  # Fórmula simple
    x, y, z = 0, 0, 0
    total_distancia = 0

    # Calcular las coordenadas ponderadas por la distancia
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

# Cargar el archivo DXF file 
file_path = r'C:\Users\Pablo\Desktop\Grafrica de Planta\Edificio.dxf'# Testeado C:\Users\Pablo\Desktop\Edificio.dxf
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

# Función para extraer el perímetro y las caras
def extract_perimeter(msp, height_per_floor=2.55, floors=6):
    """
    Extrae el perímetro del edificio y construye las caras para la visualización 3D.

    Args:
        msp: Modelspace del archivo DXF.
        height_per_floor (float): Altura de cada piso en metros.
        floors (int): Número de pisos.

    Returns:
        tuple: Contiene las líneas de perímetro, las caras 3D, puntos base, número de pisos y altura por piso.
    """
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
                # Agregar puntos de la polilínea cerrada para la base y el techo
                base_polygon = [(p.dxf.location.x, p.dxf.location.y, 0) for p in points]
                techo_polygon = [(p.dxf.location.x, p.dxf.location.y, total_height) for p in points]
                perimeter_3d.append(base_polygon)  # Base
                perimeter_3d.append(techo_polygon)  # Techo
                base_points.extend([(p.dxf.location.x, p.dxf.location.y) for p in points])  # Agregar puntos base

    # Crear caras de los pisos y techo
    poly3d = []
    for i in range(floors + 1):  # Pisos + techo
        z = height_per_floor * i
        poly3d.append([(x, y, z) for (x, y) in base_points])  # Crear cara del piso o techo

    return perimeter_3d, poly3d, base_points, floors, height_per_floor

# Extraer perímetro y crear caras
perimeter_3d, poly3d, base_points, floors, height_per_floor = extract_perimeter(msp, height_per_floor=2.55, floors=6)

# Definir los puntos en el espacio (esquinas del edificio)
postes = [
    (0, 0, 0),     # Poste 1
    (0, 25, 0),    # Poste 2
    (15, 0, 0),    # Poste 3
    (15, 25, 0)    # Poste 4
]

# RSSI de cada punto (ejemplo)
rssi = [-60, -70, -55, -90]  # Valores de RSSI

# Calcular la posición del tag
posicion = calcular_posicion(rssi, postes)

# Visualización usando matplotlib
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Dibujar líneas de perímetro con mayor grosor
for line in perimeter_3d:
    xs, ys, zs = zip(*line)
    ax.plot(xs, ys, zs, color='r', linewidth=3)  # Línea de perímetro con linewidth=3

# Añadir las caras 3D
for face in poly3d:
    ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

# Agregar líneas que conectan cada piso en el eje Y con mayor grosor
for (x, y) in base_points:
    for i in range(floors + 1):
        ax.plot([x, x], [y, y], [0, height_per_floor * i], color='g', linestyle='--', linewidth=3)  # Líneas en el eje Y con linewidth=3

# Graficar los puntos del edificio con etiquetas numeradas
for i, punto in enumerate(postes):
    # Evitar múltiples etiquetas en la leyenda
    label = "Postes con N° Ancla" if i == 0 else ""
    ax.scatter(*punto, color='blue', s=60, label=label)  # Etiquetar cada poste solo una vez en la leyenda
    ax.text(punto[0], punto[1], punto[2] + 1, f'{i + 1}', color='black', fontsize=11, ha='center')  # Agregar texto con desplazamiento en Z

# Graficar la posición del tag
ax.scatter(*posicion, color='red', s=150, label='Posición del tag')

# Añadir la etiqueta "TAG" al círculo rojo con desplazamiento en Z
tag_label = "TAG 1"  # Cambiar el número si se requiere
ax.text(posicion[0], posicion[1], posicion[2] + 1, tag_label, color='black', fontsize=12, ha='center')  # Desplazamiento en Z

# Configurar los ejes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Posición del Tag en 3D')

# Mejorar la leyenda para evitar duplicados
handles, labels = ax.get_legend_handles_labels()
unique = dict(zip(labels, handles))
ax.legend(unique.values(), unique.keys())

plt.show()
