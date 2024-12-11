import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# Función para extraer el perímetro o las divisiones de un archivo DXF
def extract_elements(file_path, height_per_floor=2.55, floors=6):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    perimeter_3d = []
    base_points = []
    total_height = height_per_floor * floors

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
                points = entity.vertices
                base_polygon = [(p.dxf.location.x, p.dxf.location.y, 0) for p in points]
                techo_polygon = [(p.dxf.location.x, p.dxf.location.y, total_height) for p in points]
                perimeter_3d.append(base_polygon)
                perimeter_3d.append(techo_polygon)
                base_points.extend([(p.dxf.location.x, p.dxf.location.y) for p in points])

    # Crear caras de los pisos y techo
    poly3d = []
    for i in range(floors + 1):
        z = height_per_floor * i
        poly3d.append([(x, y, z) for (x, y) in base_points])

    return perimeter_3d, poly3d, base_points, floors, height_per_floor

# Cargar los dos archivos DXF (perímetro y divisiones internas)
file_path_perimetro = r'C:\Users\Pablo\Desktop\Grafrica de Planta\EDIFICIO5.dxf'  # Testeado C:\Users\Pablo\Desktop\Edificio.dxf
file_path_divisiones = r'C:\Users\Pablo\Desktop\Grafrica de Planta\Edificio.dxf'

# Extraer el perímetro y las divisiones internas
perimeter_3d, poly3d, base_points_perimetro, floors, height_per_floor = extract_elements(file_path_perimetro, height_per_floor=2.55, floors=6)
divisions_3d, poly3d_div, base_points_divisiones, _, _ = extract_elements(file_path_divisiones, height_per_floor=2.55, floors=6)

# Visualización combinada usando matplotlib
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Dibujar perímetro externo con mayor grosor
for line in perimeter_3d:
    xs, ys, zs = zip(*line)
    ax.plot(xs, ys, zs, color='r', linewidth=3)

# Dibujar divisiones internas con menor grosor
for line in divisions_3d:
    xs, ys, zs = zip(*line)
    ax.plot(xs, ys, zs, color='b', linewidth=1)

# Añadir las caras del perímetro
for face in poly3d:
    ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

# Añadir las caras de las divisiones
for face in poly3d_div:
    ax.add_collection3d(Poly3DCollection([face], facecolors='yellow', linewidths=1, edgecolors='b', alpha=.25))

# Configurar los ejes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Combinación del Perímetro Externo y Divisiones Internas en 3D')

plt.show()
