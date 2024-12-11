import serial
import re
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Configuración del puerto serial (asegúrate de que el puerto sea el correcto)
ser = serial.Serial('COM1', 9600, timeout=1)

# Archivo de referencia con las coordenadas de calibración
calibration_file = r"C:\Users\Pablo\Desktop\Programas PYTHON\calibra_coordenadas.txt"

# Función para leer los datos de calibración desde el archivo txt
def read_calibration_data(calibration_file):
    calibration_data = []
    with open(calibration_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                location = parts[0]  # Ejemplo: "Piso1-DeptoA-Habitacion1"
                calib_row = {'Location': location}
                for part in parts[1:]:
                    try:
                        device, rssi = part.split(':')
                        calib_row[device.strip()] = float(rssi)
                    except ValueError:
                        continue
                calibration_data.append(calib_row)
    return pd.DataFrame(calibration_data)

# Leer los datos de calibración
calibration_data = read_calibration_data(calibration_file)

# Función para calcular la distancia euclidiana entre los datos en vivo y los de calibración
def compute_distance(calibration_row, live_data):
    devices = ['Ancla1', 'Ancla2', 'Ancla3', 'Ancla4', 'Ancla5']
    distances = []
    for device in devices:
        if device in live_data and device in calibration_row:
            distances.append((live_data[device] - calibration_row[device]) ** 2)
        else:
            # Asignar un error grande si falta algún dato
            distances.append(10000)
    return np.sqrt(sum(distances))

# Función para encontrar la ubicación más cercana según los datos de calibración
def find_closest_location(calibration_data, live_data):
    min_distance = float('inf')
    closest_location = None
    for idx, row in calibration_data.iterrows():
        location = row['Location']
        distance = compute_distance(row, live_data)
        if distance < min_distance:
            min_distance = distance
            closest_location = location
    return closest_location

# Bucle principal para leer los datos en vivo del puerto serial
try:
    live_data = {}
    while True:
        data = ser.readline()  # Lee una línea de datos desde el puerto serial
        if data:
            try:
                # Decodifica la línea de bytes y elimina caracteres no deseados
                decoded_data = data.decode('utf-8', errors='ignore').strip()

                # Usa una expresión regular para extraer el número de ancla y el valor de RSSI
                match = re.search(r'ANCLA: (\d+), RSSI: (-?\d+)', decoded_data)

                if match:
                    ancla = f"Ancla{match.group(1)}"  # Número de ancla (ej. "Ancla1")
                    rssi = float(match.group(2))  # Valor de RSSI
                    print(f"ANCLA: {ancla}, RSSI: {rssi}")  # Imprime el número de ancla y RSSI

                    # Almacena los datos de RSSI recibidos
                    live_data[ancla] = rssi

                    # Si se tienen los datos de las 5 anclas, encontrar la ubicación más cercana
                    if len(live_data) == 5:
                        closest_location = find_closest_location(calibration_data, live_data)

                        if closest_location:
                            print(f"El tag está ubicado en: {closest_location}")

                        # Reinicia los datos en vivo para la próxima ronda de lecturas
                        live_data = {}

                    # Obtén la fecha y hora actual
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Guarda los datos con la fecha y hora en el archivo
                    with open(calibration_file, "a") as file:
                        file.write(f"{timestamp} - ANCLA: {ancla}, RSSI: {rssi}\n")
                else:
                    print("Datos no válidos recibidos:", decoded_data)
            except Exception as e:
                print(f"Error al procesar los datos: {e}")

        # Espera un corto periodo antes de la siguiente lectura para evitar sobrecarga de CPU
        time.sleep(0.1)

except KeyboardInterrupt:
    # Cierra el programa de manera limpia cuando se presiona Ctrl+C
    print("\nPrograma terminado por el usuario.")

finally:
    if ser.is_open:
        ser.close()
    print("Puerto serial cerrado.")
