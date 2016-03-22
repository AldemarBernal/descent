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

RDL_THING_ROBOT = 2
RDL_THING_HOSTAGE = 3
RDL_THING_START_PLACE = 4
RDL_THING_MINE = 5
RDL_THING_ITEM = 7
RDL_THING_REACTOR = 9
RDL_THING_COOP_START_PLACE = 14

RDL_THINGS_TEXT = {
    RDL_THING_ROBOT: 'robots',
    RDL_THING_HOSTAGE: 'hostages',
    RDL_THING_START_PLACE: 'start_places',
    RDL_THING_MINE: 'mines',
    RDL_THING_ITEM: 'items',
    RDL_THING_REACTOR: 'reactors',
    RDL_THING_COOP_START_PLACE: 'coop_start_places'}


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

                #print('version: ' + str(version))
                #print('mine data offset: ' + str(mineDataOffset))
                #print('objects offset: ' + str(objectsOffset))
                #print('file size: ' + str(fileSize))

                mineData = get_mine_data(rdl, mineDataOffset)

                read_byte(rdl)

                noIdeaOffset = read_integer(rdl)
                numNoIdea = read_integer(rdl)

                thingsOffset = read_integer(rdl)
                numThings = read_integer(rdl)

                mineData['things'] = get_things_data(rdl, numThings, thingsOffset)

                print(json.dumps(mineData, indent = 4))


def get_mine_data(rdl, offset):
    mine = OrderedDict()

    rdl.seek(offset)

    version = read_ubyte(rdl)
    vertexCount = read_short(rdl)
    cubeCount = read_short(rdl)

    #print('compiled version: ' + str(version))
    #print('vertex count: ' + str(vertexCount))
    #print('cube count: ' + str(cubeCount))

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
    #mine['vertex_count'] = vertexCount
    #mine['cube_count'] = cubeCount
    mine['vertices'] = vertices
    mine['cubes'] = cubes

    return mine


def get_things_data(rdl, numThings, offset):
    things = OrderedDict()

    rdl.seek(offset)

    for idThing in range(0, numThings):
        type = read_byte(rdl)

        thingType = read_byte(rdl)
        thing = get_things_common(rdl)

        if RDL_THINGS_TEXT[type] not in things:
            things[RDL_THINGS_TEXT[type]] = []

        if type == RDL_THING_ROBOT:
            dropType = read_byte(rdl)
            dropTypeId = read_byte(rdl)
            dropCount = read_byte(rdl)
            unknown = read_integer(rdl)
            textureOverride = read_byte(rdl)
            unknown = read_bytes(rdl, 155)

            thing['type'] = thingType
            thing['drop_type'] = dropType
            thing['drop_type_id'] = dropTypeId
            thing['drop_count'] = dropCount
            thing['texture_override'] = textureOverride

        elif type == RDL_THING_HOSTAGE:
            unknown = read_bytes(rdl, 16)

        elif type == RDL_THING_START_PLACE or type == RDL_THING_COOP_START_PLACE:
            unknown = read_bytes(rdl, 139)

            thing['start_number'] = thingType

        elif type == RDL_THING_ITEM:
            unknown = read_bytes(rdl, 6)
            textureOverride = read_byte(rdl)
            unknown = read_bytes(rdl, 9)

            thing['type'] = thingType
            thing['texture_override'] = textureOverride

        elif type == RDL_THING_REACTOR:
            unknown = read_bytes(rdl, 75)

            thing['type'] = thingType

        else:
            raise Exception('Oops, wrong thing type: ' + str(type))

        things[RDL_THINGS_TEXT[type]].append(thing)

    return things


def get_things_common(rdl):
    thing = OrderedDict()

    thing['control'] = read_byte(rdl)
    thing['movement'] = read_byte(rdl)
    thing['render'] = read_byte(rdl)
    thing['flags'] = read_byte(rdl)
    thing['cube'] = read_ushort(rdl)
    thing['position'] = read_vector(rdl)
    thing['orientation'] = []
    thing['orientation'].append(read_vector(rdl))
    thing['orientation'].append(read_vector(rdl))
    thing['orientation'].append(read_vector(rdl))
    thing['size'] = read_integer(rdl) / 65536.0
    thing['shield'] = read_integer(rdl) / 65536.0
    thing['last_position'] = read_vector(rdl)

    return thing


def read_byte(file):
    return struct.unpack('<b', file.read(1))[0]

def read_bytes(file, max_submodels):
    dict = OrderedDict()
    for index in range(0, max_submodels):
        dict[index] = read_byte(file)

    return dict

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
