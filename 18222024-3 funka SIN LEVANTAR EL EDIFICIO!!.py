import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Tabla de coordenadas
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

# Configuración de pisos
altura_piso = 2.55  # Altura de cada piso en el eje Z

# Obtener coordenadas del TAG desde el teclado
def ingresar_coordenadas():
    print("Ingrese las coordenadas del TAG (use coma para los decimales, por ejemplo, 1,4):")
    x_tag = float(input("Coordenada X: ").replace(',', '.'))
    y_tag = float(input("Coordenada Y: ").replace(',', '.'))
    z_tag = float(input("Coordenada Z (en metros): ").replace(',', '.'))
    return x_tag, y_tag, z_tag

# Identificar el piso en función del eje Z
def identificar_piso(z):
    piso = int(z // altura_piso) + 1
    return piso

# Identificar la habitación más cercana en la tabla
def encontrar_habitacion(x, y, tabla):
    etiqueta_cercana = None
    distancia_minima = float('inf')
    
    for etiqueta, (x_tabla, y_tabla) in tabla.items():
        distancia = np.sqrt((x - x_tabla)**2 + (y - y_tabla)**2)
        if distancia < distancia_minima:
            distancia_minima = distancia
            etiqueta_cercana = etiqueta
    
    return etiqueta_cercana, distancia_minima

# Visualización del edificio y la posición del TAG
def graficar_edificio(posicion_tag, etiqueta_habitacion, piso):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Coordenadas del edificio
    etiquetas = list(tabla_coordenadas.keys())
    x_coords = [coord[0] for coord in tabla_coordenadas.values()]
    y_coords = [coord[1] for coord in tabla_coordenadas.values()]
    z_coords = [0] * len(tabla_coordenadas)  # Base en el primer piso

    # Dibujar puntos de habitaciones en el gráfico
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        for z in range(0, 5):  # Hasta el piso 5
            ax.scatter(x, y, z * altura_piso, color='blue', s=20)
            ax.text(x, y, z * altura_piso, etiquetas[i], fontsize=9)

    # Dibujar posición del TAG
    x_tag, y_tag, z_tag = posicion_tag
    ax.scatter(x_tag, y_tag, z_tag, color='red', s=150, label='Posición del TAG')
    ax.text(x_tag, y_tag, z_tag + 0.5, f"{etiqueta_habitacion}, Piso {piso}", fontsize=12, color='black', ha='center')

    # Configuración de la gráfica
    ax.set_title("Ubicación del TAG en el Edificio")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.legend()
    plt.show()

# Flujo principal del programa
if __name__ == "__main__":
    while True:
        # Ingresar coordenadas del TAG
        x_tag, y_tag, z_tag = ingresar_coordenadas()

        # Identificar el piso
        piso = identificar_piso(z_tag)

        # Identificar la habitación más cercana
        etiqueta_habitacion, distancia = encontrar_habitacion(x_tag, y_tag, tabla_coordenadas)

        # Mostrar resultado
        print(f"El TAG está en el {etiqueta_habitacion}, piso {piso}.")

        # Graficar el edificio y la posición del TAG
        graficar_edificio((x_tag, y_tag, z_tag), etiqueta_habitacion, piso)
