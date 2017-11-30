
def is_unique_points(points=None):
    if points is None:
        points = {}
    points_dict = {}
    for key, values in points.items():
        new_key = '%s:%s' % tuple(values)
        is_exists = points_dict.get(new_key, None)
        if is_exists:
            return False
        else:
            points_dict[new_key] = key

    return True
