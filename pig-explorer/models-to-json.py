import json
import os
import sys
from collections import OrderedDict


def show_usage():
    print 'usage: python model-to-json.py <pig.json>'

def models_to_json(filename):
    if not os.path.isfile(filename):
        print filename + ' not found'

    with open(filename, 'rb') as models_file:
        models = json.load(models_file, object_pairs_hook = OrderedDict)

        folder = filename + '.models'
        if not os.path.exists(folder):
            os.makedirs(folder)

        real_id = 0
        excluded = []
        for id in range(0, models['num_polymodels']):
            if models['polymodels'][str(id)]['simpler_model'] != '0':
                excluded.append(int(models['polymodels'][str(id)]['simpler_model']))

            if id + 1 not in excluded:
                model = models['polymodels'][str(id)]

                model_file = os.path.join(folder, str(real_id)) + '.json'
                real_id += 1

                with open(model_file, 'w') as output:
                    json.dump(model, output)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        show_usage()
    else:
        model = models_to_json(sys.argv[1])
