# Extraer el perímetro y las caras del edificio
def extract_perimeter(msp, height_per_floor=2.55, floors=6):
    perimeter_3d = []
    base_points = []
    total_height = height_per_floor * floors

    # Extraer entidades del DXF
    for entity in msp:
        print(f"Entidad encontrada: {entity.dxftype()}")  # Imprimir el tipo de entidad

        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            length = np.linalg.norm([end.x - start.x, end.y - start.y])
            if length > 5:  # Solo líneas mayores a 5 unidades
                perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base
                perimeter_3d.append([(start.x, start.y, total_height), (end.x, end.y, total_height)])  # Techo
                base_points.append((start.x, start.y))

        elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:  # Añadir manejo de POLYLINE si está presente
            points = entity.vertices()  # Obtener los vértices
            base_polygon = [(p.x, p.y, 0) for p in points]
            perimeter_3d.append(base_polygon)
            base_points.extend([(p.x, p.y) for p in points])

    # Crear caras de los pisos y techo
    poly3d = []
    for i in range(floors + 1):
        z = height_per_floor * i
        if base_points:
            poly3d.append([(x, y, z) for (x, y) in base_points])

    return perimeter_3d, poly3d, base_points
