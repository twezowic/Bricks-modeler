import base64
from dataclasses import dataclass
import json
from math import ceil, floor
from pprint import pprint
from pymongo import MongoClient
from bson import ObjectId
import os
import pandas as pd

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


def add_models(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'r') as file:
            content = file.read()

        document = {
            'model': file_name.split('.')[0],
            'file': content
        }

        models.insert_one(document)


def get_model(model_name):
    document = models.find_one({'model': model_name})

    if document:
        file_content = document['file']
        return file_content
    else:
        print(f"Model {model_name} not found.")


# deprecated ^------------------------------------------------------------------------------^

def add_track(name, track, thumbnail, user_id=0, set_id=None):
    model_document = {
        'name': name,
        'track': track,
        'thumbnail': thumbnail,
        'user_id': user_id,
    }

    tracks.insert_one(model_document)


def get_all_tracks(user_id):
    result = tracks.find({'user_id': user_id}, {'_id': 1, 'thumbnail': 1, 'name': 1})
    documents_list = []
    for document in result:
        document['_id'] = str(document['_id'])
        documents_list.append(document)
    return documents_list


def get_track(id):
    return tracks.find_one({'_id': ObjectId(id)}, {'track': 1, '_id': 0})



def add_set(name, thumbnail, user_id=None):
    model_document = {
        'name': name,
        'thumbnail': thumbnail,
        'user_id': user_id,
    }

    sets.insert_one(model_document)


def add_review(set_id, comment: str, rating: int, user_id=None):
    model_document = {
        'set_id': set_id,
        'comment': comment,
        'rating': rating,
        'user_id': user_id,
    }

    reviews.insert_one(model_document)


def get_reviews_for_set(set_id=None):             
    result = reviews.find({'set_id': set_id}, {'comment': 1, 'rating': 1, 'user_id': 1})
    return result


# połączenie z instruction_models oraz sets później
def add_instruction_step(up_mask, up_model_id, down_mask, down_model_id, set_id=0, step_number=1):
    model_document = {
        'set_id': set_id,
        'step': step_number,
        'up_mask': up_mask,
        'up_model_id': up_model_id,
        'down_mask': down_mask,
        'down_model_id': down_model_id
    }
    instruction_steps.insert_one(model_document)


def add_instruction_model(model):
    model_document = {
        # 'set_id': set_id,
        # 'step': step_number,
        'model_id': model.model_id,
        'name': model.name,
        'color': model.color
    }
    instruction_models.insert_one(model_document)


@dataclass
class StepDB:
    up_mask: str
    up_id: str
    down_mask: str
    down_id: str


def temp_add_whole_instruction(steps: list[StepDB], models):
    for step in steps:
        add_instruction_step(step.up_mask, step.up_id, step.down_mask, step.down_id)
    for model in models:
        add_instruction_model(model)


def get_current_steps(set_id=0, step=1):
    steps = instruction_steps.find({'set_id': set_id, 'step': {'$lte': step}},
                                   {'up_mask': 1, 'up_model_id': 1, 'down_mask': 1, "down_model_id": 1})
    unique_model_ids = set()
    steps_list = []
    for step in steps:
        unique_model_ids.add(step['up_model_id'])
        unique_model_ids.add(step['down_model_id'])

        step['_id'] = str(step['_id'])
        steps_list.append(step)

    models = instruction_models.find({'model_id': {'$in': list(unique_model_ids)}},
                                     {'model_id': 1, 'name': 1, 'color': 1})
    models_list = []
    for document in models:
        document['_id'] = str(document['_id'])
        models_list.append(document)

    return models_list, steps_list

# -----------------------------------------------------------------------------------------------------


def _get_size(minimum, maximum):
    LENGTH = 20
    HEIGHT = 8          # +4 inset
    return [floor(abs(maximum[1] - minimum[1]) / LENGTH),
            floor(abs(maximum[0] - minimum[0]) / LENGTH),
            ceil((abs(maximum[2] - minimum[2]) - 4) / HEIGHT)
            ]


def add_models_v2():
    descriptions = pd.read_csv('./new_parts.csv')                  

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

        document = {
            'model': part_num,
            'file': content,
            'description': description,
            'category': category,
            'thumbnail': thumbnail_base64,
            'size': _get_size(minimum, maximum),
            'min': minimum,
            'max': maximum,
            # inset_positions: [] przez depth map
        }

        models2.insert_one(document)


def get_thumbnails_v2(name: str = "", category: str = "", size: list[int] = [0, 0, 0], limit: int = 20):
    filters = {}
    if name:
        filters['description'] = {'$regex': name, '$options': 'i'}
    if category:
        filters['category'] = {'$regex': category}
    if size:
        for i in range(3):
            if size[i] != 0:
                filters[f'size.{i}'] = size[i]
    print(filters)

    models = models2.find(filters, {'thumbnail': 1, 'model': 1})
    result = []
    for r in models[:limit]:
        r['_id'] = str(r['_id'])
        result.append(r)
    return result


def get_models_v2(name: str):
    model = models2.find_one({'model': name}, {"file": 1})

    if model:
        file_content = model['file']
        return file_content
    else:
        print(f"Model {name} not found.")


def add_track_v2(name, track, thumbnail, user_id, set_id=None):
    model_document = {
        'name': name,
        'track': track,
        'thumbnail': thumbnail,
        'user_id': user_id,
    }
    if set_id:
        model_document['set_id'] = set_id

    tracks2.insert_one(model_document)


def get_all_tracks_v2(user_id):
    result = tracks2.find({'user_id': user_id}, {'_id': 1, 'thumbnail': 1, 'name': 1})
    documents_list = []
    for document in result:
        document['_id'] = str(document['_id'])
        documents_list.append(document)
    return documents_list


def get_track_v2(id):
    return tracks2.find_one({'_id': ObjectId(id)}, {'track': 1, '_id': 0})


def _max_values():       # [48, 56, 49], dane z 12.11.24
    cursor = models2.find({}, {'size': 1})

    max_res = [0, 0, 0]
    for m in cursor:
        for i in range(3):
            if int(m['size'][i]) > max_res[i]:
                max_res[i] = int(m['size'][i])

    return max_res


if __name__ == "__main__":
    # add_models('./gltf')
    # get_model('2926')
    # add_models_v2()
    print(_max_values())