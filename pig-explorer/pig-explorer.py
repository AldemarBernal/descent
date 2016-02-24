import json
import os
import pprint
import struct
import sys
from collections import OrderedDict
from io import BytesIO


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
    print 'usage: python pig-explorer.py <file.pig>'


def explore(filename):
    if not os.path.isfile(filename):
        print filename + ' not found'

    else:
        #polymodel data offset
        offset = 0xF13A - 8
        max_submodels = 10
        pig_dict = OrderedDict()
        pp = pprint.PrettyPrinter(indent = 4)

        with open(filename, 'rb') as pig:
            original_pig_addr = read_integer(pig)

            pig.read(offset)

            pig_dict['num_polymodels'] = read_integer(pig)
            pig_dict['polymodels'] = OrderedDict()
            models_raw = OrderedDict()

            for pm_index in range(0, pig_dict['num_polymodels']):
                polymodel = OrderedDict()

                polymodel['num_models'] = read_integer(pig)
                polymodel['model_data_size'] = read_integer(pig)
                polymodel['model_data'] = read_integer(pig)

                polymodel['submodel'] = OrderedDict()
                polymodel['submodel']['ptrs'] = read_integers(pig, max_submodels)
                polymodel['submodel']['offsets'] = read_vectors(pig, max_submodels)
                polymodel['submodel']['norms'] = read_vectors(pig, max_submodels)
                polymodel['submodel']['pnts'] = read_vectors(pig, max_submodels)
                polymodel['submodel']['rads'] = read_integers(pig, max_submodels)
                polymodel['submodel']['parents'] = read_bytes(pig, max_submodels)
                polymodel['submodel']['mins'] = read_vectors(pig, max_submodels)
                polymodel['submodel']['maxs'] = read_vectors(pig, max_submodels)

                polymodel['mins'] = read_vector(pig)
                polymodel['maxs'] = read_vector(pig)
                polymodel['rad'] = read_integer(pig)
                polymodel['num_textures'] = read_byte(pig)
                polymodel['first_texture'] = read_short(pig)
                polymodel['simpler_model'] = read_byte(pig)

                pig_dict['polymodels'][pm_index] = polymodel

            for pm_index in range(0, pig_dict['num_polymodels']):
                models_raw[pm_index] = pig.read(pig_dict['polymodels'][pm_index]['model_data_size'])

            counts = {0: 0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0}

            for pm_index in range(0, pig_dict['num_polymodels']):
#                print(pig_dict['polymodels'][pm_index])
                md = OrderedDict()
                mdr = BytesIO(models_raw[pm_index])
#                md = parse_idta(mdr)
#                pig_dict['polymodels'][pm_index]['model_data'] = md

                for submodel in range(0, pig_dict['polymodels'][pm_index]['num_models']):
                    md[submodel] = parse_idta(mdr, pig_dict['polymodels'][pm_index]['submodel']['ptrs'][submodel])

                pig_dict['polymodels'][pm_index]['model_data'] = md

        return pig_dict


def read_byte(file):
    return struct.unpack('<B', file.read(1))[0]

def read_short(file):
    return struct.unpack('<h', file.read(2))[0]

def read_integer(file):
    return struct.unpack('<i', file.read(4))[0]

def read_vector(file):
    vector = OrderedDict()
    vector['x'] = read_integer(file)
    vector['y'] = read_integer(file)
    vector['z'] = read_integer(file)
    return vector

def read_bytes(file, max_submodels):
    dict = OrderedDict()
    for index in range(0, max_submodels):
        dict[index] = read_byte(file)

    return dict

def read_shorts(file, max_submodels):
    dict = OrderedDict()
    for index in range(0, max_submodels):
        dict[index] = read_short(file)

    return dict

def read_integers(file, max_submodels):
    dict = OrderedDict()
    for index in range(0, max_submodels):
        dict[index] = read_integer(file)

    return dict

def read_vectors(file, max_submodels):
    dict = OrderedDict()
    for index in range(0, max_submodels):
        dict[index] = read_vector(file)

    return dict

