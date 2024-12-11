import csv
import re
from datetime import datetime

# Ruta del archivo de entrada
calibration_file = r"C:\Users\Pablo\Documents\calibra_coordenadas.txt"

def generar_dataset_knn(calibration_file):
    dataset = []

    # Leer el archivo de calibración
    with open(calibration_file, 'r', encoding='latin-1') as file:
        for line in file:
            line = line.strip()
            print(f"Procesando línea: '{line}'")  # Mensaje de depuración

            # Limpiar faltas de ortografía, acentos, y caracteres especiales
            line = re.sub(r'Habitaci n', 'Habitacion', line, flags=re.IGNORECASE)
            line = re.sub(r' rea', 'Area', line, flags=re.IGNORECASE)

            # Buscar las líneas con los valores RSSI, ANCLA, Departamento, Habitacion, Piso
            match_data = re.search(
                r'ANCLA: (?P<ancla>\d+), RSSI: (?P<rssi>-?\d+), Piso: (?P<piso>\d+), Departamento: (?P<departamento>[\w\s]+), Habitacion: (?P<habitacion>[^,]+)',
                line, re.IGNORECASE
            )
            if match_data:
                ancla = int(match_data.group('ancla'))
                rssi = int(match_data.group('rssi'))
                piso = int(match_data.group('piso'))
                departamento = match_data.group('departamento').strip()
                habitacion = match_data.group('habitacion').strip()

                # Crear el registro con el formato solicitado
                registro = {
                    'ANCLA': ancla,
                    'RSSI': rssi,
                    'Departamento': departamento,
                    'Habitacion': habitacion,
                    'Piso': piso
                }
                dataset.append(registro)
                print(f"Registro agregado: {registro}")  # Mensaje de depuración

        # Verificar si se añadieron registros al dataset
        if not dataset:
            print("No se encontraron datos en el archivo o el formato no es el esperado.")
            return

        # Guardar el dataset en un archivo CSV
        output_file = 'dataset_knn.csv'
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ANCLA', 'RSSI', 'Departamento', 'Habitacion', 'Piso']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for registro in dataset:
                writer.writerow(registro)

        print(f"Dataset guardado en {output_file}")

# Generar el dataset
generar_dataset_knn(calibration_file)
