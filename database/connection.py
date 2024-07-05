import json
import re
from dataclasses import dataclass
import numpy as np

from mysqldb import get_part_description
from mongodb import get_model


LENGTH = 20

@dataclass
class Insertion:
    positions: list     # 4 pozycje wokół wypustki

    @staticmethod
    def from_corner(position):  # brac po uwage jakos kąt
        positions = []
        for i in range(2):
            for j in range(2):
                positions.append([position[0]+20*i, position[1]+20*j])
        return Insertion(positions)
    
    def __eq__(self, value: object) -> bool:        # pozniej brac pod uwage pozycje poziomie tylko a pionowe w zasięgu pewnym
        for position in self.positions:
            if position not in value.positions:
                return False
        return True

@dataclass
class Model:
    middle: list
    minimum: list
    size: list

    def dimensions(self):
        return len(self.size)
    
    def get_insertions(self):
        result = np.zeros(tuple(self.size) + (2,), dtype=int)
        if self.dimensions() == 2:
            half_x = self.size[0] / 2
            half_y = self.size[1] / 2

            for i in range(self.size[1]):
                for j in range(self.size[0]):
                    result[j, i, 1] = int(self.middle[1] - 20 * half_x + j * 20)
                    result[j, i, 0] = int(self.middle[0] - 20 * half_y + i * 20)
                    
        elif self.dimensions() == 3:
            ...
        else:
            raise Exception
        return result

def check_size(model_name):
    desc = get_part_description(model_name)
    pattern = r"(\d{1,2}(\d+)?(?: x \d{1,2}(\d+)?){1,2})"

    result = re.search(pattern, desc)
    if result:
        dimensions = result.group(1)

        return [int(dim) for dim in dimensions.split(' x ')]
    else:
        print("No dimensions")


def get_metadata(model_name):
    model = json.loads(get_model(model_name))
    minimum = model['accessors'][0]['min']
    maximum = model['accessors'][0]['max']
    return minimum, maximum


def check_connection(file):
    with open(file) as fh:
        scene = json.load(fh)['models']
    models = []
    for model in scene:
        model_name = str(model['gltfPath'])   # to powinien zawsze być string trzeba poprawić w frontendzie
        models.append(Model(model['position'], get_metadata(model_name)[0], check_size(model_name)))
        # model['rotation']
    
    points = []
    for model in models:
        points.append(model.get_insertions())
    return points
    

# check_connection("scene.json")
points = check_connection('database/scene.json')

# print(points)


def find_same_positions(arrays):
    result = []

    for idx1, arr1 in enumerate(arrays):
        for idx2, arr2 in enumerate(arrays):
            if idx1 >= idx2:
                continue
            for elem1 in arr1[0]:
                for elem2 in arr2[0]:
                    if np.array_equal(elem1, elem2):
                        model_nr1 = idx1
                        model_nr2 = idx2
                        result.append((model_nr1, model_nr2, elem1))
    return result

results = find_same_positions(points)

for model_nr1, model_nr2, position1 in results:
    print(f"Model {model_nr1} and {model_nr2}")
    print(points[model_nr1])

