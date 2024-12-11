import serial
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Cargar el archivo de calibración con una codificación específica para evitar problemas de caracteres especiales
try:
    calibra_df = pd.read_csv('calibra_coordenadas.txt', sep=",", encoding="latin-1", names=["Fecha_Hora", "Ancla", "RSSI", "Piso", "Departamento", "Habitacion", "Area"])
except UnicodeDecodeError:
    print("Error de decodificación al leer el archivo. Intenta con una codificación diferente.")
    exit()

# Función para solicitar detalles de ubicación
def solicitar_ubicacion():
    piso = input("Ingrese el número de piso (0 para Sótano, 1-5 para los pisos): ")
    departamento = input("Ingrese el departamento (As, An, C, Bs, Bn): ")
    habitacion = input("Ingrese el número de habitación (1, 2, o 3): ")
    area = input("Ingrese el área de la habitación (C para cocina, B para baño, 0 para ninguno): ")
    return piso, departamento, habitacion, area

# Solicitar detalles de ubicación al iniciar
piso, departamento, habitacion, area = solicitar_ubicacion()

# Configuración de la conexión serial
ser = serial.Serial('COM1', 9600, timeout=1)  # Ajusta el puerto según sea necesario

# Configuración de la visualización en tiempo real
plt.ion()
fig, ax = plt.subplots()
sc = ax.scatter([], [], s=100)
ax.set_xlim(0, 20)
ax.set_ylim(0, 30)
ax.set_title("Posición estimada del TAG")
ax.set_xlabel("Coordenada X")
ax.set_ylabel("Coordenada Y")

# Función para actualizar la posición en la gráfica
def actualizar_grafico(coordenada_x, coordenada_y):
    sc.set_offsets([[coordenada_x, coordenada_y]])
    plt.draw()
    plt.pause(0.1)

# Configuración del temporizador
start_time = datetime.now()  # Tiempo de inicio

# Diccionario para mapear departamentos a sus coordenadas
coordenadas_departamentos = {
    "An": (0, 0),
    "C": (8.75, 0),  # Centro entre 'An' y 'As'
    "As": (17.5, 0),
    "Bn": (0, 25),
    "Bs": (17.5, 25)
}

# Comenzar la lectura de datos
while True:
    # Verificar si han pasado 10 minutos para volver a solicitar detalles de ubicación
    current_time = datetime.now()
    if current_time - start_time >= timedelta(minutes=10):
        print("Han pasado 10 minutos. Ingrese los detalles de ubicación nuevamente.")
        piso, departamento, habitacion, area = solicitar_ubicacion()

        # Actualizar el archivo de calibración con los nuevos detalles
        with open("calibra_coordenadas.txt", "a", encoding="latin-1") as file:
            file.write(f"\nDatos de ubicación: Piso: {piso}, Departamento: {departamento}, Habitación: {habitacion}, Área: {area}\n")

        start_time = current_time

    # Leer una línea de datos del puerto serial
    data = ser.readline()
    if data:
        try:
            # Decodificar y limpiar la línea de datos
            decoded_data = data.decode('utf-8', errors='ignore').strip()
            
            # Extraer número de ancla y valor de RSSI
            match = re.search(r'ANCLA: (\d+), RSSI: (\d+)', decoded_data)
            
            if match:
                ancla = int(match.group(1))
                rssi = int(match.group(2))
                print(f"ANCLA: {ancla}, RSSI: {rssi}")
                
                # Buscar coincidencia en el archivo de calibración
                coincidencias_ancla = calibra_df[calibra_df["Ancla"] == ancla]
                coincidencia_cercana = coincidencias_ancla.iloc[(coincidencias_ancla["RSSI"] - rssi).abs().argsort()[:1]]
                
                # Extraer datos de coincidencia y graficar
                piso_cercano = coincidencia_cercana["Piso"].values[0]
                departamento_cercano = coincidencia_cercana["Departamento"].values[0]
                habitacion_cercana = coincidencia_cercana["Habitacion"].values[0]
                
                # Obtener coordenadas del departamento y actualizar gráfico
                coordenada_x, coordenada_y = coordenadas_departamentos.get(departamento_cercano, (0, 0))
                actualizar_grafico(coordenada_x, coordenada_y)

                # Guardar los datos en el archivo de calibración con la fecha y hora
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open("calibra_coordenadas.txt", "a", encoding="latin-1") as file:
                    file.write(f"{timestamp} - ANCLA: {ancla}, RSSI: {rssi}, Piso: {piso_cercano}, Departamento: {departamento_cercano}, "
                               f"Habitación: {habitacion_cercana}, Área: {area}\n")
            else:
                print("Datos no válidos recibidos:", decoded_data)
        except Exception as e:
            print(f"Error al procesar los datos: {e}")
1