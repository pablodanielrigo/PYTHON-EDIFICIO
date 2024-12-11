import serial
import pandas as pd
from openpyxl import Workbook
from datetime import datetime
import os

# Configuración del puerto serial
import serial

serial_port = 'COM1'  # Cambia este puerto al correcto
baud_rate = 9600  # Ajusta la tasa de baudios según la configuración

try:
  String input = Serial.readString();  // Leer los datos del puerto serial
  Serial.println("Datos recibidos: " + input);  // Imprimir los datos recibidos
    if (Serial.available() > 0) {
  
  // Aquí puedes agregar el código de validación para asegurarte que el formato es correcto
}

except serial.SerialException as e:
    print(f"No se pudo abrir el puerto serial: {e}")
    exit()

while True:
    try:
        # Leer datos disponibles en el buffer serial
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='replace')  # Reemplaza caracteres no válidos
            data = data.strip()  # Elimina espacios o saltos de línea adicionales

            # Imprimir los datos recibidos para verificar su estructura
            print("Datos recibidos:", repr(data))

            # Comprobar si los datos contienen las palabras clave esperadas
            if "ANCLA" in data and "RSSI" in data:
                parts = data.split(",")  # Dividir por coma

                # Verificar que tenemos al menos dos partes
                if len(parts) >= 2:
                    ancla_part = parts[0].split(":")
                    rssi_part = parts[1].split(":")

                    # Verificar que ambas partes tienen un valor después de los ":"
                    if len(ancla_part) >= 2 and len(rssi_part) >= 2:
                        ancla = ancla_part[1].strip()
                        rssi = rssi_part[1].strip()
                        print(f"ANCLA: {ancla}, RSSI: {rssi}")
                    else:
                        print("Formato de datos inesperado: falta ANCLA o RSSI.")
                else:
                    print("Formato de datos inesperado: datos incompletos.")
            else:
                print("Formato de datos incorrecto: falta ANCLA o RSSI.")

    except UnicodeDecodeError as e:
        print(f"Error al procesar datos: {e}")
    except IndexError as e:
        print(f"Error al procesar datos: {e}")
    except KeyboardInterrupt:
        print("\nLectura interrumpida por el usuario.")
        break

ser.close()



# Nombre del archivo Excel
file_name = "Datos_RSSI.xlsx"

# Verifica si el archivo ya existe
if not os.path.isfile(file_name):
    # Si el archivo no existe, crea uno nuevo con encabezados
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Datos RSSI"
    headers = ["Fecha/Hora", "Piso", "Departamento", "Habitación/Baño", "Ancla", "RSSI"]
    sheet.append(headers)
    workbook.save(file_name)

# Crear un DataFrame vacío con las columnas necesarias
df = pd.DataFrame(columns=["Fecha/Hora", "Piso", "Departamento", "Habitación/Baño", "Ancla", "RSSI"])

# Función para procesar los datos recibidos
def procesar_datos(linea):
    # Extrae el número de ancla y el RSSI
    try:
        parts = linea.decode().strip().split(",")
        ancla = int(parts[0].split(":")[1].strip())
        rssi = int(parts[1].split(":")[1].strip())
        
        # Asignación de piso, departamento, habitación/baño (esto puede adaptarse)
        ubicacion = {
            1: {"Piso": 1, "Departamento": 101, "Habitación/Baño": "Habitación 1"},
            2: {"Piso": 1, "Departamento": 101, "Habitación/Baño": "Baño"},
            3: {"Piso": 2, "Departamento": 202, "Habitación/Baño": "Habitación 2"},
            4: {"Piso": 2, "Departamento": 202, "Habitación/Baño": "Baño"},
            5: {"Piso": 3, "Departamento": 303, "Habitación/Baño": "Habitación 3"},
        }
        
        # Obtén los datos de ubicación
        piso = ubicacion[ancla]["Piso"]
        departamento = ubicacion[ancla]["Departamento"]
        habitacion_bano = ubicacion[ancla]["Habitación/Baño"]
        
        # Agrega los datos al DataFrame
        new_row = {
            "Fecha/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Piso": piso,
            "Departamento": departamento,
            "Habitación/Baño": habitacion_bano,
            "Ancla": ancla,
            "RSSI": rssi
        }
        
        global df
        df = df.append(new_row, ignore_index=True)
        
        # Guarda los datos en tiempo real en el archivo Excel
        with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, sheet_name="Datos RSSI", header=False, startrow=writer.sheets["Datos RSSI"].max_row)
        
        print(f"Datos guardados: {new_row}")
    
    except Exception as e:
        print(f"Error al procesar datos: {e}")

# Ciclo de lectura continua del puerto serial
try:
    print("Iniciando lectura del puerto serial...")
    while True:
        if ser.in_waiting > 0:
            linea = ser.readline()
            procesar_datos(linea)
except KeyboardInterrupt:
    print("Lectura finalizada.")
finally:
    ser.close()
