import csv
import json
from math import ceil, floor
import numpy as np
import cv2
from rich.progress import track
import os

import trimesh

LENGTH = 20


def is_point_in_triangle(px, py, A, B, C):
    """
    Check if sum of area of triangles
    creted from given point is equal to triangle
    """
    def triangle_area(x1, y1, x2, y2, x3, y3):
        return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)

    threshold = 1e-6

    area_ABC = triangle_area(A[0], A[1], B[0], B[1], C[0], C[1])
    area_PAB = triangle_area(px, py, A[0], A[1], B[0], B[1])
    area_PBC = triangle_area(px, py, B[0], B[1], C[0], C[1])
    area_PCA = triangle_area(px, py, C[0], C[1], A[0], A[1])

    return abs(area_ABC - (area_PAB + area_PBC + area_PCA)) < threshold


# calculating z value in projection from 3D to 2D
def calculate_z(x, y, A, B, C):
    AB = np.subtract(B, A)
    AC = np.subtract(C, A)

    normal = np.cross(AB, AC)

    # równanie płaszczyzny
    a, b, c = normal
    d = -np.dot(normal, A)

    if c == 0:  # równoległe do osi Z
        return None

    return -(a * x + b * y + d) / c


def is_circle(contour):
    _, radius = cv2.minEnclosingCircle(contour)
    _, _, w, h = cv2.boundingRect(contour)
    print(radius)

    aspect_ratio = w / h

    return (
        0.8 <= aspect_ratio <= 1.2 and
        20 <= radius <= 40
    )

def get_size(file_name: str):
    with open(file_name) as fh:
        model = json.loads(fh.read())
        minimum = model['accessors'][0]['min']
        maximum = model['accessors'][0]['max']
        size = [ceil(abs(floor(minimum[0]) - floor(maximum[0]))),
                ceil(abs(floor(minimum[1]) - floor(maximum[1]))),
                ceil(abs(floor(minimum[2]) - floor(maximum[2]))),
                ]
    return size


def depth_map_bottom(file_num: int, generate_images=False):
    file_name = f'./api/database/gltf/{file_num}.gltf'

    size = get_size(file_name)

    mesh = trimesh.load(file_name)
    vertices = np.array(mesh.geometry[f'{file_num}-Mesh'].vertices)
    faces = np.array(mesh.geometry[f'{file_num}-Mesh'].faces)

    width, height, _ = size
    depth_map = np.full((height, width), np.inf)

    # znormalizowanie vertexów na mapę
    max_coords = np.max(vertices, axis=0)
    min_coords = np.min(vertices, axis=0)

    vertices = (vertices - min_coords) / (max_coords - min_coords)

    vertices[:, 0] = width * vertices[:, 0] - 1
    vertices[:, 1] = height * vertices[:, 1] - 1

    # wypełnienie depth mapy
    for face in faces:
        p1, p2, p3 = vertices[face]
        x_coords = [int(p1[0]), int(p2[0]), int(p3[0])]
        y_coords = [int(p1[1]), int(p2[1]), int(p3[1])]
        min_x, max_x = max(min(x_coords), 0), min(max(x_coords), width - 1)
        min_y, max_y = max(min(y_coords), 0), min(max(y_coords), height - 1)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if is_point_in_triangle(x, y, p1, p2, p3):
                    depth_map[y, x] = 1
    depth_map[np.isinf(depth_map)] = 0
    depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
    depth_map_normalized = depth_map_normalized.astype(np.uint8)

    if generate_images:
        output_image = cv2.cvtColor(depth_map_normalized.astype(np.uint8), cv2.COLOR_GRAY2BGR)
    _, binary_image = cv2.threshold(depth_map_normalized, 128, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    inside_points = []
    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)

        # przesunięcie gdy istnieją specjalne fragmenty częsci
        min_x, min_y = 0, 0
        if (offset := width % 20) != 0:
            min_x = offset
    
        if (offset := height % 20) != 0:
            min_y = offset
        
        possible_insets = []
        for x in range(10+min_x, width, 20):
            for y in range(10+min_y, height, 20):
                possible_insets.append([x, y])
        for point in possible_insets:
            minimum = (point[0]-3, point[1]+3)
            maximum = (point[0]+3, point[1]-3)
            if cv2.pointPolygonTest(largest_contour, tuple(minimum), False) >= 0 and cv2.pointPolygonTest(largest_contour, tuple(maximum), False) >= 0:
                inside_points.append((point[0], point[1], 0))
                if generate_images:
                    cv2.circle(output_image, tuple(point), 3, (0, 0, 255), -1)
        if generate_images:
            cv2.drawContours(output_image, [largest_contour], -1, (0, 255, 255), thickness=2)
    elif np.min(depth_map) == 1:
        for x in range(10, width, 20):
            for y in range(10, height, 20):
                inside_points.append([x, y, 0])
                if generate_images:
                    cv2.circle(output_image, (x, y), 3, (0, 0, 255), -1)

    if generate_images:    
        cv2.imwrite(f'depth_map/faces/bot_{file_num}.png', output_image)

    return inside_points


