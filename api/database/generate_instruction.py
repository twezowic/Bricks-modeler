from dataclasses import dataclass
from typing import List
from collections import defaultdict
from pprint import pprint


@dataclass
class ConnectionDB:
    up_mask: str
    up_id: str
    down_mask: str
    down_id: str


@dataclass
class ModelDB:
    model_id: str
    color: str
    name: str


@dataclass
class StepDB:
    step: int
    models: List[ModelDB]
    connections: List[ConnectionDB]


def generate_stepdb(models: List[ModelDB], connections: List[ConnectionDB]) -> List[StepDB]:
    outgoing_edges = defaultdict(list)
    incoming_edges = defaultdict(list)
    model_ids = {model.model_id for model in models}

    for conn in connections:
        outgoing_edges[conn.up_id].append(conn.down_id)
        incoming_edges[conn.down_id].append(conn.up_id)

    steps = []
    used_models = set()
    step_number = 0

    while model_ids:
        current_step_models = [model_id for model_id in model_ids if not outgoing_edges[model_id]]
        if not current_step_models:
            raise ValueError("Cycle detected in the graph!")

        current_step_connections = [
            conn for conn in connections
            if conn.down_id in current_step_models or conn.up_id in current_step_models
        ]

        steps.append(StepDB(
            step=step_number,
            models=[
                model for model in models if model.model_id in current_step_models
            ],
            connections=[
                conn for conn in current_step_connections if conn.down_id in current_step_models
            ]
        ))

        used_models.update(current_step_models)
        model_ids.difference_update(current_step_models)
        for model_id in current_step_models:
            for up_model in incoming_edges[model_id]:
                outgoing_edges[up_model].remove(model_id)

        step_number += 1

    return steps


if __name__ == "__main__":
    models = [
        ModelDB(model_id='model-9786401f-03d3-472b-9a29-837fea4d737b', color='#ff0000', name='3001'),
        ModelDB(model_id='model-fe1a85c0-629e-4e1b-8791-9d8136d60998', color='#ff0000', name='3001'),
        ModelDB(model_id='model-65478609-9013-4497-8905-7bb110527f72', color='#ff0000', name='3001'),
        ModelDB(model_id='model-8853a989-2269-4a15-91cd-ad2f576fd7ce', color='#ff0000', name='3001'),
        ModelDB(model_id='model-d4f22309-9cd0-4f57-877d-c3a551596ace', color='#ff0000', name='3001'),
        ModelDB(model_id='model-ba32ddef-78d2-4aac-b7fc-cb0573798b9b', color='#ff0000', name='3001'),
        ModelDB(model_id='model-abb3777f-0175-4808-b1be-cc23be5850d8', color='#ff0000', name='3003'),
        ModelDB(model_id='model-da8c34ae-295c-4f04-bd29-05a3807f8324', color='#ff0000', name='3003'),
        ModelDB(model_id='model-f12f872d-4dc4-4f82-8837-74282d47145a', color='#ff0000', name='30151'),
        ModelDB(model_id='model-d6d8f681-6e90-4e71-b5fc-2d90631070b5', color='#ff0000', name='30151')
    ]

    connections = [
        ConnectionDB(up_mask='00010001', up_id='model-9786401f-03d3-472b-9a29-837fea4d737b', down_mask='10001000', down_id='model-65478609-9013-4497-8905-7bb110527f72'),
        ConnectionDB(up_mask='01100110', up_id='model-9786401f-03d3-472b-9a29-837fea4d737b', down_mask='1111', down_id='model-abb3777f-0175-4808-b1be-cc23be5850d8'),
        ConnectionDB(up_mask='10001000', up_id='model-9786401f-03d3-472b-9a29-837fea4d737b', down_mask='00010001', down_id='model-fe1a85c0-629e-4e1b-8791-9d8136d60998'),
        ConnectionDB(up_mask='11001100', up_id='model-fe1a85c0-629e-4e1b-8791-9d8136d60998', down_mask='00110011', down_id='model-8853a989-2269-4a15-91cd-ad2f576fd7ce'),
        ConnectionDB(up_mask='00110011', up_id='model-fe1a85c0-629e-4e1b-8791-9d8136d60998', down_mask='11001100', down_id='model-ba32ddef-78d2-4aac-b7fc-cb0573798b9b'),
        ConnectionDB(up_mask='11110000', up_id='model-abb3777f-0175-4808-b1be-cc23be5850d8', down_mask='00110011', down_id='model-ba32ddef-78d2-4aac-b7fc-cb0573798b9b'),
        ConnectionDB(up_mask='00110011', up_id='model-65478609-9013-4497-8905-7bb110527f72', down_mask='11001100', down_id='model-d4f22309-9cd0-4f57-877d-c3a551596ace'),
        ConnectionDB(up_mask='11001100', up_id='model-65478609-9013-4497-8905-7bb110527f72', down_mask='1111', down_id='model-da8c34ae-295c-4f04-bd29-05a3807f8324'),
        ConnectionDB(up_mask='11001100', up_id='model-8853a989-2269-4a15-91cd-ad2f576fd7ce', down_mask='1111', down_id='model-f12f872d-4dc4-4f82-8837-74282d47145a'),
        ConnectionDB(up_mask='00110011', up_id='model-d4f22309-9cd0-4f57-877d-c3a551596ace', down_mask='1111', down_id='model-d6d8f681-6e90-4e71-b5fc-2d90631070b5')
    ]

    step_db_list = generate_stepdb(models, connections, set_id="example-set")

    for step in step_db_list:
        pprint(step)
