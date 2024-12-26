import base64
import csv
from dataclasses import dataclass, asdict
import json
from math import ceil, floor
from pymongo import MongoClient
from bson import ObjectId
import os
import pandas as pd
from collections import Counter

client = MongoClient('mongodb://localhost:27017/')
db = client['LEGO']

models = db['Models']
tracks = db['Tracks']
sets = db['Sets']
reviews = db['Reviews']

instruction_steps = db['Instruction_steps']
instruction_models = db['Instruction_models']


models2 = db['Models_v2']
tracks2 = db['Tracks_v2']
sets2 = db['Sets_v2']
reviews2 = db['Reviews_v2']
instruction_steps2 = db['Instruction_steps_v2']
instruction_models2 = db['Instruction_models_v2']


models3 = db['Models_v3']
tracks3 = db['Tracks_v3']
sets3 = db['Sets_v3']
steps3 = db['Steps_v3']
reviews3 = db['Reviews_v3']


# ------------------------------------------------------------------------------------
# Utils
def _get_size(minimum, maximum):
    LENGTH = 20
    HEIGHT = 8          # +4 inset
    return [floor(abs(maximum[1] - minimum[1]) / LENGTH),
            floor(abs(maximum[0] - minimum[0]) / LENGTH),
            ceil((abs(maximum[2] - minimum[2]) - 4) / HEIGHT)
            ]


def _max_values():       # [48, 56, 39], dane z 12.24.24
    cursor = models3.find({}, {'size': 1})

    max_res = [0, 0, 0]
    for m in cursor:
        for i in range(3):
            if int(m['size'][i]) > max_res[i]:
                max_res[i] = int(m['size'][i])

    return max_res


def _load_depth_maps(part_num: str):
    base_path = "/home/tomek/Documents/lego_pd/depth_map/csv"

    bot_file = os.path.join(base_path, f"{part_num}/{part_num}_bot.csv")
    top_file = os.path.join(base_path, f"{part_num}/{part_num}_top.csv")

    with open(bot_file, mode='r') as bot_csv:
        reader = csv.reader(bot_csv)
        insets_bot = [list(map(int, row)) for row in reader]

    with open(top_file, mode='r') as top_csv:
        reader = csv.reader(top_csv)
        insets_top = [list(map(int, row)) for row in reader]

    return insets_top, insets_bot


# Models
def add_models_v3():
    descriptions = pd.read_csv('./new_parts_without_wheels.csv')

    for i, row in descriptions.iterrows():
        part_num = row['part_num']
        category = row['part_cat_id']
        description = row['name']
        print(f"{i}/{len(descriptions)}")

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

        document = {
            'model': part_num,
            'file': content,
            'description': description,
            'category': category,
            'thumbnail': thumbnail_base64,
            'size': _get_size(minimum, maximum),
            'min': minimum,
            'max': maximum,
            'insets_top': top,
            'insets_bot': bot,
        }

        models3.insert_one(document)


def get_model_v3(name: str):
    model = models3.find_one({'model': name}, {"file": 1})

    if model:
        file_content = model['file']
        return file_content
    else:
        print(f"Model {name} not found.")


def get_model_v3_metadata(name: str):
    model = models3.find_one({'model': name},
                             {"insets_top": 1, "insets_bot": 1, "min": 1, "max": 1})
    return model


def get_thumbnails_v3(name: str = "", category: str = "",
                      size: list[int] = [0, 0, 0], limit: int = 20):
    filters = {}
    if name:
        filters['description'] = {'$regex': name, '$options': 'i'}
    if category:
        filters['category'] = {'$regex': category}
    if size:
        for i in range(3):
            if size[i] != 0:
                filters[f'size.{i}'] = size[i]

    models = models3.find(filters, {'thumbnail': 1, 'model': 1})
    result = []
    for r in models[:limit]:
        r['_id'] = str(r['_id'])
        result.append(r)
    return result


# Tracks
def add_track_v3(name: str, track, thumbnail,
                 user_id: str, set_id: str = None):
    model_document = {
        'name': name,
        'track': track,
        'thumbnail': thumbnail,
        'user_id': user_id,
    }

    if set_id is not None:
        model_document['set_id'] = set_id

    tracks3.insert_one(model_document)


def get_all_tracks_v3(user_id):
    result = tracks3.find({'user_id': user_id}, {'_id': 1, 'thumbnail': 1, 'name': 1})
    documents_list = []
    for document in result:
        document['_id'] = str(document['_id'])
        documents_list.append(document)
    return documents_list


def get_track_v3(id: str):
    return tracks3.find_one({'_id': ObjectId(id)}, {'track': 1, '_id': 0})


def add_review(set_id: str, comment: str, rating: int, user_id):
    model_document = {
        'set_id': set_id,
        'comment': comment,
        'rating': rating,
        'user_id': user_id,
    }

    reviews3.insert_one(model_document)


def get_reviews_for_set(set_id: str):
    result = reviews3.find({'set_id': set_id}, {'comment': 1, 'rating': 1, 'user_id': 1})
    return result


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
    set_id: str
    step: int
    thumbnail: str
    models: list[ModelDB]
    connections: list[ConnectionDB]


def add_instruction(name: str, user_id: str,
                    steps: list[StepDB]):
    model_document = {
        'name': name,
        'user_id': user_id,
        'thumbnail': steps[-1].thumbnail,
    }

    set_inserted = sets3.insert_one(model_document)

    connection_documents = []

    for index, step in enumerate(steps):
        connection_document = {
            'thumbnail': step.thumbnail,
            'set_id': set_inserted._id,
            'step': index,
            'models': json.dumps([asdict(model)for model in step.models]),
            'connections': json.dumps([asdict(connection)for connection in step.connections]),
        }
        connection_documents.append(connection_document)

    if connection_documents:
        steps3.insert_many(connection_documents)


def get_step(set_id: int, step: int):
    step_result = steps3.find_one({'set_id': set_id, 'step': step})

    return step_result.models, step_result.connections


def get_step_models(set_id: int, step: int):
    """
    Returns models and thumbnail of given step of instruction.
    """
    step_result = steps3.find_one({'set_id': set_id, 'step': step})
    c = Counter((model['name'], model['color']) for model in step_result.models)

    return [{"name": model[0], "color": model[1], "count": count} for model, count in c.items()], step_result.thumbnail


if __name__ == "__main__":
    print(_max_values())
    # add_models_v3()
