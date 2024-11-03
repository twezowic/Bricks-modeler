import json
from dataclasses import dataclass
import numpy as np
from pprint import pprint
from collections import defaultdict
from math import floor

from database.mongodb import get_model

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
        result = np.stack([result_bottom, result_top])
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
            print(minimum)
            print(maximum)
            print()
            height = (maximum[2] - minimum[2]) // HEIGHT
            size = [floor(abs(minimum[1] - maximum[1])/LENGTH), floor(abs(minimum[0] - maximum[0])/LENGTH)]
            models.append(Model(model['name'], model['position'], minimum, maximum, model['rotation'], size, height))
        return models

def get_metadata(model_name):
    model = json.loads(get_model(model_name))
    minimum = model['accessors'][0]['min']
    maximum = model['accessors'][0]['max']
    return minimum, maximum


def check_connection(models) -> dict[str, list]:
    points = defaultdict(list)
    for model in Model.from_json(models):
        connect = model.get_insertions()
        if connect is not None:
            points[model.name] = connect
    return points


@dataclass
class ModelDB:
    model_id: str
    color: str
    name: str

    @staticmethod
    def from_scene(scene, model_id):
        print(scene.models)
        color, name = next((model['gltfPath'], model['color']) for model in scene.models if model['name'] == model_id)
        return ModelDB(model_id, color, name)
    

@dataclass
class StepDB:
    step_id: int
    mask_up: str
    up_id: str
    mask_down: str
    down_id: str
    # instruction_step


def get_masks(coords1, coords2):
    # symetrie sprawdzać przez np.rot90(a, n= 1 | 2 | 3 )
    maska1 = np.zeros(coords1.shape[:2], dtype=bool)
    maska2 = np.zeros(coords2.shape[:2], dtype=bool)

    coords2_flat = coords2.reshape(-1, coords2.shape[-1])
    for i in range(coords1.shape[0]):
        for j in range(coords1.shape[1]):
            punkt = coords1[i, j]

            if any(np.all(punkt == p) for p in coords2_flat):
                maska1[i, j] = True

    coords1_flat = coords1.reshape(-1, coords1.shape[-1])
    for i in range(coords2.shape[0]):
        for j in range(coords2.shape[1]):
            punkt = coords2[i, j]

            if any(np.all(punkt == p) for p in coords1_flat):
                maska2[i, j] = True

    return maska1, maska2

def find_connected_groups(scene) -> list[tuple[str, int]]:

    pprint(scene)
    # dict model_name -> wszystkie możliwe połączenia
    models = check_connection(scene.models)

    pprint(models)

    # słownik model_name -> pojedyńcze połączenie
    coordinate_map = defaultdict(list)

    for model_name, coordinates in models.items():
        down = np.min(coordinates[:, :, :, 2])
        for coord_set in coordinates.reshape(-1, 3):
            key = tuple(coord_set)
            coordinate_map[key].append((model_name, int(down)))

    pprint(coordinate_map)

    # model_name -> połączonego do niego modele
    graph = defaultdict(set)

    for models_with_same_coords in coordinate_map.values():
        for i in range(len(models_with_same_coords)):
            for j in range(i + 1, len(models_with_same_coords)):
                graph[models_with_same_coords[i]].add(models_with_same_coords[j])
                graph[models_with_same_coords[j]].add(models_with_same_coords[i])

    pprint(graph)

    instruction_steps = []
    instruction_models = []
    for key, values in graph.items():
        height = key[1]
        for model_name, model_height in values:
            if model_height > height:
                maska1, maska2 = get_masks(models[key[0]][1], models[model_name][0])

                pprint(maska1)
                flatten_mask_1 = ''.join(maska1.astype(int).astype(str).flatten())
                pprint(flatten_mask_1)
                print()

                pprint(maska2)
                flatten_mask_2 = ''.join(maska2.astype(int).astype(str).flatten())
                pprint(flatten_mask_2)
                print()

                instruction_models.append(ModelDB.from_scene(scene, key[0]))
                instruction_steps.append((flatten_mask_1, flatten_mask_2, key[0], model_name))
    pprint(instruction_models)
    pprint(instruction_steps)
            
    # Depth first-search
    # Do otrzymania grup połączeń
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

    # dodaje modele nie połączone
    all_model_names = {model_name for model_name in models.keys()}
    unconnected_models = all_model_names - set(model for model, _ in graph.keys())
    for model in unconnected_models:
        groups.append([(model, 0)])

    print(groups)

    return groups
