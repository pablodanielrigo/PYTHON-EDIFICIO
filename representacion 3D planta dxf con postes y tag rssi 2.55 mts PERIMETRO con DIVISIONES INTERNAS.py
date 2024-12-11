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

# Cargar el archivo DXF
file_path = r'C:\Users\Pablo\Desktop\Grafrica de Planta\EDIFICIO5.dxf'  # Ajusta la ruta según tu archivo
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

# Función para extraer el perímetro y las divisiones internas
def extract_walls(msp, height_per_floor=2.55, floors=6):
    """
    Extrae las paredes del edificio, incluyendo el perímetro y las divisiones internas, y construye las caras para la visualización 3D.

    Args:
        msp: Modelspace del archivo DXF.
        height_per_floor (float): Altura de cada piso en metros.
        floors (int): Número de pisos.

    Returns:
        tuple: Contiene las paredes de perímetro, paredes internas, las caras 3D, puntos base, número de pisos y altura por piso.
    """
    perimeter_walls = []
    internal_walls = []
    base_points = []
    total_height = height_per_floor * floors  # Altura total del edificio

    for entity in msp:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            length = np.linalg.norm([end.x - start.x, end.y - start.y])
            if length > 5:  # Filtrar líneas cortas
                # Diferenciar paredes exteriores e interiores por capa, si es posible
                layer = entity.dxf.layer.lower()
                if 'perimeter' in layer or 'externa' in layer:
                    perimeter_walls.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base Z=0
                    perimeter_walls.append([(start.x, start.y, total_height), (end.x, end.y, total_height)])  # Techo
                    base_points.append((start.x, start.y))
                else:
                    internal_walls.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base Z=0
                    internal_walls.append([(start.x, start.y, total_height), (end.x, end.y, total_height)])  # Techo
        elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            if entity.is_closed:
                points = entity.vertices  # Obtener los vértices
                # Diferenciar por capa si es posible
                layer = entity.dxf.layer.lower()
                if 'perimeter' in layer or 'externa' in layer:
                    # Agregar puntos de la polilínea cerrada para la base y el techo
                    base_polygon = [(p.dxf.location.x, p.dxf.location.y, 0) for p in points]
                    techo_polygon = [(p.dxf.location.x, p.dxf.location.y, total_height) for p in points]
                    perimeter_walls.append(base_polygon)  # Base
                    perimeter_walls.append(techo_polygon)  # Techo
                    base_points.extend([(p.dxf.location.x, p.dxf.location.y) for p in points])
                else:
                    # Polilínea cerrada interna (e.g., habitaciones)
                    base_polygon = [(p.dxf.location.x, p.dxf.location.y, 0) for p in points]
                    techo_polygon = [(p.dxf.location.x, p.dxf.location.y, total_height) for p in points]
                    internal_walls.append(base_polygon)  # Base
                    internal_walls.append(techo_polygon)  # Techo
                    base_points.extend([(p.dxf.location.x, p.dxf.location.y) for p in points])
            else:
                # Polilínea abierta: considerar como pared interna
                points = entity.vertices
                for i in range(len(points)-1):
                    p1 = points[i]
                    p2 = points[i+1]
                    internal_walls.append([(p1.dxf.location.x, p1.dxf.location.y, 0),
                                          (p2.dxf.location.x, p2.dxf.location.y, 0)])
                    internal_walls.append([(p1.dxf.location.x, p1.dxf.location.y, total_height),
                                          (p2.dxf.location.x, p2.dxf.location.y, total_height)])
                base_points.extend([(p.dxf.location.x, p.dxf.location.y) for p in points])

    # Crear caras de los pisos y techo
    poly3d = []
    for i in range(floors + 1):  # Pisos + techo
        z = height_per_floor * i
        poly3d.append([(x, y, z) for (x, y) in base_points])  # Crear cara del piso o techo

    return perimeter_walls, internal_walls, poly3d, base_points, floors, height_per_floor

# Extraer paredes y crear caras
perimeter_walls, internal_walls, poly3d, base_points, floors, height_per_floor = extract_walls(msp, height_per_floor=2.55, floors=6)

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

# Dibujar paredes de perímetro con mayor grosor y color rojo
for wall in perimeter_walls:
    if isinstance(wall[0], tuple) and isinstance(wall[1], tuple):
        # LINE entity
        xs, ys, zs = zip(*wall)
        ax.plot(xs, ys, zs, color='red', linewidth=3)  # Línea de perímetro con linewidth=3
    else:
        # POLYLINE entity
        xs, ys, zs = zip(*wall)
        ax.add_collection3d(Poly3DCollection([list(wall)], facecolors='none', linewidths=3, edgecolors='red'))

# Dibujar paredes internas con menor grosor y color naranja
for wall in internal_walls:
    if isinstance(wall[0], tuple) and isinstance(wall[1], tuple):
        # LINE entity
        xs, ys, zs = zip(*wall)
        ax.plot(xs, ys, zs, color='orange', linewidth=1.5, linestyle='--')  # Línea de divisiones internas
    else:
        # POLYLINE entity
        xs, ys, zs = zip(*wall)
        ax.add_collection3d(Poly3DCollection([list(wall)], facecolors='none', linewidths=1.5, edgecolors='orange', linestyle='--'))

# Añadir las caras 3D
for face in poly3d:
    ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='gray', alpha=.25))

# Agregar líneas que conectan cada punto en el eje Z
for (x, y) in base_points:
    ax.plot([x, x], [y, y], [0, height_per_floor * floors], color='green', linestyle='--', linewidth=1)  # Líneas en el eje Z

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
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('Posición del Tag en 3D con Divisiones Internas')

# Mejorar la leyenda para evitar duplicados
handles, labels = ax.get_legend_handles_labels()
unique = dict(zip(labels, handles))
ax.legend(unique.values(), unique.keys())

plt.show()
