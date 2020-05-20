#!/usr/bin/env python3

import csv
import sys
from collections import namedtuple


route_elem = namedtuple(
    'route_elem',
    'x y z index '
    'm_element_enum m_length m_metal_layer m_direction fanouts fanins')
directions = ["left", "right", "up", "down"]

elem_enum_types = {
    0x002B: "LOCAL_LINE",
    0x002D: "LE_BUFFER",
    0x00C4: "FAST_CASCADE_OUT (LUT chain)",
    0x010C: "R4",
    0x0113: "C4",
    0x011A: "LOCAL_INTERCONNECT",
    0x0127: "CLK_BUFFER",
    0x012A: "GLOBAL_CLK_H",
    0x012C: "LAB_CLK",
    0x0133: "IO_DATAIN",
    0x0136: "IO_OE_PIN",
    0x013D: "IO_DATAOUT",
    0x016C: "LAB_CONTROL_MUX",
    0x016E: "JTAG_TDOUSER_PIN",
    0x016F: "JTAG_TMSUTAP_PIN",
    0x0170: "JTAG_TCKUTAP_PIN",
    0x0171: "JTAG_TDIUTAP_PIN",
    0x0172: "JTAG_SHIFTUSER_PIN",
    0x0173: "JTAG_CLKDRUSER_PIN",
    0x0174: "JTAG_UPDATEUSER_PIN",
    0x0175: "JTAG_RUNIDLEUSER_PIN",
    0x0176: "JTAG_USR1USER_PIN",
    0x0177: "GLOBAL_CLK_MUX",
    0x01FE: "IO_BYPASS_OUT",
    0x01FF: "UFM_OUT",
    0x021D: "GEN_CORE_BUF",
}


# Routing graph
def parse_routing(infn):
    with open(infn, 'r') as f:
        inlines = f.readlines()

    # fanouts
    m_route_element_list = []
    m_route_element_templates = {}

    # m_fanin_map
    m_node_data = []
    m_offsets = []

    # Read the structures that we understand
    i = 0
    while i < len(inlines):
        l = inlines[i]
        i += 1

        if l.endswith('ptr.m_route_element_list\n'):
            num_node_data = int(l[4:12], 16)

            for _ in range(num_node_data):
                l = inlines[i]
                i += 1
                m_x = int(l[4:8], 16)

                l = inlines[i]
                i += 1
                m_y = int(l[4:8], 16)

                l = inlines[i]
                i += 1
                m_fanout_edge_base = int(l[4:12], 16)

                l = inlines[i]
                i += 1
                m_template = l[3:16]

                m_route_element_list.append((
                    m_x, m_y, m_fanout_edge_base, m_template))

        elif l.endswith('DYGR_ROUTE_ELEMENT_TEMPLATE\n'):
            addr = l[0:13]

            l = inlines[i]
            i += 1
            m_element_enum = int(l[4:8], 16)

            l = inlines[i]
            i += 1
            m_num_edges = int(l[4:8], 16)

            l = inlines[i]
            i += 1
            m_z = int(l[4:8], 16)

            l = inlines[i]
            i += 1
            m_index = int(l[4:8], 16)

            l = inlines[i]
            i += 1
            m_first_purely_redundant_edge = int(l[4:8], 16)
            # XXX this isn't used in these parts?
            assert m_first_purely_redundant_edge == m_num_edges

            l = inlines[i]
            i += 1
            m_length = int(l[4:6], 16)

            l = inlines[i]
            i += 1
            m_metal_layer = int(l[4:6], 16)

            l = inlines[i]
            i += 1
            m_direction = int(l[4:6], 16)

            # skip header for m_fanout_list_offsets
            i += 1

            m_fanout_list_offsets = []
            for _ in range(m_num_edges):
                l = inlines[i]
                i += 1
                offset = int(l[4:12], 16)

                m_fanout_list_offsets.append(offset)

            # skip m_fanout_to_positions, doesn't seem to be used here?

            m_route_element_templates[addr] = (
                m_element_enum, m_z, m_index, m_length, m_metal_layer,
                m_direction, m_fanout_list_offsets)

        elif l.endswith('ptr.m_fanin_map.m_node_data\n'):
            num_node_data = int(l[4:12], 16)

            for _ in range(num_node_data):
                l = inlines[i]
                i += 1
                m_fanin_edge_base = int(l[4:12], 16)

                l = inlines[i]
                i += 1
                m_num_fanin_edges = int(l[4:12], 16)

                l = inlines[i]
                i += 1
                m_starting_offset_idx = int(l[4:12], 16)

                m_node_data.append((
                    m_fanin_edge_base, m_num_fanin_edges,
                    m_starting_offset_idx))

        elif l.endswith('ptr.m_fanin_map.m_offsets\n'):
            num_offsets = int(l[4:12], 16)

            for _ in range(num_offsets):
                l = inlines[i]
                i += 1
                offset = int(l[4:12], 16)

                m_offsets.append(offset)

    assert len(m_route_element_list) == len(m_node_data)

    # put the pieces together
    route_elems = []
    for i in range(len(m_route_element_list)):
        m_x, m_y, m_fanout_edge_base, m_template = m_route_element_list[i]

        (m_element_enum, m_z, m_index, m_length, m_metal_layer, m_direction,
         m_fanout_list_offsets) = m_route_element_templates[m_template]

        fanouts = []
        for x in m_fanout_list_offsets:
            x = x + m_fanout_edge_base
            x = x & 0xFFFFFFFF
            assert x & 0x80000000   # TODO WHAT DOES THIS DO?
            x = x & 0x7FFFFFFF
            fanouts.append(x)

        fanins = []
        m_fanin_edge_base, m_num_fanin_edges, m_starting_offset_idx = \
            m_node_data[i]
        for j in range(m_num_fanin_edges):
            offset = m_offsets[m_starting_offset_idx + j]
            x = m_fanin_edge_base + offset
            x = x & 0xFFFFFFFF
            assert x & 0x80000000   # TODO WHAT DOES THIS DO?
            x = x & 0x7FFFFFFF
            fanins.append(x)

        route_elems.append(route_elem(
            m_x, m_y, m_z, m_index, m_element_enum, m_length,
            m_metal_layer, m_direction, fanouts, fanins))

    return route_elems


