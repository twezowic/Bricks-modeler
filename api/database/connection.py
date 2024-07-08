import json
import re
from dataclasses import dataclass
import numpy as np
from pprint import pprint
import csv
from collections import Counter
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
            result_top[:, : , 2] = top
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
            # points.append((model.name, connect))
            for point in connect:
                points.extend(point)
    return points



# scene = [{"name":"model-0","gltfPath":"3062b","position":[10,10,48],"rotation":[0,0,0],"color":"#63452c"},{"name":"model-1","gltfPath":"3062b","position":[10,10,72],"rotation":[0,0,0],"color":"#63452c"},{"name":"model-2","gltfPath":"3062b","position":[10,10,96],"rotation":[0,0,0],"color":"#63452c"},{"name":"model-3","gltfPath":"3062b","position":[10,10,24],"rotation":[0,0,0],"color":"#63452c"},{"name":"model-4","gltfPath":"30176","position":[10,10,120],"rotation":[0,0,0],"color":"#26a269"},{"name":"model-5","gltfPath":"30176","position":[10,10,144],"rotation":[0,0,-3.141592653589793],"color":"#26a269"},{"name":"model-7","gltfPath":"3003","position":[-30,-60,24],"rotation":[0,0,0],"color":"#f6d32d"},{"name":"model-9","gltfPath":"4865a","position":[-40,-60,48],"rotation":[0,0,1.5707963267948966],"color":"#f6d32d"},{"name":"model-10","gltfPath":"3069b","position":[-20,-60,32],"rotation":[0,0,-1.5707963267948966],"color":"#f6d32d"},{"name":"model-13","gltfPath":"2343","position":[-20,-20,40],"rotation":[0,0,0],"color":"#a51d2d"}]
# points = check_connection(scene)
# pprint(points)


def connection_for_api(scene) -> dict:
    points = check_connection(scene.models)

    result = []
    points = [tuple(point) for point in points]
    counter = Counter(points)
    for point in counter.keys():
        if counter[point] == 1:
            color = 'blue'
        else:
            color = 'red'
        result.append({'point': point, 'color': color})
    return result
