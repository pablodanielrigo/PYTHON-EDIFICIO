import serial
import re

# Configuración del puerto serial
ser = serial.Serial('COM1', 9600, timeout=1)  # Cambia 'COM1' al puerto que estés usando
print("Conectado al puerto COM1 a 9600 baudios.")

# Crear o abrir el archivo de texto para guardar los datos
with open('coordenadas.txt', 'w') as file:
    file.write("ANCLA, RSSI\n")  # Escribir encabezado en el archivo

    # Leer continuamente los datos del puerto serial
    while True:
        if ser.in_waiting > 0:  # Si hay datos disponibles para leer
            line = ser.readline().decode('utf-8').strip()  # Leer y decodificar la línea recibida
            
            # Buscar el formato "ANCLA: <número>, RSSI: <valor>"
            match = re.match(r'ANCLA: (\d+), RSSI: (\d+)', line)
            
            if match:
                # Extraer el número de ancla y el valor de RSSI
                anchor_number = match.group(1)
                rssi_value = match.group(2)

                # Imprimir en pantalla
                print(f"ANCLA: {anchor_number}, RSSI: {rssi_value}")
                
                # Guardar los datos en el archivo de texto
                file.write(f"{anchor_number}, {rssi_value}\n")

            else:
                print(f"Datos no válidos recibidos: {line}")
        
        # Puedes agregar un delay pequeño si es necesario para controlar la velocidad de lectura
        # time.sleep(0.1)  # Ajusta según sea necesario