# Bitstream bits for routing graph connections
def parse_asm(infn):
    with open(infn, 'r') as f:
        inlines = f.readlines()

    i = 0
    while i < len(inlines):
        l = inlines[i]
        i += 1

        if l.endswith('DYGR_ROUTE_ASM_INFO_BODY\n'):
            l = inlines[i]
            assert 'm_num_asm_nodes' in l
            i += 1
            m_num_asm_nodes = int(l[4:12], 16)

            # skip m_route_asm_nodes header
            i += 1

            node_choice_bits = []
            for _ in range(m_num_asm_nodes):
                l = inlines[i]
                assert 'm_num_bit_groups' in l
                i += 1
                m_num_bit_groups = int(l[4:8], 16)

                l = inlines[i]
                assert 'm_num_bits' in l
                i += 1
                m_num_bits = int(l[4:8], 16)

                # skip m_start_bit_index header
                i += 1

                m_start_bit_index = []
                for _ in range(m_num_bit_groups):
                    l = inlines[i]
                    assert 'm_start_bit_index' in l
                    i += 1
                    m_start_bit_index.append(int(l[4:8], 16))

                # skip m_asm_bits header
                i += 1

                m_asm_bits = []
                for _ in range(m_num_bits):
                    l = inlines[i]
                    assert 'm_flat_address' in l
                    i += 1
                    m_flat_address = int(l[4:12], 16)

                    l = inlines[i]
                    assert 'm_use_encoded_setting' in l
                    i += 1
                    m_use_encoded_setting = int(l[4:6], 16)

                    l = inlines[i]
                    assert 'm_is_encoded_bit_high' in l
                    i += 1
                    m_is_encoded_bit_high = int(l[4:6], 16)

                    l = inlines[i]
                    assert 'm_is_strangely_encoded' in l
                    i += 1
                    m_is_strangely_encoded = int(l[4:6], 16)

                    l = inlines[i]
                    assert 'm_is_cff_bit' in l
                    i += 1
                    m_is_cff_bit = int(l[4:6], 16)

                    # XXX don't know what these do
                    assert m_is_strangely_encoded == 0
                    assert m_is_cff_bit == 0

                    m_asm_bits.append((
                        m_flat_address,
                        m_use_encoded_setting == 0xFF,
                        m_is_encoded_bit_high == 0xFF))

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
                node_choice_bits.append(choice_bits)

    return node_choice_bits


# Bitstream bits for other stuff
groupmux_info = namedtuple('groupmux_info',
                           'type idx instance mux_level mux_choice bit_pos')
groupbit_info = namedtuple('groupbit_info',
                           'type idx instance bit_i bit_pos')


