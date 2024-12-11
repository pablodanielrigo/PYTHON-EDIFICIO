import serial
import re
from datetime import datetime, timedelta
import csv
import os

# Configuración del puerto serial
ser = serial.Serial('COM1', 9600)  # Cambia 'COM1' al puerto adecuado para tu caso

# Función para solicitar detalles de ubicación con validación y confirmación
def solicitar_ubicacion():
    while True:
        # Solicitar y validar el número de piso
        while True:
            piso = input("Ingrese el número de piso: ")
            if piso.isdigit():
                confirm = input(f"Has ingresado piso: {piso}. ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    break
            else:
                print("Entrada inválida. Por favor, ingresa solo números para el piso.")

        # Solicitar y validar el departamento
        departamentos_validos = ['As', 'An', 'C', 'Bs', 'Bn']
        while True:
            departamento = input("Ingrese el departamento (An, C, Bn, As, Bs): ")
            if departamento in departamentos_validos:
                confirm = input(f"Has ingresado departamento: {departamento}. ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    break
            else:
                print(f"Entrada inválida. Por favor, ingresa uno de los siguientes departamentos: {', '.join(departamentos_validos)}.")

        # Solicitar y validar el número de habitación
        while True:
            habitacion = input("Ingrese el número de habitación (1, 2, 3): ")
            if habitacion.isdigit():
                confirm = input(f"Has ingresado habitación: {habitacion}. ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    break
            else:
                print("Entrada inválida. Por favor, ingresa solo números para la habitación.")

        # Solicitar y validar el área
        areas_validas = ['c', 'b', '0']  # 'c' para Cocina, 'b' para Baño, '0' para Común
        while True:
            area = input("Ingrese el área (Cocina c, Baño b, Común 0): ")
            if area in areas_validas:
                confirm = input(f"Has ingresado área: {area}. ¿Es correcto? (s/n): ").lower()
                if confirm == 's':
                    break
            else:
                print(f"Entrada inválida. Por favor, ingresa uno de los siguientes valores para el área: {', '.join(areas_validas)}.")

        # Confirmación final de todos los datos ingresados
        print(f"\nResumen de datos ingresados:")
        print(f"Piso: {piso}")
        print(f"Departamento: {departamento}")
        print(f"Habitación: {habitacion}")
        print(f"Área: {area}")
        confirm_total = input("¿Son correctos todos los datos? (s/n): ").lower()
        if confirm_total == 's':
            break
        else:
            print("Volvamos a ingresar los datos.\n")

    return piso, departamento, habitacion, area

# Solicitar detalles de ubicación inicialmente
piso, departamento, habitacion, area = solicitar_ubicacion()

# Limpiar el buffer del puerto serial después de ingresar los datos de ubicación
ser.flushInput()
ser.flushOutput()

# Configuración del temporizador
start_time = datetime.now()  # Tiempo de inicio


# Nombre del archivo CSV
csv_file = "calibra_coordenadas.csv"

# Campos para el archivo CSV
fieldnames = ['timestamp', 'ancla', 'rssi', 'piso', 'departamento', 'habitacion', 'area']

# Verificar si el archivo existe y si está vacío
file_exists = os.path.isfile(csv_file)
file_is_empty = os.path.getsize(csv_file) == 0 if file_exists else True

# Si el archivo no existe o está vacío, escribir el encabezado
if not file_exists or file_is_empty:
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

# Comenzar la lectura de datos
while True:
    # Verificar si han pasado 15 minutos
    current_time = datetime.now()
    if current_time - start_time >= timedelta(minutes=15):
        # Solicitar detalles de ubicación nuevamente
        print("Han pasado 15 minutos. Ingrese los detalles de ubicación nuevamente.")
        piso, departamento, habitacion, area = solicitar_ubicacion()

        # Limpiar el buffer del puerto serial antes de comenzar a capturar nuevos datos
        ser.flushInput()
        ser.flushOutput()

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

                # Guardar los datos en el archivo CSV
                with open(csv_file, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({
                        'timestamp': timestamp,
                        'ancla': ancla,
                        'rssi': rssi,
                        'piso': piso,
                        'departamento': departamento,
                        'habitacion': habitacion,
                        'area': area
                    })
            else:
                print("Datos no válidos recibidos:", decoded_data)
        except Exception as e:
            print(f"Error al procesar los datos: {e}")
