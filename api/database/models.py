from dataclasses import dataclass


@dataclass
class ConnectionDB:
    up_mask: list
    up_id: str
    down_mask: list
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
class StepDB:
    step: int
    models: list[ModelDB]
    connections: list[ConnectionDB]
    set_id: str = None
    thumbnail: str = None
