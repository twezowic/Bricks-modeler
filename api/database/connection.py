import json
import re
from dataclasses import dataclass
import numpy as np
from pprint import pprint
import csv
from collections import Counter, defaultdict
from math import pi

from database.mysqldb import get_part_description
from database.mongodb import get_model

# from mysqldb import get_part_description
# from mongodb import get_model


LENGTH = 20
HEIGHT = 8

@dataclass
class Model:
    name: str
    middle: list
    minimum: list
    maximum: list
    rotation: list
    size: list
    height: int


    def get_insertions(self):       # bierze środek
        if not self.size:       # pozniej cos z tym zrobic
            return
        if self.size:
            result_bottom = np.zeros(tuple(self.size) + (3,), dtype=int)
            half_x = self.size[0] / 2
            half_y = self.size[1] / 2

            bottom = self.middle[2] + self.minimum[2]
            top = bottom + self.height * HEIGHT
            result_bottom[:, :, 2] = bottom

            for i in range(self.size[1]):
                for j in range(self.size[0]):
                    result_bottom[j, i, 1] = int(self.middle[1] - 20 * half_x + j * 20+10)
                    result_bottom[j, i, 0] = int(self.middle[0] - 20 * half_y + i * 20+10)
            result_top = np.copy(result_bottom)
            result_top[:, :, 2] = top
            result = np.concatenate((result_bottom, result_top))

            result = self.apply_rotation(result)

        return result


    def get_rotation_matrix(self):
        angles = self.rotation
        cos_x, sin_x = np.cos(angles[0]), np.sin(angles[0])
        cos_y, sin_y = np.cos(angles[1]), np.sin(angles[1])
        cos_z, sin_z = np.cos(angles[2]), np.sin(angles[2])

        R_x = np.array([
            [1, 0, 0],
            [0, cos_x, -sin_x],
            [0, sin_x, cos_x]
        ])

        R_y = np.array([
            [cos_y, 0, sin_y],
            [0, 1, 0],
            [-sin_y, 0, cos_y]
        ])

        R_z = np.array([
            [cos_z, -sin_z, 0],
            [sin_z, cos_z, 0],
            [0, 0, 1]
        ])

        R = np.dot(R_z, np.dot(R_y, R_x))
        return R

    def apply_rotation(self, points):
        rotation_matrix = self.get_rotation_matrix()
        points_rotated = points.reshape(-1, 3)

        for i in range(points_rotated.shape[0]):
            point = points_rotated[i]
            point_rotated = np.dot(rotation_matrix, point - self.middle) + self.middle
            points_rotated[i] = point_rotated

        return points_rotated.reshape(points.shape)


    @staticmethod
    def from_json(scene):
        models = []
        for model in scene:
            model_name = model['gltfPath']
            minimum, maximum = get_metadata(model_name)
            height = (maximum[2] - minimum[2]) // HEIGHT
            models.append(Model(model['name'], model['position'], minimum, maximum, model['rotation'], check_size(model_name), height))
        return models

def check_size(model_name): # zawsze daje max 2 rozmiary
    desc = get_part_description(model_name)
    pattern = r"(\d{1,2}(\d+)?(?: x \d{1,2}(\d+)?){1})"

    result = re.search(pattern, desc)
    if result:
        dimensions = result.group(1)

        return [int(dim) for dim in dimensions.split(' x ')]
    else:
        return None


def get_metadata(model_name):
    model = json.loads(get_model(model_name))
    minimum = model['accessors'][0]['min']
    maximum = model['accessors'][0]['max']
    return minimum, maximum


def check_connection(scene):
    points = []
    for model in Model.from_json(scene):
        connect = model.get_insertions()
        if connect is not None:
            points.append((model.name, connect))
    return points


# zamienić żeby zwracało także grupy pojedyńcze
def find_connected_groups(scene):
    models = check_connection(scene.models)
    coordinate_map = defaultdict(list)

    for model_name, coordinates in models:
        for coord_set in coordinates.reshape(-1, coordinates.shape[-1]):
            key = tuple(coord_set)
            coordinate_map[key].append(model_name)

    graph = defaultdict(set)

    for models_with_same_coords in coordinate_map.values():
        for i in range(len(models_with_same_coords)):
            for j in range(i + 1, len(models_with_same_coords)):
                graph[models_with_same_coords[i]].add(models_with_same_coords[j])
                graph[models_with_same_coords[j]].add(models_with_same_coords[i])

    def dfs(model, visited):
        stack = [model]
        group = []

        while stack:
            current_model = stack.pop()
            if current_model not in visited:
                visited.add(current_model)
                group.append(current_model)
                stack.extend(graph[current_model] - visited)

        return group

    visited = set()
    groups = []

    for model in graph:
        if model not in visited:
            group = dfs(model, visited)
            groups.append(group)

    return groups
