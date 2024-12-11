
import pandas as pd
import serial
import time
import re
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from datetime import datetime
import numpy as np

# Leer el dataset generado previamente
dataset = pd.read_csv('dataset_knn.csv', encoding='latin-1')

# Preparar los datos para el modelo
X = dataset[['ANCLA', 'RSSI']]
# Concatenar Departamento y Habitación para formar una etiqueta única
y = dataset['Departamento'] + "_" + dataset['Habitacion'].astype(str)

# Dividir los datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear un pipeline con normalización y RandomForest para mejorar la precisión
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10))
])

# Entrenar el modelo
pipeline.fit(X_train, y_train)

# Leer datos desde el puerto COM1
serial_port = 'COM1'
baud_rate = 9600

# Variables para almacenar las mediciones
mediciones = []
max_mediciones = 20  # Incrementar el número de mediciones para mayor estabilidad

try:
    # Configurar el puerto serial
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Conectado al puerto {serial_port} a {baud_rate} baudios")

    while True:
        # Leer una línea del puerto serial
        line = ser.readline().decode('latin-1').strip()
        if line:
            # Filtrar los caracteres no deseados
            line = re.sub(r'[^0-9a-zA-Z,:\s]', '', line)
            print(f"Datos recibidos: {line}")
            
            # Buscar los valores RSSI y ANCLA en la línea recibida
            match_data = re.search(r'ANCLA: (?P<ancla>\d+), RSSI: (?P<rssi>\d+)', line, re.IGNORECASE)
            if match_data:
                ancla = int(match_data.group('ancla'))
                rssi = int(match_data.group('rssi'))

                # Almacenar la medición
                mediciones.append((ancla, rssi))

                # Verificar si se alcanzó el número de mediciones requerido
                if len(mediciones) == max_mediciones:
                    # Promediar las lecturas de RSSI para cada ancla
                    mediciones_dict = {}
                    for ancla, rssi in mediciones:
                        if ancla not in mediciones_dict:
                            mediciones_dict[ancla] = []
                        mediciones_dict[ancla].append(rssi)
                    
                    # Crear un dataframe con los valores promedio de RSSI por ancla
                    anclas = list(mediciones_dict.keys())
                    rssis = [np.mean(rssis) for rssis in mediciones_dict.values()]
                    input_data = pd.DataFrame(list(zip(anclas, rssis)), columns=['ANCLA', 'RSSI'])

                    # Realizar la predicción
                    prediccion = pipeline.predict(input_data)
                    departamento_habitacion = prediccion[0]
                    departamento, habitacion = departamento_habitacion.split("_")
                    print(f"Predicción: Departamento {departamento}, Habitación {habitacion}")

                    # Obtener la fecha y hora actuales
                    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Guardar la predicción en el archivo CSV
                    output_file = 'predicciones.csv'
                    with open(output_file, 'a', newline='', encoding='latin-1') as csvfile:
                        fieldnames = ['Fecha', 'Departamento', 'Habitacion']
                        writer = pd.DataFrame([[fecha_hora, departamento, habitacion]], columns=fieldnames)
                        writer.to_csv(csvfile, header=False, index=False)

                    # Limpiar las mediciones para la siguiente ronda
                    mediciones = []
        else:
            print("Esperando datos...")

        # Esperar un poco antes de la siguiente lectura
        time.sleep(0.1)

except serial.SerialException as e:
    print(f"Error al leer el puerto serial: {e}")
except KeyboardInterrupt:
    print("Interrupción del usuario, cerrando conexión serial.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Conexión serial cerrada.")
