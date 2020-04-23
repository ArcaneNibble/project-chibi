#!/usr/bin/env python3

import csv
import sys
import parse_dumped_routing_2

WIDTH = 195
HEIGHT = 207

def parse_asm(infn):
    with open(infn, 'r') as f:
        inlines = f.readlines()

    i = 0
    while i < len(inlines):
        l = inlines[i]
        i += 1

        if l.endswith('DYGR_ROUTE_ASM_INFO_BODY\n'):
            # print(l)

            l = inlines[i]
            i += 1
            m_num_asm_nodes = int(l[4:12], 16)
            # print(m_num_asm_nodes)

            # skip m_route_asm_nodes header
            i += 1

            node_choice_bits = []
            for _ in range(m_num_asm_nodes):
                l = inlines[i]
                i += 1
                m_num_bit_groups = int(l[4:8], 16)
                # print(l)
                assert 'm_num_bit_groups' in l

                l = inlines[i]
                i += 1
                m_num_bits = int(l[4:8], 16)
                # print(l)

                # skip m_start_bit_index header
                i += 1

                m_start_bit_index = []
                for _ in range(m_num_bit_groups):
                    l = inlines[i]
                    i += 1
                    m_start_bit_index.append(int(l[4:8], 16))
                # print(m_start_bit_index)

                # skip m_asm_bits header
                i += 1

                m_asm_bits = []
                for _ in range(m_num_bits):
                    l = inlines[i]
                    i += 1
                    m_flat_address = int(l[4:12], 16)

                    l = inlines[i]
                    i += 1
                    m_use_encoded_setting = int(l[4:6], 16)

                    l = inlines[i]
                    i += 1
                    m_is_encoded_bit_high = int(l[4:6], 16)

                    l = inlines[i]
                    i += 1
                    m_is_strangely_encoded = int(l[4:6], 16)

                    l = inlines[i]
                    i += 1
                    m_is_cff_bit = int(l[4:6], 16)

                    # XXX don't know what these do
                    assert m_is_strangely_encoded == 0
                    assert m_is_cff_bit == 0

                    m_asm_bits.append((m_flat_address, m_use_encoded_setting == 0xFF, m_is_encoded_bit_high == 0xFF))
                # print(m_asm_bits)

                # reformat
                choice_bits = []
                for j in range(m_num_bit_groups):
                    first_bit = m_start_bit_index[j] - 1
                    if j == m_num_bit_groups - 1:
                        last_bit = m_num_bits
                    else:
                        last_bit = m_start_bit_index[j + 1] - 1
                    assert first_bit >= 0
                    bits = m_asm_bits[first_bit:last_bit]
                    choice_bits.append(bits)
                    # print(first_bit, last_bit, bits)
                    # assert len(bits) > 0
                # print(choice_bits)
                node_choice_bits.append(choice_bits)

    return node_choice_bits

def main():
    infn_globalbits = sys.argv[1]
    infn_routing = sys.argv[2]
    infn_asm = sys.argv[3]
    outfn = "global-bits-parsed.csv"

    bits_info = []
    for _ in range(HEIGHT):
        bits_info.append(['??'] * WIDTH)

    # do the routing stuff
    route_elements = parse_dumped_routing_2.parse_routing(infn_routing)

    # actual bit map is here
    route_bits = parse_asm(infn_asm)
    # print(route_bits)

    # print(len(route_elements), len(route_bits))
    assert len(route_elements) == len(route_bits)

    for elem_src_i in range(len(route_elements)):
        e = route_elements[elem_src_i]
        a = route_bits[elem_src_i]

        elem_src_name = "{}:X{}Y{}S{}I{}".format(parse_dumped_routing_2.elem_enum_types[e.m_element_enum], e.x, e.y, e.z, e.index)
        # print(elem_src_name)

        for fanout_i in range(len(e.fanouts)):
            elem_dst_i = e.fanouts[fanout_i] & 0x7FFFFFFF
            edest = route_elements[elem_dst_i]
            elem_dst_name = "{}:X{}Y{}S{}I{}".format(parse_dumped_routing_2.elem_enum_types[edest.m_element_enum], edest.x, edest.y, edest.z, edest.index)
            print("{} -> {}".format(elem_src_name, elem_dst_name))

            bits_involved = a[fanout_i]
            # print(bits_involved)
            assert len(bits_involved) <= 2 # just for now

            for bit, _, _ in bits_involved:
                alteraX = bit % WIDTH
                alteraY = bit // WIDTH

                cur_data = bits_info[alteraY][-alteraX-1]
                if cur_data == '??':
                    new_data = elem_dst_name
                elif elem_dst_name in cur_data:
                    new_data = cur_data
                else:
                    print("WARN: adding {} to {}".format(elem_dst_name, cur_data))
                    new_data = cur_data + '\n' + elem_dst_name

                bits_info[alteraY][-alteraX-1] = new_data

    cur_type = None
    cur_idx = None
    with open(infn_globalbits, 'r') as f:
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

                    alteraX = bit % WIDTH
                    alteraY = bit // WIDTH

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
            elif l.startswith('Group ['):
                # print(l)
                assert cur_type is not None
                assert cur_idx is not None
                l = l[6:]

                index, bits = l.split(':')
                index = index.strip()
                bits = bits.strip()
                # print(index, bits)

                bits = bits.split(' ')
                # print(index, bits)

                def parse_index(x):
                    assert x[0] == '['
                    assert x[-1] == ']'
                    return int(x[1:-1])
                index = parse_index(index)
                bits = [int(x) for x in bits if not x.startswith('ILL_')]
                # print(index, bits)

                for bit_i, bit in enumerate(bits):
                    instance = index

                    alteraX = bit % WIDTH
                    alteraY = bit // WIDTH

                    cur_data = bits_info[alteraY][-alteraX-1]
                    if cur_data == '??':
                        cur_data = ''
                    bits_info[alteraY][-alteraX-1] = "{}{}\nindex {}\ninstance {}\nbit {}".format(
                        cur_data + '\n\n' if cur_data else '',
                        cur_type,
                        cur_idx,
                        index,
                        bit_i)

    # output
    with open(outfn, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(bits_info)

if __name__ == '__main__':
    main()
