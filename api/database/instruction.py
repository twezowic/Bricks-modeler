from dataclasses import dataclass
import numpy as np
from database.mongodb import get_step
import networkx as nx
from database.connection import get_models_connection


@dataclass
class ModelDB:
    model_id: str
    color: str
    name: str

    @staticmethod
    def from_scene(scene: list[dict]) -> list['ModelDB']:
        result = []
        for model in scene:
            result.append(ModelDB(model['name'],
                                  model['color'],
                                  (model['gltfPath'])))
        return result

    def __eq__(self, value: 'ModelDB'):
        return all([
            self.color == value.color,
            self.name == value.name
        ])


@dataclass
class ConnectionDB:
    up_mask: str
    up_id: str
    down_mask: str
    down_id: str

    def __eq__(self, value: 'ConnectionDB'):
        return all([
            self.up_mask == value.up_mask,
            self.up_id == value.up_id,
            self.down_mask == value.down_mask,
            self.down_id == value.down_id,
        ])

    def __hash__(self):
        return hash((self.up_mask, self.up_id, self.down_mask, self.down_id))


@dataclass
class StepDB:
    set_id: str
    step: int
    thumbnail: str
    models: list[ModelDB]
    connections: list[ConnectionDB]


def get_masks(coords1, coords2):
    coords1 = np.array(coords1)
    coords2 = np.array(coords2)

    unique_x1, unique_y1 = np.unique(coords1[:, 0]), np.unique(coords1[:, 1])
    unique_x2, unique_y2 = np.unique(coords2[:, 0]), np.unique(coords2[:, 1])

    mask1 = np.zeros((len(unique_y1), len(unique_x1)), dtype=int)
    mask2 = np.zeros((len(unique_y2), len(unique_x2)), dtype=int)

    # wartość: pozycja w tabeli
    index_map1_x = {val: idx for idx, val in enumerate(unique_x1)}
    index_map1_y = {val: idx for idx, val in enumerate(unique_y1)}
    index_map2_x = {val: idx for idx, val in enumerate(unique_x2)}
    index_map2_y = {val: idx for idx, val in enumerate(unique_y2)}

    for coord in coords1:
        x_idx = index_map1_x[coord[0]]
        y_idx = index_map1_y[coord[1]]
        if any(np.all(coord == c) for c in coords2):
            mask1[y_idx, x_idx] = 1

    for coord in coords2:
        x_idx = index_map2_x[coord[0]]
        y_idx = index_map2_y[coord[1]]
        if any(np.all(coord == c) for c in coords1):
            mask2[y_idx, x_idx] = 1

    return mask1, mask2


def prepare_step(scene):
    models, graph = get_models_connection(scene)
    instruction_connections = []
    for key, values in graph.items():
        height = key[1]
        for model_name, model_height in values:
            if model_height > height:
                mask1, mask2 = get_masks(models[key[0]][0], models[model_name][1])
                instruction_connections.append(ConnectionDB(mask1.tolist(), key[0], mask2.tolist(), model_name))
    return ModelDB.from_scene(scene.models if not isinstance(scene, list) else scene), instruction_connections


def _prepare_edges(steps: list[ConnectionDB]):
    edges = []
    for step in steps:
        edges.append((step.up_id, step.down_id))
    return edges


def _replace_id(steps: list[ConnectionDB], old: str, new: str) -> list[ConnectionDB]:
    for step in steps:
        if step.down_id == old:
            step.down_id = new
        if step.up_id == old:
            step.up_id = new


def is_symmetry(mask1, mask2):
    mask1_np = np.array(mask1)
    mask2_np = np.array(mask2)

    is_equal_any_rotation = any(
        np.array_equal(mask2_np, np.rot90(mask1_np, k)) for k in range(1, 4)
    )

    return is_equal_any_rotation


def compare_masks(instruction_db_steps: list[ConnectionDB], current_connections: list[ConnectionDB]):
    for con1, con2 in zip(instruction_db_steps, current_connections):
        if con1.up_mask != con2.up_mask and \
           not is_symmetry(con1.up_mask, con2.up_mask):
            return False
        if con1.down_mask != con2.down_mask and \
           not is_symmetry(con1.down_mask, con2.down_mask):
            return False
    return True


def compare_instruction_step(scene,
                             set_id: str, step: int):
    current_models, current_connections = prepare_step(scene)
    instruction_models, instruction_connections = get_step(set_id, step)

    if len(current_connections) != len(instruction_connections) or \
       len(current_models) != len(instruction_models):
        return False
    
    instruction_db_models = [ModelDB(model['model_id'], model['color'], model['name']) for model in instruction_models]
    instruction_db_steps = [ConnectionDB(connection['up_mask'], connection['up_id'], connection['down_mask'], connection['down_id']) for connection in instruction_connections]

    models1 = {model.model_id: model for model in instruction_db_models}
    models2 = {model.model_id: model for model in current_models}

    # pprint(current_models)
    # print()
    # pprint(current_connections)
    # print()
    # pprint(instruction_db_models)
    # print()
    # pprint(instruction_db_steps)

    G1 = nx.DiGraph()
    edges1 = _prepare_edges(instruction_db_steps)
    G1.add_edges_from(edges1)

    G2 = nx.DiGraph()
    edges2 = _prepare_edges(current_connections)
    G2.add_edges_from(edges2)

    matcher = nx.isomorphism.DiGraphMatcher(G1, G2)
    if matcher.is_isomorphic():
        mapping = matcher.mapping
        for v1, v2 in mapping.items():
            # Sprawdzanie koloru i typu elementu
            if models1[v1] != models2[v2]:
                return False
            # Przemiana w obecnych połączeniach id modeli na odpowiadające z instrukcji
            _replace_id(current_connections, v2, v1)
    else:
        return False

    return compare_masks(instruction_db_steps, current_connections)
