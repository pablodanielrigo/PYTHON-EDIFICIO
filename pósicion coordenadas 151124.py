import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Coordenadas base de los departamentos en el piso 0
coordenadas = {
    "An , 1 , 0": (1.4, 1.4, 0),
    "An , 2 , 0": (1.4, 4.15, 0),
    "An , 3 , 0": (1.4, 8.1, 0),
    "C , 1 , 0": (1.4, 11.3, 0),
    "As , 1 , 0": (1.4, 15.5, 0),
    "As , 2 , 0": (1.4, 18.4, 0),
    "As , 3 , 0": (1.4, 21.2, 0),
    "Bn , 1 , 0": (8.6, 1.4, 0),
    "Bn , 2 , 0": (8.6, 4.15, 0),
    "Bn , 3 , 0": (8.6, 8.1, 0),
    "Bs , 1 , 0": (8.6, 15.5, 0),
    "Bs , 2 , 0": (8.6, 18.5, 0),
    "Bs , 3 , 0": (8.6, 21.2, 0)
}

# Función para obtener la entrada del usuario
def solicitar_datos():
    departamento = input("Ingrese el departamento (An, As, C, Bn, Bs): ").strip()
    habitacion = input("Ingrese el número de habitación (1, 2, 3): ").strip()
    piso = input("Ingrese el número de piso (0 a 5): ").strip()

    # Validar entradas
    if departamento not in ["An", "As", "C", "Bn", "Bs"]:
        print("Departamento inválido.")
        return None
    if habitacion not in ["1", "2", "3"]:
        print("Número de habitación inválido.")
        return None
    if not piso.isdigit() or int(piso) < 0 or int(piso) > 5:
        print("Número de piso inválido.")
        return None

    return departamento, habitacion, int(piso)

# Función para graficar la coordenada
def graficar_coordenada(coordenadas, coordenada_seleccionada):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Graficar todas las coordenadas
    for nombre, (x, y, z) in coordenadas.items():
        ax.scatter(x, y, z, label=nombre, s=30)
        ax.text(x, y, z + 0.5, nombre, color='black', fontsize=10, ha='center')

    # Graficar la coordenada seleccionada
    x, y, z = coordenada_seleccionada
    ax.scatter(x, y, z, color='red', s=100, label='Seleccionada')
    ax.text(x, y, z + 0.5, 'Seleccionada', color='red', fontsize=12, ha='center')

    # Configurar los ejes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Posición Seleccionada en 3D')
    plt.legend()
    plt.show()

# Solicitar datos al usuario
datos = solicitar_datos()
if datos:
    departamento, habitacion, piso = datos
    clave = f"{departamento} , {habitacion} , 0"  # Clave para buscar la coordenada base

    if clave in coordenadas:
        x, y, z = coordenadas[clave]
        z += piso * 2.55  # Ajustar la coordenada Z según el piso ingresado
        coordenada_seleccionada = (x, y, z)
        print(f"Coordenada ajustada: {coordenada_seleccionada}")

        # Graficar la coordenada ajustada
        graficar_coordenada(coordenadas, coordenada_seleccionada)
    else:
        print("La combinación de departamento y habitación no existe.")
else:
    print("Error en la entrada de datos.")
