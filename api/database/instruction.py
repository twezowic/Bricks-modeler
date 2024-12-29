from dataclasses import dataclass
import numpy as np
from database.mongodb import get_step
from pprint import pprint
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
    # symetrie sprawdzać przez np.rot90(a, n= 1 | 2 | 3 ) to chyba i tak w sprawdzaniu?
    maska1 = np.zeros(coords1.shape[0], dtype=bool)
    maska2 = np.zeros(coords2.shape[0], dtype=bool)

    coords2_flat = coords2.reshape(-1, coords2.shape[-1])

    for i in range(coords1.shape[0]):
        if any(np.all(coords1[i] == p) for p in coords2_flat):
            maska1[i] = True

    coords1_flat = coords1.reshape(-1, coords1.shape[-1])

    for i in range(coords2.shape[0]):
        if any(np.all(coords2[i] == p) for p in coords1_flat):
            maska2[i] = True

    return maska1, maska2


def prepare_step(scene):
    models, graph = get_models_connection(scene)
    instruction_connections = []
    for key, values in graph.items():
        height = key[1]
        for model_name, model_height in values:
            if model_height > height:
                maska1, maska2 = get_masks(models[key[0]][0], models[model_name][1])

                flatten_mask_1 = ''.join(maska1.astype(int).astype(str).flatten())
                flatten_mask_2 = ''.join(maska2.astype(int).astype(str).flatten())

                instruction_connections.append(ConnectionDB(flatten_mask_1, key[0], flatten_mask_2, model_name))
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


def compare_instruction_step(scene,
                             set_id: str, step: int):
    current_models, current_connections = prepare_step(scene)
    instruction_models, instruction_connections = get_step(set_id, step)

    if len(current_connections) != len(instruction_connections) or \
       len(current_models) != len(instruction_models):
        return False
    
    print(instruction_connections)

    instruction_db_models = [ModelDB(model['model_id'], model['color'], model['name']) for model in instruction_models]
    instruction_db_steps = [ConnectionDB(connection['up_mask'], connection['up_id'], connection['down_mask'], connection['down_id']) for connection in instruction_connections]

    models1 = {model.model_id: model for model in instruction_db_models}
    models2 = {model.model_id: model for model in current_models}

    pprint(current_models)
    print()
    pprint(current_connections)
    print()
    pprint(instruction_db_models)
    print()
    pprint(instruction_db_steps)

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
    
    # Sprawdzanie czy maski odpowiadają
    steps1 = {
        (step.up_id, step.down_id): step for step in instruction_db_steps
    }
    steps2 = {
        (step.up_id, step.down_id): step for step in current_connections
    }

    return steps1 == steps2
