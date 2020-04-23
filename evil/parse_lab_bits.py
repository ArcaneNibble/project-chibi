#!/usr/bin/env python3

import csv
import sys

WIDTH = 28
HEIGHT = 46
CRAM_DIM = 195

def main():
    infn = sys.argv[1]
    outfn = "labbits-parsed.csv"

    bits_info = []
    for _ in range(HEIGHT):
        bits_info.append(['??'] * WIDTH)

    cur_type = None
    cur_idx = None
    with open(infn, 'r') as f:
        for l in f:
            # print(l)
            if l.startswith('***** ARCHITECTURE GROUP'):
                cur_type = None
                cur_idx = None
            elif l.startswith('Type '):
                assert cur_type is None
                cur_type = l[5:-1]
                print("Current type: {}".format(cur_type))
            elif l.startswith('Index '):
                assert cur_idx is None
                cur_idx = l[6:-1]
            elif l.startswith('Group Mux '):
                assert cur_type is not None
                assert cur_idx is not None
                l = l[10:]

                indices, bits = l.split(':')
                indices = indices.strip()
                bits = bits.strip()
                # print(indices, bits)

                indices = indices.split(' ')
                bits = bits.split(' ')
                # print(indices, bits)
                assert len(indices) == 2

                def parse_index(x):
                    assert x[0] == '['
                    assert x[-1] == ']'
                    return int(x[1:-1])
                indices = [parse_index(x) for x in indices]
                bits = [int(x) for x in bits if not x.startswith('ILL_')]
                # print(indices, bits)

                for bit_i, bit in enumerate(bits):
                    instance, mux_level = indices
                    # print(instance, _mux_level)

                    alteraX = bit % CRAM_DIM
                    alteraY = bit // CRAM_DIM

                    cur_data = bits_info[alteraY][-alteraX-1]
                    if cur_data == '??':
                        cur_data = ''
                    bits_info[alteraY][-alteraX-1] = "{}{}\nindex {}\ninstance {}\nmux level {}\nmux choice {}".format(
                        cur_data + '\n\n' if cur_data else '',
                        cur_type,
                        cur_idx,
                        instance,
                        mux_level,
                        bit_i)

    # output
    with open(outfn, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(bits_info)

if __name__ == '__main__':
    main()
