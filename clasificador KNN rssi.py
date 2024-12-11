import pandas as pd
import serial
import time
import re
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Leer el dataset generado previamente
dataset = pd.read_csv('dataset_knn.csv', encoding='latin-1')

# Preparar los datos para el modelo KNN
X = dataset[['ANCLA', 'RSSI']]
y = dataset['Departamento']

# Dividir los datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalizar los datos
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Entrenar el modelo KNN
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)

# Leer datos desde el puerto COM1
serial_port = 'COM1'
baud_rate = 9600

try:
    # Configurar el puerto serial
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Conectado al puerto {serial_port} a {baud_rate} baudios")

    while True:
        # Leer una línea del puerto serial
        line = ser.readline().decode('latin-1').strip()
        if line:
            print(f"Datos recibidos: {line}")
            
            # Buscar los valores RSSI y ANCLA en la línea recibida
            match_data = re.search(r'ANCLA: (?P<ancla>\d+), RSSI: (?P<rssi>-?\d+)', line, re.IGNORECASE)
            if match_data:
                ancla = int(match_data.group('ancla'))
                rssi = int(match_data.group('rssi'))

                # Crear un dataframe temporal para la predicción
                input_data = pd.DataFrame([[ancla, rssi]], columns=['ANCLA', 'RSSI'])
                input_data = scaler.transform(input_data)

                # Realizar la predicción
                prediccion = knn.predict(input_data)
                print(f"Predicción: Departamento {prediccion[0]}")
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
