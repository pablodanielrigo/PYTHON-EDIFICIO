import serial
import time

# Configuración del puerto serial
puerto_serial = serial.Serial('COM1', baudrate=9600, timeout=1)

try:
    while True:
        # Esperar 0.5 segundos antes de la siguiente lectura
        time.sleep(0.5)
        
        # Leer una línea completa de datos en bruto (bytes) del puerto serial
        linea = puerto_serial.readline()
        
        # Imprimir los datos recibidos, en bruto (bytes) y como texto si es decodificable
        if linea:
            print("Datos recibidos en bruto:", linea)  # Imprime los bytes en crudo
            try:
                # Intentar decodificar y mostrar como texto UTF-8
                texto = linea.decode('utf-8', errors='ignore').strip()
                print("Datos decodificados:", texto)
            except UnicodeDecodeError:
                print("No se pudo decodificar la línea")
except KeyboardInterrupt:
    print("Detenido por el usuario")
finally:
    puerto_serial.close()
