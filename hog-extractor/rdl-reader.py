import os
import struct
import sys
from collections import OrderedDict


def show_usage():
    print 'usage: python rdl-reader.py <levelxx.rdl>'


def rdl_read(filename):
    if not os.path.isfile(filename):
        print(filename + ' not found')

    else:
        with open(filename, 'rb') as rdl:
            signature = rdl.read(4)

            if signature != 'LVLP':
                print('LVLP header not found')

            else:
                version = read_integer(rdl)
                mineDataOffset = read_integer(rdl)
                objectsOffset = read_integer(rdl)
                fileSize = read_integer(rdl)

                print('version: ' + str(version))
                print('mine data offset: ' + str(mineDataOffset))
                print('objects offset: ' + str(objectsOffset))
                print('file size: ' + str(fileSize))

                mineData = get_mine_data(rdl, mineDataOffset)


def get_mine_data(rdl, offset):
    rdl.seek(offset)

    read_byte(rdl)

    vertexCount = read_short(rdl)
    cubeCount = read_short(rdl)

    vertices = read_vectors(rdl, vertexCount)

    print('vertex count: ' + str(vertexCount))
    print('cube count: ' + str(cubeCount))

    print('vertices:')
    print(vertices)



def read_byte(file):
    return struct.unpack('<B', file.read(1))[0]

def read_short(file):
    return struct.unpack('<H', file.read(2))[0]

def read_integer(file):
    return struct.unpack('<i', file.read(4))[0]

def read_vector(file):
    vector = OrderedDict()
    vector['x'] = read_integer(file)
    vector['y'] = read_integer(file)
    vector['z'] = read_integer(file)
    return vector

def read_vectors(file, max_submodels):
    dict = OrderedDict()
    for index in range(0, max_submodels):
        dict[index] = read_vector(file)

    return dict


if __name__ == "__main__":

    if len(sys.argv) < 2:
        show_usage()
    else:
        rdl_read(sys.argv[1])
