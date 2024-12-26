from dataclasses import dataclass
import numpy as np
from pprint import pprint
from collections import defaultdict

from database.mongodb import get_model_v3_metadata

LENGTH = 20
HEIGHT = 8


@dataclass
class Model:
    name: str
    gltf: str
    middle: list
    minimum: list
    rotation: list
    map_top: list
    map_bot: list

    def get_insertions(self) -> tuple[list, list]:
        """
        Computes the insets in world location from
        part world location and saved depth map.

        Returns:
          Tuple with 2 lists representing top and bottom
          insets positions.
        """
        offset = np.array(
            [self.middle[0]+self.minimum[0],
             self.middle[1]+self.minimum[1],
             self.middle[2]+self.minimum[2]]
        )

        print(self.map_top)

        result_top = [
            point+offset for point in self.map_top
        ]

        result_bot = [
            point+offset for point in self.map_bot
        ]

        result_top_array = np.array(result_top)
        result_bot_array = np.array(result_bot)

        result_top_array = self.apply_rotation(result_top_array)
        result_bot_array = self.apply_rotation(result_bot_array)

        return result_top_array, result_bot_array

    def _get_rotation_matrix(self):
        """
        Computes the 3D rotation matrix based on the object's rotation angles.

        Returns:
            np.ndarray: A 3x3 rotation matrix representing
            the cumulative rotation.
        """
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

    def apply_rotation(self, points: list):
        """
        Applies a 3D rotation to a set of points
        based on the object's rotation.

        Returns:
            np.ndarray: The rotated points with the same shape as the input.
        """
        rotation_matrix = self._get_rotation_matrix()
        points_rotated = points.reshape(-1, 3)

        for i in range(points_rotated.shape[0]):
            point = points_rotated[i]
            point_rotated = np.dot(rotation_matrix, point - self.middle) \
                + self.middle
            points_rotated[i] = point_rotated

        return points_rotated.reshape(points.shape)

    @staticmethod
    def from_json(scene: list[dict]) -> list['Model']:
        models = []
        for model in scene:
            model_name = model['gltfPath']
            minimum, _, map_top, map_bot = _get_metadata(model_name)
            models.append(Model(model['name'],
                                model['gltfPath'],
                                model['position'],
                                minimum,
                                model['rotation'],
                                map_top,
                                map_bot))
        return models


def _get_metadata(model_name: str):
    model = get_model_v3_metadata(model_name)
    return model['min'], model['max'], model['insets_top'], model['insets_bot']


def check_connection(models: list[dict]) -> dict[str, list]:
    """
    Returns dict of model_id and list of list of insets [top, bot].
    """
    points = defaultdict(list)
    for model in Model.from_json(models):
        top, bot = model.get_insertions()
        if top is not None or bot is not None:  # TODO check if needed
            points[model.name] = [top, bot]
    return points


def get_models_connection(scene: dict[str, list]):
    """
    Returns dict [model_name: models_names_connected_to_key]
    """
    # słownik model_name -> pojedyńcze połączenie
    models = check_connection(scene.models)

    # TODO może to usprawnić żeby faktycznie korzystało z top i bottom
    coordinate_map = defaultdict(list)

    for model_name, coordinates in models.items():
        if len(coordinates[0]) and len(coordinates[1]):
            coordinates = np.concatenate((coordinates[0], coordinates[1]))
        elif not len(coordinates[1]):
            coordinates = coordinates[0]
        else:
            coordinates = coordinates[1]
        down = np.min(coordinates[:, 2])
        for coord_set in coordinates.reshape(-1, 3):
            key = tuple(coord_set)
            coordinate_map[key].append((model_name, int(down)))

    pprint(coordinate_map)

    # model_name -> połączonego do niego modele
    graph = defaultdict(set)

    for models_with_same_coords in coordinate_map.values():
        for i in range(len(models_with_same_coords)):
            for j in range(i + 1, len(models_with_same_coords)):
                graph[models_with_same_coords[i]].add(
                    models_with_same_coords[j])
                graph[models_with_same_coords[j]].add(
                    models_with_same_coords[i])

    return models, graph


def find_connected_groups(scene) -> list[tuple[str, int]]:
    models, graph = get_models_connection(scene)

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
    unconnected_models = all_model_names - set(
        model for model, _ in graph.keys())
    for model in unconnected_models:
        groups.append([(model, 0)])

    print(groups)

    return groups


# TODO temporary to delete only showing insets positions
def connection_for_api(scene) -> dict:
    points = check_connection(scene.models)

    result = []
    for _, point in points.items():
        for x in point[0].reshape(-1, 3).tolist():
            result.append({'point': x, 'color': 'blue'})
        for x in point[1].reshape(-1, 3).tolist():
            result.append({'point': x, 'color': 'blue'})

    return result
