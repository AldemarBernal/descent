import json
import os
import struct
import sys
from collections import OrderedDict


#RDL constants
RDL_LEFT_SIDE = 0x01
RDL_TOP_SIDE = 0x02
RDL_RIGHT_SIDE = 0x04
RDL_BOTTOM_SIDE = 0x08
RDL_BACK_SIDE = 0x10
RDL_FRONT_SIDE = 0x20
RDL_ENERGY_CENTER = 0x40

RDL_SIDES = [RDL_LEFT_SIDE, RDL_TOP_SIDE, RDL_RIGHT_SIDE, RDL_BOTTOM_SIDE, RDL_BACK_SIDE, RDL_FRONT_SIDE]
RDL_SIDES_TEXT = {
    RDL_LEFT_SIDE: 'left_side',
    RDL_TOP_SIDE: 'top_side',
    RDL_RIGHT_SIDE: 'right_side',
    RDL_BOTTOM_SIDE: 'bottom_side',
    RDL_BACK_SIDE: 'back_side',
    RDL_FRONT_SIDE: 'front_side'}


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

#                print('version: ' + str(version))
#                print('mine data offset: ' + str(mineDataOffset))
#                print('objects offset: ' + str(objectsOffset))
#                print('file size: ' + str(fileSize))

                mineData = get_mine_data(rdl, mineDataOffset)

                print(json.dumps(mineData, indent = 4))


def get_mine_data(rdl, offset):
    mine = OrderedDict()

    rdl.seek(offset)

    version = read_ubyte(rdl)
    vertexCount = read_short(rdl)
    cubeCount = read_short(rdl)

#    print('compiled version: ' + str(version))
#    print('vertex count: ' + str(vertexCount))
#    print('cube count: ' + str(cubeCount))

    vertices = read_vectors(rdl, vertexCount)

    cubes = OrderedDict()
    for cubeIndex in range(0, cubeCount):
        cube = OrderedDict()

        bitmask = read_byte(rdl)
        if bitmask:
            cube['attached_cubes'] = OrderedDict()

            for side in RDL_SIDES:
                if bitmask & side:
                    cube['attached_cubes'][RDL_SIDES_TEXT[side]] = read_short(rdl)

        cube['vertices'] = []
        for index in range(0, 8):
            cube['vertices'].append(read_short(rdl))


        if bitmask & RDL_ENERGY_CENTER:
            cube['energy_center'] = OrderedDict()
            cube['energy_center']['special'] = read_ubyte(rdl)
            cube['energy_center']['number'] = read_byte(rdl)
            cube['energy_center']['value'] = read_short(rdl)


        cube['static_light'] = float(read_short(rdl)) / 4096.0

        wall_bitmask = read_byte(rdl)
        if wall_bitmask:
            cube['walls'] = OrderedDict()

            for side in RDL_SIDES:
                if wall_bitmask & side:
                    cube['walls'][RDL_SIDES_TEXT[side]] = read_ubyte(rdl)


        cube['textures'] = OrderedDict()

        for side in RDL_SIDES:
            if not (bitmask & side) or (wall_bitmask & side) or cube['attached_cubes'][RDL_SIDES_TEXT[side]] < 0:
                texture = read_ushort(rdl)
                cube['textures'][RDL_SIDES_TEXT[side]] = OrderedDict()
                cube['textures'][RDL_SIDES_TEXT[side]]['primary'] = texture & 0x7FFF

                if texture & 0x8000:
                    cube['textures'][RDL_SIDES_TEXT[side]]['secondary'] = read_short(rdl)

                cube['textures'][RDL_SIDES_TEXT[side]]['vertices'] = []
                for vertexIndex in range(0, 4):
                    uvl = OrderedDict()

                    uvl['u'] = float(read_short(rdl)) / 4096.0
                    uvl['v'] = float(read_short(rdl)) / 4096.0
                    uvl['l'] = float(read_ushort(rdl)) / 4096.0

                    cube['textures'][RDL_SIDES_TEXT[side]]['vertices'].append(uvl)


        cubes[cubeIndex] = cube


    mine['version'] = version
    mine['vertex_count'] = vertexCount
    mine['cube_count'] = cubeCount
    mine['vertices'] = vertices
    mine['cubes'] = cubes

    return mine


def read_byte(file):
    return struct.unpack('<b', file.read(1))[0]

def read_ubyte(file):
    return struct.unpack('<B', file.read(1))[0]

def read_short(file):
    return struct.unpack('<h', file.read(2))[0]

def read_ushort(file):
    return struct.unpack('<H', file.read(2))[0]

def read_integer(file):
    return struct.unpack('<i', file.read(4))[0]

def read_vector(file):
    vector = OrderedDict()
    vector['x'] = float(read_integer(file)) / 65536.0
    vector['y'] = float(read_integer(file)) / 65536.0
    vector['z'] = float(read_integer(file)) / 65536.0
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
