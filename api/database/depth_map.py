import csv
import json
from math import ceil, floor
import random
import numpy as np
import cv2
from rich.progress import track

import trimesh

LENGTH = 20


# check if sum of area of triangles creted from given point is equal to triangle
def is_point_in_triangle(px, py, A, B, C):
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

    if c == 0:  # represent as line
        return max([A[2], B[2], C[2]])

    return -(a * x + b * y + d) / c


def is_circle(contour):
    (x, y), radius = cv2.minEnclosingCircle(contour)
    x, y, w, h = cv2.boundingRect(contour)
    
    aspect_ratio = w / h

    return (
        0.8 <= aspect_ratio <= 1.2 and
        20 <= radius <= 40
    )



# później brane z bazy danych ma być tylko min i max bo tutaj inaczej zaokrąglam ceil zamiast floor
def get_size(file_name: str):
    with open(file_name) as fh:
        model = json.loads(fh.read())
        minimum = model['accessors'][0]['min']
        maximum = model['accessors'][0]['max']
        size = [ceil(abs(floor(minimum[0]) - floor(maximum[0]))),
                ceil(abs(floor(minimum[1]) - floor(maximum[1])))]
    return size


def depth_map_from_faces(file_num: int, a=None, b=None):
    file_name = f'./api/database/gltf/{file_num}.gltf'

    size = get_size(file_name)

    mesh = trimesh.load(file_name)

    # mesh.show()

    vertices = np.array(mesh.geometry[f'{file_num}-Mesh'].vertices)
    faces = np.array(mesh.geometry[f'{file_num}-Mesh'].faces)

    # tworzenie odpowiedniego rozmiaru mapy
    width, height = size
    width *= 4
    height *= 4
    depth_map = np.full((height, width), -np.inf)

    # znormalizowanie vertexów na mapę
    max_coords = np.max(vertices, axis=0)
    min_coords = np.min(vertices, axis=0)

    vertices = (vertices - min_coords) / (max_coords - min_coords)

    vertices[:, 0] = width * vertices[:, 0] - 1
    vertices[:, 1] = height - 1 - (height * vertices[:, 1])  # sprawdzić czy na pewno w bazie też jest odwrócone


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
                    depth_map[y, x] = max(depth_map[y, x], calculate_z(x, y, p1, p2, p3))

    # normalizacja mapy
    depth_map[np.isinf(depth_map)] = 0
    depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)

    depth_map_normalized = depth_map_normalized.astype(np.uint8)

    equalized_image = cv2.equalizeHist(depth_map_normalized)

    # # zwiększenie kontrastu
    sobelx = cv2.Sobel(equalized_image, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(equalized_image, cv2.CV_64F, 0, 1, ksize=5)

    gradient_magnitude = cv2.magnitude(sobelx, sobely)

    gradient_magnitude_normalized = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX)
    gradient_magnitude_normalized = gradient_magnitude_normalized.astype(np.uint8)
    

    # _, binary_image = cv2.threshold(gradient_magnitude_normalized, 100, 255, cv2.THRESH_BINARY)
    # binary_image = cv2.Canny(gradient_magnitude_normalized, 50, 150)

    output_image = cv2.cvtColor(depth_map_normalized.astype(np.uint8), cv2.COLOR_GRAY2BGR)
    
    counter = 0
    # wyznaczanie krawędzi
    contours, _ = cv2.findContours(gradient_magnitude_normalized, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:

        if is_circle(contour):
            # (x, y), _ = cv2.minEnclosingCircle(contour) 
            cv2.drawContours(output_image, [contour],
                                            -1, (0, 0, 255), 1)
            counter += 1
        else: 
             cv2.drawContours(output_image, [contour],
                                            -1, (0, 255, 0), 1)

    # insets_coordinates = []
    # half_length = 10
    # # wyznaczanie wypustek
    # for x in range(0, int(width / half_length)-1):
    #     for y in range(0, int(height / half_length)-1):
    #         # print(x, y)
    #         top_left_x = x * half_length
    #         top_left_y = y * half_length
            
    #         bottom_right_x = top_left_x + LENGTH
    #         bottom_right_y = top_left_y + LENGTH
            
    #         square = gradient_magnitude_normalized[
    #             top_left_y:bottom_right_y,
    #             top_left_x:bottom_right_x
    #         ]

    # np.savetxt(f'depth_map/{file_num}.csv', depth_map_normalized, fmt='%d')
    # print(f"{file_num}: {insets_coordinates} {counter}")
    cv2.imwrite(f'depth_map/faces/x/{file_num}.png', output_image)




# for a in range(-10, 10):
#     depth_map_from_faces(file_num, a)


def generate(n=1543):
    with open('./api/database/new_parts.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for index, row in track(enumerate(reader), total=n):
            depth_map_from_faces(row['part_num'])
            if index == n:
                break
        

# generate(200)
depth_map_from_faces("24201")

# jak rozwiązać że środek tak naprawde to 4 punkty -> jak było do tej pory?
