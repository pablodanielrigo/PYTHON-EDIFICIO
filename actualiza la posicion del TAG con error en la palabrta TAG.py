import ezdxf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import serial
import time
from datetime import datetime

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
                perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])
                perimeter_3d.append([(start.x, start.y, total_height), (end.x, end.y, total_height)])
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

# Configurar puerto serial
puerto = 'COM1'  # Cambiar al puerto correcto
baudrate = 115200

# Cargar archivo DXF
file_path = r'C:\Users\Pablo\Desktop\Grafrica de Planta\Edificio.dxf'
doc = ezdxf.readfile(file_path)
msp = doc.modelspace()

# Extraer perímetro y caras
perimeter_3d, poly3d, base_points, floors, height_per_floor = extract_perimeter(msp, height_per_floor=2.55, floors=6)

# Iniciar la visualización
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Dibujar el edificio
for line in perimeter_3d:
    xs, ys, zs = zip(*line)
    ax.plot(xs, ys, zs, color='r', linewidth=3)

for face in poly3d:
    ax.add_collection3d(Poly3DCollection([face], facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

# Dibujar líneas verticales entre los pisos
for (x, y) in base_points:
    for i in range(floors + 1):
        ax.plot([x, x], [y, y], [0, height_per_floor * i], color='g', linestyle='--', linewidth=3)

# Configurar ejes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Posición del Tag en 3D')

# Función para actualizar la posición del TAG
def actualizar_tag(posicion):
    # Eliminar el tag anterior (si existe)
    for collection in ax.collections:
        if isinstance(collection, Poly3DCollection):
            continue
        collection.remove()

    # Dibujar el nuevo tag
    ax.scatter(*posicion, color='red', s=150, label='Posición del tag')
    ax.text(posicion[0], posicion[1], posicion[2] + 1, 'TAG', color='black', fontsize=12, ha='center')

# Función para calcular el piso actual
def calcular_piso(z, height_per_floor):
    return int(z // height_per_floor) + 1

# Conectar al puerto serial y leer los datos
try:
    ser = serial.Serial(puerto, baudrate, timeout=1)
    time.sleep(2)  # Esperar a que el puerto se estabilice
    print(f"Conectado al puerto {puerto} a {baudrate} baudios.")

    while True:
        # Leer una línea de datos del puerto serial
        linea = ser.readline().decode('utf-8').strip()
        
        if linea:
            # Suponiendo que los datos recibidos son las coordenadas x, y, z en formato CSV
            try:
                coordenadas = list(map(float, linea.split(',')))
                if len(coordenadas) == 3:
                    # Actualizar la posición del TAG con las coordenadas recibidas
                    posicion_tag = coordenadas
                    print(f"Posición del TAG: {posicion_tag}")
                    piso_actual = calcular_piso(posicion_tag[2], height_per_floor)
                    print(f"Piso actual: {piso_actual}")

                    # Comprobar si el TAG está dentro de los límites
                    dentro_limites = all(0 <= coord <= limite for coord, limite in zip(posicion_tag[:2], [15, 24]))
                    estado_limite = "Dentro de los límites" if dentro_limites else "Fuera de los límites"
                    print(estado_limite)

                    actualizar_tag(posicion_tag)
                    plt.draw()
                    plt.pause(0.1)  # Pausa para actualizar la visualización
            except ValueError:
                print("Error al procesar las coordenadas")

except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
except KeyboardInterrupt:
    print("Lectura detenida por el usuario.")
finally:
    if ser.is_open:
        ser.close()
    print("Puerto serial cerrado.")

# Mostrar la gráfica inicial antes de recibir datos
plt.show()
