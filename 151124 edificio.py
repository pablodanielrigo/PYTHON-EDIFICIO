import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Función para extraer el perímetro y las caras del DXF
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

    for entity in msp:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base Z=0
            perimeter_3d.append([(start.x, start.y, floors * height_per_floor), (end.x, end.y, floors * height_per_floor)])
            base_points.append((start.x, start.y))

        elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            if entity.is_closed:
                points = entity.vertices
                # Agregar puntos de la polilínea cerrada para la base y el techo
                base_polygon = [(p.x, p.y, 0) for p in points]
                techo_polygon = [(p.x, p.y, floors * height_per_floor) for p in points]
                perimeter_3d.append(base_polygon)  # Base
                perimeter_3d.append(techo_polygon)  # Techo
                base_points.extend([(p.x, p.y) for p in points])  # Puntos base

    # Crear caras de los pisos
    poly3d = []
    for i in range(floors + 1):  # Pisos + techo
        z = height_per_floor * i
        poly3d.append([(x, y, z) for (x, y) in base_points])  # Crear cara del piso o techo

    return perimeter_3d, poly3d, base_points

# Cargar el archivo DXF
file_path = r'C:\Users\Pablo\Desktop\Grafrica de Planta\Edificio.dxf'
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

# Extraer el perímetro y las caras del edificio
perimeter_3d, poly3d, base_points = extract_perimeter(msp, height_per_floor=2.55, floors=6)

# Coordenadas base de los departamentos en el piso 0
tabla_coordenadas = {
    "An , 1": (1.4, 1.4),
    "An , 2": (1.4, 4.15),
    "An , 3": (1.4, 8.1),
    "C , 1": (1.4, 11.3),
    "As , 1": (1.4, 15.5),
    "As , 2": (1.4, 18.4),
    "As , 3": (1.4, 21.2),
    "Bn , 1": (8.6, 1.4),
    "Bn , 2": (8.6, 4.15),
    "Bn , 3": (8.6, 8.1),
    "Bs , 1": (8.6, 15.5),
    "Bs , 2": (8.6, 18.5),
    "Bs , 3": (8.6, 21.2),
}

# Función para calcular la posición del TAG basada en departamento, habitación y piso
def calcular_posicion_tag(departamento, habitacion, piso):
    clave = f"{departamento} , {habitacion}"
    if clave not in tabla_coordenadas:
        raise ValueError("La combinación de departamento y habitación no existe en la tabla.")
    
    x, y = tabla_coordenadas[clave]
    z = piso * 2.55  # Calcular Z según el piso
    return x, y, z

# Solicitar datos al usuario
departamento = input("Ingrese el departamento (An, As, C, Bn, Bs): ").strip()
habitacion = input("Ingrese el número de habitación (1, 2, 3): ").strip()
piso = int(input("Ingrese el número de piso (0 a 5): ").strip())

# Calcular la posición del TAG
try:
    posicion = calcular_posicion_tag(departamento, habitacion, piso)
except ValueError as e:
    print(e)
    exit()

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
    for i in range(6):  # Hasta el piso 5
        ax.plot([x, x], [y, y], [0, i * 2.55], color='g', linestyle='--', linewidth=1)

# Graficar la posición del TAG
ax.scatter(*posicion, color='red', s=150, label='TAG')
ax.text(posicion[0], posicion[1], posicion[2] + 1, 'TAG', color='red', fontsize=10, ha='center')

# Configurar los ejes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Edificio Completo con Posición del TAG')

plt.show()



