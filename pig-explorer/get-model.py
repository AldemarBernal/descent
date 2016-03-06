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

        former_points = 0
        idx = 0

        for key in range(0, model['num_models']):
            md = model['model_data'][str(key)]
            points = parse_idta_points(md)
            indexes = parse_idta_indexes(md)

            print('//submodel: ' + str(key))
            print('//vertices')
            for point in points:
                x = point['x'] + model['submodel']['offsets'][str(key)]['x']
                y = point['y'] + model['submodel']['offsets'][str(key)]['y']
                z = point['z'] + model['submodel']['offsets'][str(key)]['z']

                x = float(x) / 65536.0
                y = float(y) / 65536.0
                z = float(z) / 65536.0

                print('\t\t\tnew Vector3(%.5ff, %.5ff, %.5ff),' % (x, y, z))

            print('//triangles')
            for index in indexes:
#                point = points[index - former_points]

                print('\t\t\ttriangles[' + str(idx) + '] = ' + str(index) + ';')
                idx += 1


            former_points += len(points)

def parse_idta_points(model):
    points = []

    for key, md in model.iteritems():
        idta = md['idta']

        if idta == IDTA_DEFPOINTS:
            pass

        elif idta == IDTA_FLATPOLY:
            pass

        elif idta == IDTA_TMAPPOLY:
            pass

        elif idta == IDTA_SORTNORM:
            for pts in parse_idta_points(md['z_front_nodes']):
                points.append(pts)

            for pts in parse_idta_points(md['z_back_nodes']):
                points.append(pts)

        elif idta == IDTA_RODBM:
            pass

        elif idta == IDTA_SUBCALL:
            for pts in parse_idta_points(md['subcall']):
                points.append(pts)

        elif idta == IDTA_DEFP_START:
            for key_point, point in md['vms_points'].iteritems():
                points.append(point)

        elif idta == IDTA_GLOW:
            pass

        else:
            raise Exception('oops')

    return points

def parse_idta_indexes(model):
    indexes = []

    for key, md in model.iteritems():
        idta = md['idta']

        if idta == IDTA_DEFPOINTS:
            pass

        elif idta == IDTA_FLATPOLY:
            if len(md['pltdx']) == 3:
                for index in md['pltdx'].itervalues():
                    indexes.append(index)
            elif len(md['pltdx']) == 4:
                indexes.append(md['pltdx']["0"])
                indexes.append(md['pltdx']["1"])
                indexes.append(md['pltdx']["2"])

                indexes.append(md['pltdx']["0"])
                indexes.append(md['pltdx']["1"])
                indexes.append(md['pltdx']["3"])

                indexes.append(md['pltdx']["0"])
                indexes.append(md['pltdx']["2"])
                indexes.append(md['pltdx']["3"])

                indexes.append(md['pltdx']["1"])
                indexes.append(md['pltdx']["2"])
                indexes.append(md['pltdx']["3"])

            idx = 0
            for index in md['pltdx'].itervalues():
                if idx < 3:
#                    indexes.append(index)
                    idx += 1

        elif idta == IDTA_TMAPPOLY:
            if len(md['pltdx']) == 3:
                for index in md['pltdx'].itervalues():
                    indexes.append(index)
            elif len(md['pltdx']) == 4:
                indexes.append(md['pltdx']["0"])
                indexes.append(md['pltdx']["1"])
                indexes.append(md['pltdx']["2"])

                indexes.append(md['pltdx']["0"])
                indexes.append(md['pltdx']["1"])
                indexes.append(md['pltdx']["3"])

                indexes.append(md['pltdx']["0"])
                indexes.append(md['pltdx']["2"])
                indexes.append(md['pltdx']["3"])

                indexes.append(md['pltdx']["1"])
                indexes.append(md['pltdx']["2"])
                indexes.append(md['pltdx']["3"])


            idx = 0
            for index in md['pltdx'].itervalues():
                if idx < 3:
#                    indexes.append(index)
                    idx += 1

        elif idta == IDTA_SORTNORM:
            for index in parse_idta_indexes(md['z_front_nodes']):
                indexes.append(index)

            for index in parse_idta_indexes(md['z_back_nodes']):
                indexes.append(index)

        elif idta == IDTA_RODBM:
            pass

        elif idta == IDTA_SUBCALL:
            for index in parse_idta_indexes(md['subcall']):
                indexes.append(index - last_num_models)

        elif idta == IDTA_DEFP_START:
                pass

        elif idta == IDTA_GLOW:
            pass

        else:
            raise Exception('oops')

    return indexes


if __name__ == "__main__":

    if len(sys.argv) < 3:
        show_usage()
    else:
        model = get_model(sys.argv[1], sys.argv[2])
