from dataclasses import dataclass
from typing import Optional
import base64
import json
import os
import csv
from math import floor, ceil


def _load_depth_maps(part_num: str):
    base_path = "./depth_map/csv"

    bot_file = os.path.join(base_path, f"{part_num}/{part_num}_bot.csv")
    top_file = os.path.join(base_path, f"{part_num}/{part_num}_top.csv")

    with open(bot_file, mode='r') as bot_csv:
        reader = csv.reader(bot_csv)
        insets_bot = [list(map(int, row)) for row in reader]

    with open(top_file, mode='r') as top_csv:
        reader = csv.reader(top_csv)
        insets_top = [list(map(int, row)) for row in reader]

    return insets_top, insets_bot


def _get_size(minimum, maximum):
    LENGTH = 20
    HEIGHT = 8          # +4 inset
    return [floor(abs(maximum[1] - minimum[1]) / LENGTH),
            floor(abs(maximum[0] - minimum[0]) / LENGTH),
            ceil((abs(maximum[2] - minimum[2]) - 4) / HEIGHT)
            ]


@dataclass
class ModelDB:
    model: str
    file: str
    description: str
    category: str
    thumbnail: str
    size: list
    min: list
    max: list
    insets_top: list
    insets_bot: list

    @staticmethod
    def create(row):
        part_num = row['part_num']
        category = row['part_cat_id']
        description = row['name']

        gltf_file_path = os.path.join("./gltf", f"{part_num}.gltf")

        with open(gltf_file_path, 'r') as file:
            content = file.read()

        thumbnail_path = os.path.join("./thumbnails", f"{part_num}.png")

        with open(thumbnail_path, 'rb') as img_file:
            thumbnail = img_file.read()
        thumbnail_base64 = base64.b64encode(thumbnail).decode('utf-8')

        metadata = json.loads(content)
        minimum = metadata['accessors'][0]['min']
        maximum = metadata['accessors'][0]['max']

        top, bot = _load_depth_maps(part_num)

        return ModelDB(
            part_num,
            content,
            description,
            category,
            thumbnail_base64,
            _get_size(minimum, maximum),
            minimum,
            maximum,
            top,
            bot,
        )


@dataclass
class TrackDB:
    name: str
    track: list
    thumbnail: str
    user_id: str
    set_id: Optional[str] = None
    step: Optional[int] = None


@dataclass
class CommentDB:
    set_id: str
    comment: str
    user_id: str


@dataclass
class SetDB:
    name: str
    user_id: str


@dataclass
class InstructionConnectionDB:
    up_mask: list
    up_id: str
    down_mask: list
    down_id: str

    def __eq__(self, value: 'InstructionConnectionDB'):
        return all([
            self.up_mask == value.up_mask,
            self.up_id == value.up_id,
            self.down_mask == value.down_mask,
            self.down_id == value.down_id,
        ])

    def __hash__(self):
        return hash((self.up_mask, self.up_id, self.down_mask, self.down_id))


@dataclass
class InstructionModelDB:
    model_id: str
    color: str
    name: str

    @staticmethod
    def from_scene(scene: list[dict]) -> list['InstructionModelDB']:
        result = []
        for model in scene:
            result.append(InstructionModelDB(model['name'],
                          model['color'],
                          (model['gltfPath'])))
        return result

    def __eq__(self, value: 'InstructionModelDB'):
        return all([
            self.color == value.color,
            self.name == value.name
        ])


@dataclass
class StepDB:
    step: int
    models: list[InstructionModelDB]
    connections: list[InstructionConnectionDB]
    set_id: str = None
    thumbnail: str = None
