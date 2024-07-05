import json
import re

from mysqldb import get_part_description
from mongodb import get_model

def check_size(model_name):
    desc = get_part_description(model_name)
    pattern = r"(\d{1,2}(\.\d+)?(?: x \d{1,2}(\.\d+)?){1,2})"

    result = re.search(pattern, desc)
    if result:
        dimensions = result.group(1)

        return [float(dim) for dim in dimensions.split(' x ')]
    else:
        print("No dimensions")


def get_metadata(model_name):
    model = json.loads(get_model(model_name))
    minimum = model['accessors'][0]['min']
    maximum = model['accessors'][0]['max']
    return minimum, maximum


def check_connection(file, model_name):
    with open(file) as fh:
        scene = json.load(fh)['models']
    ...
    

# check_connection("scene.json")

print(get_metadata("3460"))