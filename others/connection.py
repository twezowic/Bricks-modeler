import json

def check_size(model_name):



def check_connection(file, model_name):
    with open(file) as fh:
        scene = json.load(fh)['models']
    ...
        


# check_connection("scene.json")

print(check_size("3460"))