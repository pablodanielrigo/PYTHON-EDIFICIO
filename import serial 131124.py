import serial
import time

# Conectar al puerto serial
ser = serial.Serial('COM1', 9600, timeout=1)
print("Conectado al puerto COM1 a 9600 baudios.")
print("Leyendo datos y guardando en coordenadas.txt...")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        
        # Filtrar mensajes de espera
        if "ESPERANDO" in line:
            print("ESPERANDO detectado en los datos recibidos")
            time.sleep(0.5)  # Espera medio segundo antes de intentar leer nuevamente
            continue

        # Verificar y procesar datos de RSSI
        try:
            # Divide la línea y convierte a entero solo si es numérico
            rssi_values = [int(value) for value in line.split(',') if value.isdigit()]
            if rssi_values:
                print(f"Valores RSSI recibidos: {rssi_values}")
                # Aquí puedes guardar los datos en coordenadas.txt o procesarlos según sea necesario
            else:
                print("Error en el formato de los datos recibidos")

        except ValueError as e:
            print(f"Error en el formato de los datos recibidos: {e}")

ser.close()
