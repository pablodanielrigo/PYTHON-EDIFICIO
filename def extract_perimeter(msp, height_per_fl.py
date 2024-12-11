def extract_perimeter(msp, height_per_floor=2.55, floors=6):
    """
    Extrae el perímetro del edificio y construye las caras para la visualización 3D.

    Args:
        msp: Modelspace del archivo DXF.
        height_per_floor (float): Altura de cada piso en metros.
        floors (int): Número de pisos.

    Returns:
        tuple: Contiene las líneas de perímetro, las caras 3D, puntos base.
    """
    perimeter_3d = []
    base_points = []

    for entity in msp:
        if entity.dxftype() == 'LINE':
            # Para entidades LINE
            start = entity.dxf.start
            end = entity.dxf.end
            perimeter_3d.append([(start.x, start.y, 0), (end.x, end.y, 0)])  # Base Z=0
            perimeter_3d.append([(start.x, start.y, floors * height_per_floor), (end.x, end.y, floors * height_per_floor)])
            base_points.append((start.x, start.y))

        elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            # Para LWPOLYLINE o POLYLINE
            points = entity.get_points('xy')
            if entity.is_closed:  # Asegurarse de cerrar el polígono si aplica
                points.append(points[0])
            base_polygon = [(p[0], p[1], 0) for p in points]
            techo_polygon = [(p[0], p[1], floors * height_per_floor) for p in points]
            perimeter_3d.append(base_polygon)  # Base
            perimeter_3d.append(techo_polygon)  # Techo
            base_points.extend([(p[0], p[1]) for p in points])  # Puntos base

    # Crear caras de los pisos
    poly3d = []
    for i in range(floors + 1):  # Pisos + techo
        z = height_per_floor * i
        poly3d.append([(x, y, z) for (x, y) in base_points])  # Crear cara del piso o techo

    return perimeter_3d, poly3d, base_points
