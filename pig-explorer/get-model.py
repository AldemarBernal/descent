import json
import md5
import os
import sys


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
        models = json.load(models_file)

        for id in range(0, 50):
            model = models['polymodels'][str(id)]

            points = parse_idta(model['model_data'])
            print('models:' + str(model['num_models']) + '-' + str(len(points)))
#        print(points)

#        for md in points:
#            print md5.new(json.dumps(md)).hexdigest()
#            print md

def parse_idta(model, hashes = []):
    points = []
    more_points = None

    for key, md in model.iteritems():
        idta = md['idta']

        if idta == IDTA_DEFPOINTS:
            pass
        elif idta == IDTA_FLATPOLY:
            pass
        elif idta == IDTA_TMAPPOLY:
            pass
        elif idta == IDTA_SORTNORM:
            for pts in parse_idta(md['z_front_nodes'], hashes):
                points.append(pts)

            for pts in parse_idta(md['z_back_nodes'], hashes):
                points.append(pts)

        elif idta == IDTA_RODBM:
            pass
        elif idta == IDTA_SUBCALL:

            for pts in parse_idta(md['subcall'], hashes):
                points.append(pts)

        elif idta == IDTA_DEFP_START:
            md5_points = md5.new(json.dumps(md)).hexdigest()
            if md5_points not in hashes:
                hashes.append(md5_points)
                points.append(md['vms_points'])

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
