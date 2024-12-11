import serial
import pandas as pd
from openpyxl import Workbook
from datetime import datetime

# Configuración del puerto serial
serial_port = 'COM1'  # Reemplaza 'COMX' por el puerto adecuado
baud_rate = 9600      # Asegúrate de que coincida con la configuración de tu dispositivo

# Inicializa el puerto serial
ser = serial.Serial(serial_port, baud_rate)

# Inicializa el archivo Excel
file_name = "Datos_RSSI.xlsx"
try:
    # Intenta cargar el archivo si ya existe
    excel_data = pd.read_excel(file_name)
    writer = pd.ExcelWriter(file_name, engine='openpyxl', mode='a')
    writer.book = Workbook()
except FileNotFoundError:
    # Crea un nuevo archivo si no existe
    writer = pd.ExcelWriter(file_name, engine='openpyxl')
    writer.book = Workbook()
    writer.book.save(file_name)

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
        # Por ejemplo: Mapear número de ancla a una ubicación específica
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
        df.to_excel(writer, index=False, sheet_name="Datos RSSI")
        writer.save()
        
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
    writer.close()
