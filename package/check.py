def is_location(annotations):
    for annotation in annotations[1:]:
        # Compute bounding box area
        vertices = annotation.bounding_poly.vertices
        if len(vertices) < 4:
            continue  # skip malformed boxes

        x_coords = [v.x for v in vertices]
        y_coords = [v.y for v in vertices]
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        area = width * height

        # print(annotation.description, area)

        # Apply both conditions
        # print(annotation.description)
        if annotation.description == 'BLOCK' and area > 20000:
            return True

    return False
