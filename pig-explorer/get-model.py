import json
import os
import sys
from collections import OrderedDict


#IDTA constants
IDTA_EOF = 0
IDTA_DEFPOINTS = 1
IDTA_FLATPOLY = 2
IDTA_TMAPPOLY = 3
IDTA_SORTNORM = 4
IDTA_RODBM = 5
IDTA_SUBCALL = 6
IDTA_DEFP_START = 7
IDTA_GLOW = 8


def show_usage():
    print 'usage: python get-model.py <pig.json> <model-number>'


def get_model(filename, id):
    if not os.path.isfile(filename):
        print filename + ' not found'

    with open(filename, 'rb') as models_file:
        models = json.load(models_file, object_pairs_hook = OrderedDict)
        model = models['polymodels'][str(id)]

        for key in range(0, model['num_models']):
            md = model['model_data'][str(key)]
            points = parse_idta(md)

            print('//submodel: ' + str(key))
            for point in points:
                x = point['x'] + model['submodel']['offsets'][str(key)]['x']
                y = point['y'] + model['submodel']['offsets'][str(key)]['y']
                z = point['z'] + model['submodel']['offsets'][str(key)]['z']

                x = float(x) / 100000
                y = float(y) / 100000
                z = float(z) / 100000

                print('%.5f, %.5f, %.5f,' % (x, y, z))


def parse_idta(model):
    points = []
    more_points = None

    for key, md in model.iteritems():
        idta = md['idta']

        if idta == IDTA_DEFPOINTS:
            pass
        elif idta == IDTA_FLATPOLY:
            pass
        elif idta == IDTA_TMAPPOLY:
            for key_point, point in md['uvl_vectors'].iteritems():
                uvl = point
#                uvl['x'] += md['vms_vector']['x']
#                uvl['y'] += md['vms_vector']['y']
#                uvl['z'] += md['vms_vector']['z']

#                points.append(point)

            pass
        elif idta == IDTA_SORTNORM:
            for pts in parse_idta(md['z_front_nodes']):
                points.append(pts)

            for pts in parse_idta(md['z_back_nodes']):
                points.append(pts)

        elif idta == IDTA_RODBM:
            pass
        elif idta == IDTA_SUBCALL:

            for pts in parse_idta(md['subcall']):
                points.append(pts)

        elif idta == IDTA_DEFP_START:
            for key_point, point in md['vms_points'].iteritems():
                points.append(point)
#                pass

        elif idta == IDTA_GLOW:
            pass
        else:
            raise Exception('oops')

    return points


if __name__ == "__main__":

    if len(sys.argv) < 3:
        show_usage()
    else:
        model = get_model(sys.argv[1], sys.argv[2])
