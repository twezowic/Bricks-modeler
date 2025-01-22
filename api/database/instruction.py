import numpy as np
from database.mongodb import get_step
import networkx as nx
from database.connection import get_models_connection
from database.models import ConnectionDB, ModelDB


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


def _replace_id(steps: list[ConnectionDB], old: str, new: str):
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


def compare_masks(instruction_db_steps: list[ConnectionDB],
                  current_connections: list[ConnectionDB]) -> bool:
    def matches(con1: ConnectionDB, con2: ConnectionDB):
        return (
            (con1.up_mask == con2.up_mask or is_symmetry(con1.up_mask, con2.up_mask)) and
            (con1.down_mask == con2.down_mask or is_symmetry(con1.down_mask, con2.down_mask)) and
            con1.up_id == con2.up_id and
            con1.down_id == con2.down_id
        )

    for con1 in instruction_db_steps:
        found = False
        for con2 in current_connections:
            if matches(con1, con2):
                found = True
                break
        if not found:
            return False

    return True


def compare_instruction_step(scene, set_id: str, step: int):
    current_models, current_connections = prepare_step(scene)
    instruction_models, instruction_connections = get_step(set_id, step)

    if len(current_connections) != len(instruction_connections) or \
       len(current_models) != len(instruction_models):
        return False

    instruction_models = [ModelDB(model['model_id'],
                                  model['color'],
                                  model['name'])
                          for model in instruction_models]
    instruction_connections = [ConnectionDB(connection['up_mask'],
                                            connection['up_id'],
                                            connection['down_mask'],
                                            connection['down_id'])
                               for connection in instruction_connections]

    def node_matcher(node1, node2):
        return (
            node1['color'] == node2['color'] and
            node1['name'] == node2['name']
        )

    G1 = nx.DiGraph()
    edges1 = _prepare_edges(instruction_connections)
    for model in instruction_models:
        G1.add_node(model.model_id, color=model.color, name=model.name)
    G1.add_edges_from(edges1)

    G2 = nx.DiGraph()
    edges2 = _prepare_edges(current_connections)
    for model in current_models:
        G2.add_node(model.model_id, color=model.color, name=model.name)
    G2.add_edges_from(edges2)

    matcher = nx.isomorphism.DiGraphMatcher(G1, G2, node_match=node_matcher)
    if matcher.is_isomorphic():
        mapping = matcher.mapping
        for v1, v2 in mapping.items():
            _replace_id(current_connections, v2, v1)
    else:
        return False

    return compare_masks(instruction_connections, current_connections)