def parse_idta(mdr, offset = 0, level = ''):
    md = OrderedDict()
    md_index = 0
    pp = pprint.PrettyPrinter(indent = 4)

    mdr.seek(offset)
    idta = read_short(mdr)

    while idta != IDTA_EOF:
        md[md_index] = OrderedDict()
        md[md_index]['idta'] = idta

        if idta == IDTA_DEFPOINTS:
            md[md_index]['num_points'] = read_short(mdr)
            md[md_index]['vms_points'] = read_vectors(mdr, md[md_index]['num_points'])

        elif idta == IDTA_FLATPOLY:
            md[md_index]['num_points'] = read_short(mdr)
            md[md_index]['vms_vector'] = read_vector(mdr)
            md[md_index]['vms_normal'] = read_vector(mdr)
            md[md_index]['color_map'] = read_short(mdr)
            md[md_index]['pltdx'] = read_shorts(mdr, md[md_index]['num_points'])

            if md[md_index]['num_points'] % 2 == 0:
                md[md_index]['pad'] = read_short(mdr)

        elif idta == IDTA_TMAPPOLY:
            md[md_index]['num_points'] = read_short(mdr)
            md[md_index]['vms_vector'] = read_vector(mdr)
            md[md_index]['vms_normal'] = read_vector(mdr)
            md[md_index]['texture'] = read_short(mdr)
            md[md_index]['pltdx'] = read_shorts(mdr, md[md_index]['num_points'])

            if md[md_index]['num_points'] % 2 == 0:
                md[md_index]['pad'] = read_short(mdr)

            md[md_index]['uvl_vectors'] = read_vectors(mdr, md[md_index]['num_points'])

        elif idta == IDTA_SORTNORM:
            md[md_index]['num_points'] = read_short(mdr)
            md[md_index]['vms_vector'] = read_vector(mdr)
            md[md_index]['vms_normal'] = read_vector(mdr)
            md[md_index]['z_front'] = read_short(mdr)
            md[md_index]['z_back'] = read_short(mdr)

            old_offset = mdr.tell()
            md[md_index]['z_front_nodes'] = parse_idta(mdr, offset + md[md_index]['z_front'], level + '+')
            mdr.seek(old_offset)

            old_offset = mdr.tell()
            md[md_index]['z_back_nodes'] = parse_idta(mdr, offset + md[md_index]['z_back'], level + '+')
            mdr.seek(old_offset)

        elif idta == IDTA_RODBM:
            md[md_index]['bmp_num'] = read_short(mdr)
            md[md_index]['vms_top_point'] = read_vector(mdr)
            md[md_index]['bot_width'] = read_integer(mdr)
            md[md_index]['vms_bottom_point'] = read_vector(mdr)
            md[md_index]['top_width'] = read_integer(mdr)

        elif idta == IDTA_SUBCALL:
            md[md_index]['suboject_num'] = read_short(mdr)
            md[md_index]['vms_start_point'] = read_vector(mdr)
            md[md_index]['offset'] = read_short(mdr)
            md[md_index]['pad'] = read_integer(mdr)

            old_offset = mdr.tell()
            md[md_index]['subcall'] = parse_idta(mdr, offset + md[md_index]['offset'], level + '+')
            mdr.seek(old_offset)

            #print('//%.5f, %.5f, %.5f,' % (float(md[md_index]['vms_start_point']['x']) / 100000, float(md[md_index]['vms_start_point']['y']) / 100000, float(md[md_index]['vms_start_point']['z']) / 100000,))

        elif idta == IDTA_DEFP_START:
            md[md_index]['num_points'] = read_short(mdr)
            md[md_index]['former_points'] = read_short(mdr)
            md[md_index]['pad'] = read_short(mdr)
            md[md_index]['vms_points'] = read_vectors(mdr, md[md_index]['num_points'])

            #print('// ' + level + ' - ' + str(md[md_index]['former_points']))
            #for key, value in md[md_index]['vms_points'].iteritems():
            #    print('%.5f, %.5f, %.5f,' % (float(value['x']) / 100000, float(value['y']) / 100000, float(value['z']) / 100000,))


        elif idta == IDTA_GLOW:
            md[md_index]['glow_value'] = read_short(mdr)

        else:
            raise Exception('oops')

        offset = mdr.tell()
        idta = read_short(mdr)
        md_index += 1

    return md


if __name__ == "__main__":

    if len(sys.argv) < 2:
        show_usage()
    else:
        pig = explore(sys.argv[1])

        with open(sys.argv[1] + '.json', 'w') as output:
            json.dump(pig, output)
