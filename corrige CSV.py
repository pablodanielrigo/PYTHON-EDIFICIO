import csv

# Nombre del archivo CSV
csv_file = "calibra_coordenadas.csv"

# Lista de códigos de departamento que deben reemplazarse por el piso '1'
departamentos = ['As', 'An', 'Bn', 'Bs', 'C']

# Leer el archivo CSV y almacenar los datos
with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames
    rows = []

    for row in reader:
        # Verificar si el valor en 'piso' es uno de los códigos de departamento
        if row['piso'] in departamentos:
            row['piso'] = '1'  # Reemplazar por el piso '1'
        rows.append(row)

# Escribir los datos actualizados en el mismo archivo CSV
with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("El archivo 'calibra_coordenadas.csv' ha sido actualizado correctamente.")
