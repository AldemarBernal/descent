import os
import struct
import sys


def show_usage():
    print 'usage: python hog-extractor.py <file.hog>'


def extract(filename):
    if not os.path.isfile(filename):
        print filename + ' not found'

    else:
        folder = filename + '.files'

        with open(filename, 'rb') as hog:
            header = hog.read(3)

            if header != 'DHF':
                print 'DHF header not found, ' + filename + ' is not a HOG file'

            else:
                while True:
                    file = hog.read(13).split('\x00')[0]

                    if file == '':
                        break

                    size = struct.unpack('<i', hog.read(4))[0]
                    contents = hog.read(size)

                    print 'File: ' + file + ' - Size: ' + str(size) + ' bytes'

                    if not os.path.exists(folder):
                        os.makedirs(folder)

                    open(os.path.join(folder, file) , 'wb').write(contents)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        show_usage()
    else:
        extract(sys.argv[1])
