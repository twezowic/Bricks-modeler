import json
from math import ceil
import numpy as np
import cv2

import trimesh


LENGTH = 20


def create_depth_map(file_num: int) -> list:
    file_name = f'./gltf/{file_num}.gltf'

    with open(file_name) as fh:
        model = json.loads(fh.read())
        minimum = model['accessors'][0]['min']
        maximum = model['accessors'][0]['max']
        size = [ceil(abs(minimum[0] - maximum[0])/LENGTH)*20,
                ceil(abs(minimum[1] - maximum[1])/LENGTH)*20]

    mesh = trimesh.load(file_name)

    # mesh.show()

    points_3d = np.array(mesh.geometry[f'{file_num}-Mesh'].vertices)

    # tworzenie odpowiedniego rozmiaru mapy
    width, height = size
    depth_map = np.full((height, width), np.inf)

    # znormalizowanie vertexów na mapę
    max_coords = np.max(points_3d, axis=0)
    min_coords = np.min(points_3d, axis=0)

    points_3d = (points_3d - min_coords) / (max_coords - min_coords)

    points_3d[:, 0] = width * points_3d[:, 0] - 1
    points_3d[:, 1] = height * points_3d[:, 1] - 1

    # wypełnienie depth mapy
    for (x, y, z) in points_3d:
        u = int(x)
        v = int(y)
        depth_map[v, u] = min(depth_map[v, u], z)

    # normalizacja mapy
    depth_map[np.isinf(depth_map)] = 0
    depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)

    # przetworzenie mapy na współrzędne insetów
    for x in range(int(width/LENGTH)):
        for y in range(int(height/LENGTH)):
            square = depth_map_normalized[y*LENGTH:(y+1)*LENGTH,
                                          x*LENGTH:(x+1)*LENGTH]
            ...

    # np.savetxt(f'depth_map_{file_num}.csv', depth_map_normalized, fmt='%d')

    cv2.imwrite(f'depth_map_{file_num}.png', depth_map_normalized)


create_depth_map(2)


# na razie element: 15573 nie będzie działał poprawnie
# nie działa też dla elementów które mają wyższe punkty np.14417
# jak rozwiązać że środek tak naprawde to 4 punkty -> jak było do tej pory?

# można tylko najwyższy punkt ale nie wszystkie będą działały.
# trzeba jakoś znajdować te 8 kąty które nie zawsze też są wykrywane jako one