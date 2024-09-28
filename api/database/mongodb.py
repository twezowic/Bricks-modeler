from pymongo import MongoClient
from bson import ObjectId
import os

client = MongoClient('mongodb://localhost:27017/')
db = client['LEGO']
models = db['Models']
tracks = db['Tracks']


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


def get_all_tracks(user_id=None):
    result = tracks.find({}, {'_id': 1, 'thumbnail': 1, 'name': 1})
    documents_list = []
    for document in result:
        document['_id'] = str(document['_id'])
        documents_list.append(document)
    return documents_list


def get_track(id):
    return tracks.find_one({'_id': ObjectId(id)}, {'track': 1, '_id': 0})


if __name__ == "__main__":
    add_models('./gltf')
    # get_model('2926')
