from pymongo import MongoClient
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


def add_track_db(name, track, thumbnail, user_id=None):
    model_document = {
        'name': name,
        'track': track,
        'thumbnail': thumbnail,
    }

    tracks.insert_one(model_document)


def get_track_db(name):
    result = tracks.find_one({'name': name})
    return result


if __name__ == "__main__":
    # add_models('./gltf')
    get_model('2926', "./../others")