def depth_map_top(file_num: int, generate_images=False):
    file_name = f'./api/database/gltf/{file_num}.gltf'

    size = get_size(file_name)

    mesh = trimesh.load(file_name)

    # mesh.show()

    vertices = np.array(mesh.geometry[f'{file_num}-Mesh'].vertices)
    faces = np.array(mesh.geometry[f'{file_num}-Mesh'].faces)

    # tworzenie odpowiedniego rozmiaru mapy i skalowanie aby zachować więcej szczegółów
    width, height, z_value = size
    width *= 4
    height *= 4
    depth_map = np.full((height, width), -np.inf)

    # znormalizowanie vertexów na mapę
    max_coords = np.max(vertices, axis=0)
    min_coords = np.min(vertices, axis=0)

    vertices = (vertices - min_coords) / (max_coords - min_coords)

    vertices[:, 0] = width * vertices[:, 0] - 1
    vertices[:, 1] = height * vertices[:, 1] - 1

    # wypełnienie depth mapy
    for face in faces:
        p1, p2, p3 = vertices[face]
        x_coords = [int(p1[0]), int(p2[0]), int(p3[0])]
        y_coords = [int(p1[1]), int(p2[1]), int(p3[1])]

        min_x, max_x = max(min(x_coords), 0), min(max(x_coords), width - 1)
        min_y, max_y = max(min(y_coords), 0), min(max(y_coords), height - 1)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if is_point_in_triangle(x, y, p1, p2, p3):
                    if z := calculate_z(x, y, p1, p2, p3):
                        depth_map[y, x] = max(depth_map[y, x], z)

    # normalizacja mapy
    depth_map[np.isinf(depth_map)] = 0
    depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)

    depth_map_normalized = depth_map_normalized.astype(np.uint8)

    # jednak nie potrzebne
    # equalized_image = cv2.equalizeHist(depth_map_normalized)

    # # zwiększenie kontrastu
    sobelx = cv2.Sobel(depth_map_normalized, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(depth_map_normalized, cv2.CV_64F, 0, 1, ksize=5)

    gradient_magnitude = cv2.magnitude(sobelx, sobely)

    gradient_magnitude_normalized = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX)
    gradient_magnitude_normalized = gradient_magnitude_normalized.astype(np.uint8)

    if generate_images:
        output_image = cv2.cvtColor(depth_map_normalized.astype(np.uint8), cv2.COLOR_GRAY2BGR)

    insets = set()

    # wyznaczanie krawędzi
    contours, _ = cv2.findContours(gradient_magnitude_normalized,
                                   cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if is_circle(contour):
            (x, y), _ = cv2.minEnclosingCircle(contour) 
            if generate_images:
                cv2.drawContours(output_image, [contour],
                                 -1, (0, 0, 255), 1)
            insets.add((floor(x/40)*10+10, floor(y/40)*10+10,
                        (ceil((depth_map[int(y), int(x)] * z_value -4)/8) * 8)
                        ))

        elif generate_images:
            cv2.drawContours(output_image, [contour],
                             -1, (0, 255, 0), 1)
    if generate_images:
        cv2.imwrite(f'depth_map/faces/top_{file_num}.png', output_image)
    return sorted(insets)


def generate(n=1543, done=804): # part 41855
    with open('./api/database/new_parts.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for index, row in track(enumerate(reader), total=n):
            if index < done:
                continue
            print(index)
            generate_top_bottom_insets(row['part_num'])
            if index == n:
                break


def generate_top_bottom_insets(file_num: str):
    bottom = depth_map_bottom(file_num)
    top = depth_map_top(file_num)

    folder_path = f"depth_map/csv/{file_num}"
    os.makedirs(folder_path, exist_ok=True)

    file_name = f"{folder_path}/{file_num}_bot.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(bottom)
    
    file_name = f"{folder_path}/{file_num}_top.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(top)


# generate()
