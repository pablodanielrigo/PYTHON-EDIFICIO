import pandas as pd
import serial
import time
from openpyxl import load_workbook

# Cargar archivo de Excel y leer datos
excel_path = 'C:/Users/Pablo/Desktop/RSSI21dBm_edificio.xlsx'

df = pd.read_excel(excel_path)

# Configurar el puerto serial (ajusta el puerto y la velocidad según corresponda)
ser = serial.Serial('COM1', 9600, timeout=1)  # Cambia '/dev/ttyUSB0' al puerto correcto
time.sleep(2)  # Espera a que el puerto esté listo

# Función para determinar la ubicación del TAG basada en RSSI
def determine_location(rssi_values):
    closest_match = None
    min_difference = float('inf')
    
    # Recorrer cada fila de la tabla y calcular la diferencia con los valores recibidos
    for idx, row in df.iterrows():
        # Valores de referencia de RSSI para cada ancla (ajusta los nombres de las columnas según la hoja)
        ref_rssi = [row['An'], row['As'], row['Bn'], row['Bs'], row['C']]
        
        # Calcular la diferencia total (usamos el error absoluto)
        difference = sum(abs(ref_rssi[i] - rssi_values[i]) for i in range(5))
        
        # Si es la mejor coincidencia, actualizamos
        if difference < min_difference:
            min_difference = difference
            closest_match = row[['Piso', 'Departamento']]
    
    return closest_match

try:
    while True:
        if ser.in_waiting > 0:
            # Leer línea de datos y procesarla
            line = ser.readline().decode('utf-8').strip()
            rssi_values = list(map(int, line.split(',')))  # Convierte los valores de RSSI a una lista de enteros
            
            if len(rssi_values) == 5:  # Asegura que hayamos recibido 5 valores
                location = determine_location(rssi_values)
                
                if location is not None:
                    print(f"Ubicación estimada del TAG: Piso {location['Piso']}, Departamento {location['Departamento']}")
                else:
                    print("No se encontró una ubicación cercana.")
            else:
                print("Error en el formato de los datos recibidos.")
        
        time.sleep(1)

except KeyboardInterrupt:
    print("Finalizando programa...")
finally:
    ser.close()
