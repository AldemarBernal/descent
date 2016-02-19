import os
import pprint
import struct
import sys


def show_usage():
    print 'usage: python pig-explorer.py <file.pig>'


def explore(filename):
    if not os.path.isfile(filename):
        print filename + ' not found'

    else:
        #polymodel data offset
        offset = 0xF13A - 8
        max_submodels = 10
        pig_dict = {}
        pp = pprint.PrettyPrinter(indent = 4)

        with open(filename, 'rb') as pig:
            original_pig_addr = read_integer(pig)

            pig.read(offset)

            pig_dict['num_polymodels'] = read_integer(pig)
            print(pig_dict['num_polymodels'])
            pig_dict['polymodels'] = {}

            for pm_index in range(0, pig_dict['num_polymodels']):
                polymodel = {}

                polymodel['num_models'] = read_integer(pig)
                polymodel['model_data_size'] = read_integer(pig)
                polymodel['model_data'] = read_integer(pig)

                polymodel['submodel'] = {}
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
                pig_dict['polymodels'][pm_index]['model_data'] = pig.read(pig_dict['polymodels'][pm_index]['model_data_size'])




#            pp.pprint(pig_dict)
            print(hex(pig.tell()))
#            pp.pprint(read_vectors(pig, 10))

#            pp.pprint(pig_dict['polymodels'][0]['model_data'])
            counts = {0: 0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}

            for pm_index in range(0, pig_dict['num_polymodels']):
                print(pm_index)

#                print(pig_dict['polymodels'][pm_index]['model_data'][:4])

                counts[struct.unpack('<h', pig_dict['polymodels'][pm_index]['model_data'][:2])[0]] += 1

                model_data = pig_dict['polymodels'][pm_index]['model_data']
                mi = 0

                if (struct.unpack('<h', model_data[:2])[0] == 7):
                    print('DEFP_START')
                    print('id:')
                    print(struct.unpack('<h', model_data[mi:2])[0])
                    mi += 2
                    print('n_points:')
                    points = struct.unpack('<h', model_data[mi:mi + 2])[0]
                    print(struct.unpack('<h', model_data[mi:mi + 2])[0])
                    mi += 2
                    print('former_pts:')
                    print(struct.unpack('<h', model_data[mi:mi + 2])[0])
                    mi += 2
                    print('pad:')
                    print(struct.unpack('<h', model_data[mi:mi + 2])[0])
                    mi += 2

                    x = 0
                    y = 0
                    z = 0

                    for point in range(0, points):
                        vector = {}
                        vector['x'] = struct.unpack('<i', model_data[mi:mi + 4])[0]
                        mi += 4
                        vector['y'] = struct.unpack('<i', model_data[mi:mi + 4])[0]
                        mi += 4
                        vector['z'] = struct.unpack('<i', model_data[mi:mi + 4])[0]
                        mi += 4

                        #pp.pprint(vector)
#                        print '%.5f, %.5f, %.5f,' % (x, y, z)

                        x += float(vector['x']) / 100000
                        y += float(vector['y']) / 100000
                        z += float(vector['z']) / 100000

#                        print '%.5f, %.5f, %.5f,' % (x, y, z)

#                        print str(x) + ', ' + str(y), ', ' + str(z)

                print('next: ' + str(struct.unpack('<h', model_data[mi:mi + 2])[0]))
                mi += 2

            pp.pprint(counts)




def read_byte(file):
    return struct.unpack('<B', file.read(1))[0]

def read_short(file):
    return struct.unpack('<h', file.read(2))[0]

def read_integer(file):
    return struct.unpack('<i', file.read(4))[0]

def read_vector(file):
    return {
        'x': read_integer(file),
        'y': read_integer(file),
        'z': read_integer(file)}

def read_bytes(file, max_submodels):
    dict = {}
    for index in range(0, max_submodels):
        dict[index] = read_byte(file)

    return dict

def read_integers(file, max_submodels):
    dict = {}
    for index in range(0, max_submodels):
        dict[index] = read_integer(file)

    return dict

def read_vectors(file, max_submodels):
    dict = {}

    for index in range(0, max_submodels):
        dict[index] = read_vector(file)

    return dict


if __name__ == "__main__":

    if len(sys.argv) < 2:
        show_usage()
    else:
        explore(sys.argv[1])
