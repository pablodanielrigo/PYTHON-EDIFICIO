
import serial
import time
from datetime import datetime

# Configurar el puerto serial
puerto = 'COM1'  # Cambia esto por el puerto adecuado en tu sistema
baudrate = 115200

# Nombre del archivo de salida
archivo_salida = 'coordenadas.txt'

def obtener_estampa_tiempo():
    # Obtener la fecha y hora actual
    ahora = datetime.now()
    return ahora.strftime("%H:%M:%S, %d/%m/%Y")  # Formato: Hora:Min:Seg, Día/Mes/Año

try:
    # Crear la conexión serial
    ser = serial.Serial(puerto, baudrate, timeout=1)
    time.sleep(2)  # Espera a que el puerto se estabilice

    # Abrir el archivo en modo de escritura (agregar datos al final)
    with open(archivo_salida, 'a') as archivo:
        print(f"Conectado al puerto {puerto} a {baudrate} baudios.\nLeyendo datos y guardando en {archivo_salida}...")

        while True:
            # Leer una línea de datos desde el puerto serial
            linea = ser.readline().decode('utf-8', errors='ignore').strip()
            
            if linea:  # Si se lee algo válido
                # Verificar si la palabra "esperando" está en la línea
                if "esperando" in linea.lower():
                    print("ESPERANDO detectado en los datos recibidos")

                else:
                    # Intentar extraer el número de ancla y el valor de RSSI
                    datos = linea.split(',')
                    if len(datos) == 2:
                        try:
                            # Extraer el número de ancla y el valor de RSSI
                            numero_ancla = int(datos[0].split(':')[1].strip())
                            rssi = int(datos[1].split(':')[1].strip())

                            # Filtrar por anclas del 1 al 5
                            if 1 <= numero_ancla <= 5:
                                # Obtener la estampa de tiempo actual
                                estampa_tiempo = obtener_estampa_tiempo()
                                
                                # Preparar la línea con los datos y la estampa de tiempo
                                linea_con_estampa = f"{estampa_tiempo} - Ancla: {numero_ancla}, RSSI: {rssi}"
                                
                                # Mostrar los datos en la consola
                                print(f"Datos recibidos: {linea_con_estampa}")
                                
                                # Escribir los datos en el archivo
                                archivo.write(linea_con_estampa + '\n')
                        
                        except (ValueError, IndexError):
                            print("Error en el formato de los datos recibidos")

            # Pausar 1 segundo antes de leer el siguiente dato
            time.sleep(1)

except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
except KeyboardInterrupt:
    print("Lectura detenida por el usuario.")
finally:
    if ser.is_open:
        ser.close()
    print("Puerto serial cerrado.")
