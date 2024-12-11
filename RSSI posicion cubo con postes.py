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
    (0, 10, 0),  # Poste 2
    (10, 10, 0),  # Poste 3
    (10, 0, 0)   # Poste 4
]

# RSSI de cada punto (ejemplo)
rssi = [-50, -60, -55, -70]  # Valores de RSSI

# Calcular la posición del tag
posicion = calcular_posicion(rssi, postes)

# Graficar
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

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
