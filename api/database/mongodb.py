import json
from math import ceil
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

models2 = db['Models_v2']
tracks2 = db['Tracks_v2']
sets2 = db['Sets_v2']
reviews2 = db['Reviews_v2']


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


def add_track(name, track, thumbnail, user_id=0):
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


def _get_size(minimum, maximum):
    LENGTH = 20
    HEIGHT = 8          # +4 inset
    return [ceil((maximum[0] - minimum[0]) / LENGTH), ceil((maximum[1] - minimum[0]) / LENGTH), ceil(((maximum[2] - minimum[2]) - 4) / HEIGHT)]


def new_add_models(folder_path):
    descriptions = pd.read_csv('./parts/parts.csv')                  
    thumbnails = pd.read_csv('./parts/inventory_parts.csv')          
    directory = os.listdir(folder_path)
    without_thumbnail = []
    for i, file_name in enumerate(directory):
        print(f"{i}/{len(directory)}")
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'r') as file:
            content = file.read()

        part_num = file_name.split('.')[0]

        description = descriptions[descriptions['part_num'] == part_num]['name'].values[0]
        thumbnail = thumbnails[thumbnails['part_num'] == part_num]['img_url'].values
        if len(thumbnail) == 0:
            without_thumbnail.append(part_num)
            continue
        metadata = json.loads(content)
        minimum = metadata['accessors'][0]['min']
        maximum = metadata['accessors'][0]['max']

        document = {
            'model': part_num,
            'file': content,
            'description': description,
            'thumbnail': thumbnail[0],
            'size': _get_size(minimum, maximum),
            'min': minimum,
            'max': maximum,
            # inset_postions: [] przez depth map
        }

        models2.insert_one(document)
        pprint(without_thumbnail)


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


def get_reviews_for_set(set_id=None):               # JOIN na tabeli użytkownika jak będę miał
    result = reviews.find({'set_id': set_id}, {'comment': 1, 'rating': 1, 'user_id': 1})
    return result


if __name__ == "__main__":
    # add_models('./gltf')
    # get_model('2926')
    new_add_models("./gltf")