def parse_asmdb(infn):
    lab_bits = []
    global_bits = []

    def parse_index(x):
        assert x[0] == '['
        assert x[-1] == ']'
        return int(x[1:-1])

    cur_type = None
    cur_idx = None
    arch_group_idx = None
    skipping = False
    with open(infn, 'r') as f:
        for l in f:
            if l.startswith('***** ARCHITECTURE GROUP'):
                cur_type = None
                cur_idx = None

                arch_group_idx = int(l[25:-6])
                if arch_group_idx in (54, 55, 56, 57, 58,
                                      61, 62, 63, 64, 65, 66, 69,
                                      83, 85, 87, 90):
                    skipping = True
                    # print("Skipping arch group {}".format(arch_group_idx))
                else:
                    skipping = False
            elif l.startswith('Type '):
                if skipping:
                    continue
                assert cur_type is None
                cur_type = l[5:-1]
                # print("Current type: {}".format(cur_type))
            elif l.startswith('Index '):
                if skipping:
                    continue
                assert cur_idx is None
                cur_idx = l[6:-1]
            elif l.startswith('Group Mux '):
                if skipping:
                    continue
                assert cur_type is not None
                assert cur_idx is not None
                l = l[10:]

                indices, bits = l.split(':')
                indices = indices.strip()
                bits = bits.strip()

                indices = indices.split(' ')
                bits = bits.split(' ')
                assert len(indices) == 2

                indices = [parse_index(x) for x in indices]
                bits = [int(x) for x in bits if not x.startswith('ILL_')]

                for bit_i, bit in enumerate(bits):
                    instance, mux_level = indices

                    infoinfo = groupmux_info(
                        cur_type,
                        cur_idx,
                        instance,
                        mux_level,
                        bit_i,
                        bit)

                    if arch_group_idx < 46:
                        lab_bits.append(infoinfo)
                    else:
                        global_bits.append(infoinfo)
            elif l.startswith('Group ['):
                if skipping:
                    continue
                assert cur_type is not None
                assert cur_idx is not None
                l = l[6:]

                index, bits = l.split(':')
                index = index.strip()
                bits = bits.strip()

                bits = bits.split(' ')

                index = parse_index(index)
                bits = [int(x) for x in bits if not x.startswith('ILL_')]

                for bit_i, bit in enumerate(bits):
                    instance = index

                    infoinfo = groupbit_info(
                        cur_type,
                        cur_idx,
                        instance,
                        bit_i,
                        bit)

                    if arch_group_idx < 46:
                        lab_bits.append(infoinfo)
                    else:
                        global_bits.append(infoinfo)

    return lab_bits, global_bits


