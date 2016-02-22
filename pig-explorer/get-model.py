import json
import os
import sys


def show_usage():
    print 'usage: python get-model.py <pig.json> <model-number>'

def get_model(filename, id):
    if not os.path.isfile(filename):
        print filename + ' not found'

    with open(filename, 'rb') as models_file:
        models = json.load(models_file)
        model = models['polymodels'][id]

        print(json.dumps(model['model_data'], indent = 4))

if __name__ == "__main__":

    if len(sys.argv) < 3:
        show_usage()
    else:
        model = get_model(sys.argv[1], sys.argv[2])
