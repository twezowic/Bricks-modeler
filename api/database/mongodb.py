from dataclasses import asdict
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
import pandas as pd
from collections import Counter
from database.models import ModelDB, TrackDB, CommentDB, SetDB, StepDB

client = MongoClient('mongodb://localhost:27017/')
db = client['LEGO']

models3 = db['Models_v3']
tracks3 = db['Tracks_v3']
sets3 = db['Sets_v3']
steps3 = db['Steps_v3']
comments3 = db['Comments_v3']


# ------------------------------------------------------------------------------------
# Utils


def _max_values():       # [48, 56, 39], dane z 12.24.24
    cursor = models3.find({}, {'size': 1})

    max_res = [0, 0, 0]
    for m in cursor:
        for i in range(3):
            if int(m['size'][i]) > max_res[i]:
                max_res[i] = int(m['size'][i])

    return max_res


# Models
def add_models_v3():
    descriptions = pd.read_csv('./new_parts.csv')

    for i, row in descriptions.iterrows():
        model = ModelDB.create(row)
        models3.insert_one(asdict(model))


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
# ------------------------------------------------------------------------------------


# Tracks
def add_track_v3(name: str, track, thumbnail,
                 user_id: str,
                 set_id: Optional[str] = None,
                 step: Optional[int] = None):
    model = TrackDB(name, track, thumbnail, user_id, set_id, step)

    tracks3.insert_one(asdict(model))


def get_all_tracks_v3(user_id):
    result = tracks3.find({'user_id': user_id}, {'_id': 1, 'thumbnail': 1, 'name': 1})
    documents_list = []
    for document in result:
        document['_id'] = str(document['_id'])
        documents_list.append(document)
    return documents_list


def get_track_v3(id: str):
    return tracks3.find_one({'_id': ObjectId(id)}, {'track': 1, '_id': 0, 'set_id': 1, 'step': 1})


def update_track(id: str, track, thumbnail, step):
    updated_fields = {'track': track, 'thumbnail': thumbnail}

    if step is not None:
        updated_fields['step'] = step

    tracks3.update_one(
        {'_id': ObjectId(id)},
        {'$set': updated_fields}
    )
# ------------------------------------------------------------------------------------


# Comments
def add_comment(set_id: str, comment: str, user_id):
    model = CommentDB(set_id, comment, user_id)

    comments3.insert_one(asdict(model))


def get_comments_for_set(set_id: str):
    result = comments3.find({'set_id': set_id}, {'comment': 1, 'rating': 1, 'user_id': 1, '_id': 0})
    return list(result)
# ------------------------------------------------------------------------------------


# Sets
def add_instruction(name: str, user_id: str,
                    steps: list[StepDB]):
    model = SetDB(name, user_id)

    set_inserted = sets3.insert_one(asdict(model))

    connection_documents = []

    for index, step in enumerate(steps):
        connection_document = {
            'set_id': set_inserted.inserted_id,
            'step': index,
            'models': [asdict(model)for model in step.models],
            'connections': [asdict(connection)for connection in step.connections],
        }
        connection_documents.append(connection_document)

    if connection_documents:
        steps3.insert_many(connection_documents)

    return str(set_inserted.inserted_id)


def add_instruction_to_set(set_id, thumbnails):
    sets3.update_one(
        {'_id': ObjectId(set_id)},
        {'$set': {'thumbnail': thumbnails[-1]}}
    )
    for index, thumbnail in enumerate(thumbnails):
        steps3.update_one(
            {'set_id': ObjectId(set_id), 'step': index},
            {'$set': {'instruction': thumbnail}}
        )


def get_instruction(set_id: str):
    instruction = steps3.find({'set_id': ObjectId(set_id)}, {'step': 1, 'instruction': 1})

    result = []
    for step in instruction:
        result.append({'instruction': step['instruction'], 'step': step['step']})

    return result


def get_step(set_id: str, step: int):
    steps_results = steps3.find({'set_id': ObjectId(set_id), 'step': {'$lte': step}})

    models = []
    connections = []

    # Łączymy modele i połączenia z każdego kroku
    for step_result in steps_results:
        models.extend(step_result['models'])
        connections.extend(step_result['connections'])

    return models, connections


def get_step_models(set_id: int, step: int):
    """
    Returns models of given step of instruction, including their thumbnails.
    """
    step_result = steps3.find_one({'set_id': ObjectId(set_id), 'step': step})

    c = Counter((model['name'], model['color']) for model in step_result['models'])

    result = []
    for (name, color), count in c.items():
        model_data = models3.find_one({'model': name}, {"thumbnail": 1})
        thumbnail = model_data['thumbnail'] if model_data else None

        result.append({
            "model": name,
            "color": color,
            "count": count,
            "thumbnail": thumbnail
        })

    return result


def get_sets(page_index, page_size=10):
    skip_count = page_index * page_size

    total_count = sets3.count_documents({})

    total_pages = (total_count + page_size - 1) // page_size

    sets = sets3.find({}).skip(skip_count).limit(page_size)

    result = []
    for set_thumbnails in sets:
        set_thumbnails['_id'] = str(set_thumbnails['_id'])
        result.append(set_thumbnails)

    return {
        "data": result,
        "total_pages": total_pages
    }


def get_sets_from_user(user_id: str):
    sets = sets3.find({'user_id': user_id})

    result = []
    for set_thumbnails in sets:
        set_thumbnails['_id'] = str(set_thumbnails['_id'])
        result.append(set_thumbnails)

    return result
# ------------------------------------------------------------------------------------


if __name__ == "__main__":
    print(_max_values())
    # add_models_v3()
