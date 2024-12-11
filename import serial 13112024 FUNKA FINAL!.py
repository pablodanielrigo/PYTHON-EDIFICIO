import serial
import re
from datetime import datetime

ser = serial.Serial('COM1', 9600, timeout=1)  # Asegúrate de que el puerto sea correcto

while True:
    data = ser.readline()  # Lee una línea de datos
    if data:
        try:
            # Decodifica la línea de bytes y elimina caracteres no deseados
            decoded_data = data.decode('utf-8', errors='ignore').strip()
            
            # Usa una expresión regular para extraer el número de ancla y el valor de RSSI
            match = re.search(r'ANCLA: (\d+), RSSI: (\d+)', decoded_data)
            
            if match:
                ancla = match.group(1)  # Número de ancla
                rssi = match.group(2)  # Valor de RSSI
                print(f"ANCLA: {ancla}, RSSI: {rssi}")  # Imprime el número de ancla y RSSI
                
                # Obtén la fecha y hora actual
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Guarda los datos con la fecha y hora en el archivo
                with open("calibra_coordenadas.txt", "a") as file:
                    file.write(f"{timestamp} - ANCLA: {ancla}, RSSI: {rssi}\n")
            else:
                print("Datos no válidos recibidos:", decoded_data)
        except Exception as e:
            print(f"Error al procesar los datos: {e}")
