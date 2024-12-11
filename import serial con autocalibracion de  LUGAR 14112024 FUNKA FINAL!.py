
 
import serial
import re
from datetime import datetime, timedelta

# Configuración del puerto serial
ser = serial.Serial('COM1', 9600)  # Cambia 'COM3' al puerto adecuado para tu caso

# Función para solicitar detalles de ubicación
def solicitar_ubicacion():
    piso = input("Ingrese el número de piso: ")
    departamento = input("Ingrese  departamento (An, C, Bn, As, Bs): ")
    habitacion = input("Ingrese el número de habitación (1, 2, 3): ")
    area = input("Ingrese el área (Cocina c, Baño b, Comun 0): ")
    return piso, departamento, habitacion, area

# Solicitar detalles de ubicación inicialmente
piso, departamento, habitacion, area = solicitar_ubicacion()

# Configuración del temporizador
start_time = datetime.now()  # Tiempo de inicio

# Comenzar la lectura de datos
while True:
    # Verificar si han pasado 10 minutos
    current_time = datetime.now()
    if current_time - start_time >= timedelta(minutes=10):
        # Solicitar detalles de ubicación nuevamente
        print("Han pasado 10 minutos. Ingrese los detalles de ubicación nuevamente.")
        piso, departamento, habitacion, area = solicitar_ubicacion()

        # Añadir los nuevos detalles al archivo de calibración
        with open("calibra_coordenadas.txt", "a") as file:
            file.write(f"\nDatos de ubicación: Piso: {piso}, Departamento: {departamento}, Habitacion: {habitacion}, Area: {area}\n")

        # Reiniciar el temporizador
        start_time = current_time

    # Leer una línea de datos del puerto serial
    data = ser.readline()
    if data:
        try:
            # Decodificar y limpiar la línea de datos
            decoded_data = data.decode('utf-8', errors='ignore').strip()
            
            # Expresión regular para extraer número de ancla y valor de RSSI
            match = re.search(r'ANCLA: (\d+), RSSI: (\d+)', decoded_data)
            
            if match:
                ancla = match.group(1)  # Número de ancla
                rssi = match.group(2)   # Valor de RSSI
                print(f"ANCLA: {ancla}, RSSI: {rssi}")  # Imprimir en pantalla
                
                # Obtener fecha y hora actual
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Guardar los datos con ubicación, fecha y hora en el archivo
                with open("calibra_coordenadas.txt", "a") as file:
                    file.write(f"{timestamp} - ANCLA: {ancla}, RSSI: {rssi}, Piso: {piso}, Departamento: {departamento}, "
                               f"Habitacion: {habitacion}, Area: {area}\n")
            else:
                print("Datos no válidos recibidos:", decoded_data)
        except Exception as e:
            print(f"Error al procesar los datos: {e}")