def main(dev, mode, asmdump_fn, routingdump_fn, asmdbdump_fn):
    if dev == "240":
        CRAM_WIDTH = 195
        CRAM_HEIGHT = 207
    elif dev == "570":
        CRAM_WIDTH = 363
        CRAM_HEIGHT = 345
    elif dev == "1270":
        CRAM_WIDTH = 475
        CRAM_HEIGHT = 483
    elif dev == "2210":
        CRAM_WIDTH = 587
        CRAM_HEIGHT = 621
    else:
        print("Invalid device {}".format(dev))
        sys.exit(1)

    route_elems = parse_routing(routingdump_fn)
    route_bits = parse_asm(asmdump_fn)
    assert len(route_elems) == len(route_bits)
    lab_bits, global_bits = parse_asmdb(asmdbdump_fn)

    if mode == "dump_routing_only" or mode == "dump_routing_with_bits":
        for i in range(len(route_elems)):
            e = route_elems[i]
            print("Element {}:".format(i))
            print("    {}:X{}Y{}S{}I{}".format(
                elem_enum_types[e.m_element_enum], e.x, e.y, e.z, e.index))

            if e.m_direction == 0:
                assert e.m_length == 0 or e.m_length == 1
                assert e.m_metal_layer == 0
                if e.m_length == 1:
                    print("    m_length: {}".format(e.m_length))
            else:
                print("    m_length: {}".format(e.m_length))
                print("    m_direction: {}".format(
                    directions[e.m_direction - 1]))
                print("    m_metal_layer: {}".format(e.m_metal_layer))

            print("    Fanouts:")
            for fanout_i, x in enumerate(e.fanouts):
                efanout = route_elems[x]
                print("        element {} ({}:X{}Y{}S{}I{})".format(
                    x,
                    elem_enum_types[efanout.m_element_enum],
                    efanout.x,
                    efanout.y,
                    efanout.z,
                    efanout.index))

                if mode == "dump_routing_with_bits":
                    bits_involved = route_bits[i][fanout_i]
                    assert len(bits_involved) <= 2  # just for now

                    for bit, _, _ in bits_involved:
                        alteraX = bit % CRAM_WIDTH
                        alteraY = bit // CRAM_WIDTH

                        print("            ({}, {})".format(
                            CRAM_WIDTH - alteraX - 2, alteraY))

            print("    Fanins:")
            for x in e.fanins:
                efanin = route_elems[x]
                print("        element {} ({}:X{}Y{}S{}I{})".format(
                    x,
                    elem_enum_types[efanin.m_element_enum],
                    efanin.x,
                    efanin.y,
                    efanin.z,
                    efanin.index))
    elif mode == "dump_lab_bits":
        LAB_WIDTH = 28
        LAB_HEIGHT = 46

        outfn = "labbits-parsed-{}.csv".format(dev)

        bits_info = []
        for _ in range(LAB_HEIGHT):
            bits_info.append(['??'] * LAB_WIDTH)

        for x in lab_bits:
            alteraX = x.bit_pos % CRAM_WIDTH
            alteraY = x.bit_pos // CRAM_WIDTH

            cur_data = bits_info[alteraY][-alteraX - 1]
            if cur_data == '??':
                cur_data = ''
            # FIXME this doesn't handle groupbit_info
            bits_info[alteraY][-alteraX - 1] = (
                "{}{}\nindex {}\ninstance {}\n"
                "mux level {}\nmux choice {}").format(
                    cur_data + '\n\n' if cur_data else '',
                    x.type,
                    x.idx,
                    x.instance,
                    x.mux_level,
                    x.mux_choice)

        with open(outfn, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(bits_info)
    elif mode == "dump_global_bits":
        outfn = "global-bits-parsed-{}.csv".format(dev)

        bits_info = []
        for _ in range(CRAM_HEIGHT):
            bits_info.append(['??'] * CRAM_WIDTH)

        # routing
        for elem_src_i, e in enumerate(route_elems):
            e = route_elems[elem_src_i]
            a = route_bits[elem_src_i]

            for fanout_i, elem_dst_i in enumerate(e.fanouts):
                elem_dst_i = e.fanouts[fanout_i]
                edest = route_elems[elem_dst_i]
                elem_dst_name = "{}:X{}Y{}S{}I{}".format(
                    elem_enum_types[edest.m_element_enum],
                    edest.x, edest.y, edest.z, edest.index)

                bits_involved = a[fanout_i]
                assert len(bits_involved) <= 2  # just for now

                for bit, _, _ in bits_involved:
                    alteraX = bit % CRAM_WIDTH
                    alteraY = bit // CRAM_WIDTH

                    cur_data = bits_info[alteraY][-alteraX - 1]
                    if cur_data == '??':
                        new_data = elem_dst_name
                    elif elem_dst_name in cur_data:
                        new_data = cur_data
                    else:
                        print("WARN: adding {} to {}".format(
                            elem_dst_name, cur_data))
                        new_data = cur_data + '\n' + elem_dst_name

                    bits_info[alteraY][-alteraX - 1] = new_data

        # global bits
        for x in global_bits:
            alteraX = x.bit_pos % CRAM_WIDTH
            alteraY = x.bit_pos // CRAM_WIDTH

            cur_data = bits_info[alteraY][-alteraX - 1]
            if cur_data == '??':
                cur_data = ''
            else:
                print("WARN: Adding to {}".format(cur_data.split('\n')[0]))
            if isinstance(x, groupmux_info):
                bits_info[alteraY][-alteraX - 1] = (
                    "{}{}\nindex {}\ninstance {}\n"
                    "mux level {}\nmux choice {}").format(
                        cur_data + '\n\n' if cur_data else '',
                        x.type,
                        x.idx,
                        x.instance,
                        x.mux_level,
                        x.mux_choice)
            else:
                bits_info[alteraY][-alteraX - 1] = (
                    "{}{}\nindex {}\ninstance {}\n"
                    "bit {}").format(
                        cur_data + '\n\n' if cur_data else '',
                        x.type,
                        x.idx,
                        x.instance,
                        x.bit_i)

        with open(outfn, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(bits_info)
    else:
        print("Invalid mode {}".format(mode))
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: {} dev mode asm.dmp routing.dmp asmdb.dmp".format(
            sys.argv[0]))
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
