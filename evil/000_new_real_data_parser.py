#!/usr/bin/env python3

import csv
import json
import sys
from collections import namedtuple


LAB_WIDTH = 28
LAB_HEIGHT = 46

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

        LONG_ROWS = 4
        SHORT_ROWS = 0
        LONG_COLS = 6
        SHORT_COLS = 0

        CLK_AFTER_LAB_ROWS = 2
    elif dev == "570":
        CRAM_WIDTH = 363
        CRAM_HEIGHT = 345

        LONG_ROWS = 4
        SHORT_ROWS = 3
        LONG_COLS = 12
        SHORT_COLS = 3

        CLK_AFTER_LAB_ROWS = 4
    elif dev == "1270":
        CRAM_WIDTH = 475
        CRAM_HEIGHT = 483

        LONG_ROWS = 7
        SHORT_ROWS = 3
        LONG_COLS = 16
        SHORT_COLS = 5

        CLK_AFTER_LAB_ROWS = 5
    elif dev == "2210":
        CRAM_WIDTH = 587
        CRAM_HEIGHT = 621

        LONG_ROWS = 10
        SHORT_ROWS = 3
        LONG_COLS = 20
        SHORT_COLS = 7

        CLK_AFTER_LAB_ROWS = 7
    else:
        print("Invalid device {}".format(dev))
        sys.exit(1)

    def blockY(tileY):
        # number 0 is the bottom IO
        # number 1 to (LONG_ROWS + SHORT_ROWS) are LABs
        # number (LONG_ROWS + SHORT_ROWS) + 1 is the top IO
        assert tileY > 0
        assert tileY <= LONG_ROWS + SHORT_ROWS

        y_from_the_top = (LONG_ROWS + SHORT_ROWS) - tileY
        temp_y_out = LAB_HEIGHT * y_from_the_top
        if tileY <= CLK_AFTER_LAB_ROWS:
            temp_y_out += 1

        temp_y_out += 11    # TOP IO height

        return temp_y_out

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
    elif mode == "analyze_wire_names":
        outfn = "wire-name-map-{}.json".format(dev)
        my_wire_to_quartus_wire = {}

        # FIXME COPYPASTA
        bits_info = []
        for _ in range(CRAM_HEIGHT):
            bits_info.append(['??'] * (CRAM_WIDTH - 1))

        e_dirs = {}

        # routing
        for elem_src_i, e in enumerate(route_elems):
            e = route_elems[elem_src_i]
            a = route_bits[elem_src_i]

            elem_src_name = "{}:X{}Y{}S{}I{}".format(
                elem_enum_types[e.m_element_enum], e.x, e.y, e.z, e.index)

            e_dirs[elem_src_name] = e.m_direction

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

        # LEFT HAND SIDE IOs
        for labrow in range(LONG_ROWS):
            if dev == "240":
                tileX = 1
            else:
                tileX = 0

            tileY = 1 + SHORT_ROWS + labrow

            coordYbase = blockY(tileY)

            print(tileX, tileY, coordYbase)

            for wireI in range(8):
                my_name = 'R:X{}Y{}I{}'.format(tileX, tileY, wireI)

                if wireI % 2 == 0:
                    coordX = 3
                else:
                    coordX = 5

                if wireI // 2 == 0:
                    coordY = coordYbase + 1
                elif wireI // 2 == 1:
                    coordY = coordYbase + 3
                elif wireI // 2 == 2:
                    coordY = coordYbase + 42
                elif wireI // 2 == 3:
                    coordY = coordYbase + 44

                this_mux_bitdata = [
                    bits_info[coordY][coordX + 0],
                    bits_info[coordY][coordX + 1],
                ]

                print(wireI, this_mux_bitdata)

                results = set(this_mux_bitdata)
                assert len(results) == 1 or len(results) == 2
                if len(results) == 2:
                    assert '??' in results
                    results.remove('??')
                result = list(results)[0]
                assert e_dirs[result] == 2
                my_wire_to_quartus_wire[my_name] = result

        # TOP IOs
        for iocol in range(LONG_COLS):
            tileY = LONG_ROWS + SHORT_ROWS + 1

            if dev == "240":
                tileX = 2 + iocol
            else:
                tileX = 1 + iocol

            coordXbase = 11 + LAB_WIDTH * iocol

            print(tileX, tileY, coordXbase)

            for wireI in range(10):
                my_name = 'D:X{}Y{}I{}'.format(tileX, tileY, wireI)

                coordY = 1 + 2 * (wireI % 5)
                # print(coordY)

                if wireI < 5:
                    this_mux_bitdata = [
                        bits_info[coordY + 1][coordXbase + 0],
                        bits_info[coordY + 0][coordXbase + 2],
                    ]
                else:
                    this_mux_bitdata = [
                        bits_info[coordY + 0][coordXbase + 25],
                        bits_info[coordY + 1][coordXbase + 27],
                    ]

                print(wireI, this_mux_bitdata)

                results = set(this_mux_bitdata)
                assert len(results) == 1 or len(results) == 2
                if len(results) == 2:
                    assert '??' in results
                    results.remove('??')
                result = list(results)[0]
                assert e_dirs[result] == 4
                my_wire_to_quartus_wire[my_name] = result

        # BOTTOM IOs
        for iocol in range(LONG_COLS):
            if dev != "240" and iocol == (LONG_COLS - SHORT_COLS - 1):
                continue

            if iocol < (LONG_COLS - SHORT_COLS):
                tileY = SHORT_ROWS
                coordYbase = 11 + LONG_ROWS * LAB_HEIGHT + 1
                # XXX the last +1 is a hack for the clock
            else:
                tileY = 0
                coordYbase = 11 + (LONG_ROWS + SHORT_ROWS) * LAB_HEIGHT + 1
                # XXX the last +1 is a hack for the clock

            if dev == "240":
                tileX = 2 + iocol
            else:
                tileX = 1 + iocol

            coordXbase = 11 + LAB_WIDTH * iocol

            print(tileX, tileY, coordXbase, coordYbase)

            for wireI in range(10):
                my_name = 'U:X{}Y{}I{}'.format(tileX, tileY, wireI)

                coordY = coordYbase + 2 * (wireI % 5)
                # print(coordY)

                if wireI < 5:
                    this_mux_bitdata = [
                        bits_info[coordY + 0][coordXbase + 0],
                        bits_info[coordY + 1][coordXbase + 2],
                    ]
                else:
                    this_mux_bitdata = [
                        bits_info[coordY + 1][coordXbase + 25],
                        bits_info[coordY + 0][coordXbase + 27],
                    ]

                print(wireI, this_mux_bitdata)

                results = set(this_mux_bitdata)
                assert len(results) == 1 or len(results) == 2
                if len(results) == 2:
                    assert '??' in results
                    results.remove('??')
                result = list(results)[0]
                assert e_dirs[result] == 3
                my_wire_to_quartus_wire[my_name] = result

        # MAIN interconnect area
        def getbox(x, y):
            ret = []
            for xx in range(4):
                for yy in range(2):
                    ret.append(bits_info[y + yy][x + xx])
            return ret

        for labrow in range(LONG_ROWS + SHORT_ROWS):
            if labrow < SHORT_ROWS:
                numcols = SHORT_COLS
            else:
                numcols = LONG_COLS
            for labcol in range(numcols + 1):
                tileY = 1 + labrow
                if labrow < SHORT_ROWS:
                    tileX = 1 + (LONG_COLS - SHORT_COLS) + labcol
                    coordXbase = 7 + LAB_WIDTH * (
                        labcol + (LONG_COLS - SHORT_COLS))
                else:
                    tileX = 1 + labcol
                    coordXbase = 7 + LAB_WIDTH * labcol
                if dev == "240":
                    tileX += 1

                coordYbase = blockY(tileY)

                print(tileX, tileY, coordXbase, coordYbase)

                # UP
                for wireI in range(7):
                    my_name = 'U:X{}Y{}I{}'.format(tileX, tileY, wireI)

                    if wireI == 0:
                        this_mux_bitdata = getbox(
                            coordXbase + 0,
                            coordYbase + 0)
                    elif wireI == 1:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 4)
                    elif wireI == 2:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 10)
                    elif wireI == 3:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 16)
                    elif wireI == 4:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 32)
                    elif wireI == 5:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 36)
                    elif wireI == 6:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 42)

                    print(wireI, this_mux_bitdata)

                    results = set(this_mux_bitdata)
                    assert len(results) == 1 or len(results) == 2
                    if len(results) == 2:
                        assert '??' in results
                        results.remove('??')
                    result = list(results)[0]
                    assert e_dirs[result] == 3
                    my_wire_to_quartus_wire[my_name] = result

                # DOWN
                for wireI in range(7):
                    my_name = 'D:X{}Y{}I{}'.format(tileX, tileY, wireI)

                    if wireI == 0:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 2)
                    elif wireI == 1:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 8)
                    elif wireI == 2:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 12)
                    elif wireI == 3:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 28)
                    elif wireI == 4:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 34)
                    elif wireI == 5:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 40)
                    elif wireI == 6:
                        this_mux_bitdata = getbox(
                            coordXbase + 0,
                            coordYbase + 44)

                    print(wireI, this_mux_bitdata)

                    results = set(this_mux_bitdata)
                    assert len(results) == 1 or len(results) == 2
                    if len(results) == 2:
                        assert '??' in results
                        results.remove('??')
                    result = list(results)[0]
                    assert e_dirs[result] == 4
                    my_wire_to_quartus_wire[my_name] = result

                # RIGHT (except last col which is L2)
                for wireI in range(8):
                    if labcol != numcols:
                        my_name = 'R:X{}Y{}I{}'.format(tileX, tileY, wireI)
                    else:
                        my_name = 'L2:X{}Y{}I{}'.format(tileX, tileY, wireI)

                    if wireI == 0:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 0)
                    elif wireI == 1:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 6)
                    elif wireI == 2:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 14)
                    elif wireI == 3:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 18)
                    elif wireI == 4:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 26)
                    elif wireI == 5:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 30)
                    elif wireI == 6:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 38)
                    elif wireI == 7:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 44)

                    print(wireI, this_mux_bitdata)

                    results = set(this_mux_bitdata)
                    assert len(results) == 1 or len(results) == 2
                    if len(results) == 2:
                        assert '??' in results
                        results.remove('??')
                    result = list(results)[0]
                    if labcol != numcols:
                        assert e_dirs[result] == 2
                    else:
                        assert e_dirs[result] == 1
                    my_wire_to_quartus_wire[my_name] = result

                # LEFT (except first col which doesn't have any or
                # the UFM corner which is R2)
                for wireI in range(8):
                    if labcol == 0 and labrow >= SHORT_ROWS:
                        continue

                    if labcol != 0:
                        my_name = 'L:X{}Y{}I{}'.format(tileX, tileY, wireI)
                    else:
                        my_name = 'R2:X{}Y{}I{}'.format(tileX, tileY, wireI)

                    if wireI < 4:
                        this_mux_bitdata = getbox(
                            coordXbase + 0,
                            coordYbase + 4 + 4 * wireI)
                    else:
                        this_mux_bitdata = getbox(
                            coordXbase + 0,
                            coordYbase + 28 + 4 * (wireI - 4))

                    print(wireI, this_mux_bitdata)

                    results = set(this_mux_bitdata)
                    assert len(results) == 1 or len(results) == 2
                    if len(results) == 2:
                        assert '??' in results
                        results.remove('??')
                    result = list(results)[0]
                    if labcol != 0:
                        assert e_dirs[result] == 1
                    else:
                        assert e_dirs[result] == 2
                    my_wire_to_quartus_wire[my_name] = result

        with open(outfn, 'w', newline='') as f:
            json.dump(my_wire_to_quartus_wire, f, sort_keys=True,
                      indent=4, separators=(',', ': '))
    elif mode == "dump_routing_my_way":
        wirenamefn = "wire-name-map-{}.json".format(dev)
        with open(wirenamefn, 'r') as f:
            my_wire_to_quartus_wire = json.load(f)
            quartus_wire_to_my_wire = \
                {v: k for k, v in my_wire_to_quartus_wire.items()}

        # FIXME ALL THE COPYPASTA
        outfn = "routing-bits-{}.json".format(dev)
        my_routing_dump = {}

        # FIXME COPYPASTA
        bits_info = []
        for _ in range(CRAM_HEIGHT):
            bits_info.append([None] * (CRAM_WIDTH - 1))

        bits_info_mark = []
        for _ in range(CRAM_HEIGHT):
            bits_info_mark.append([None] * (CRAM_WIDTH - 1))

        # FIXME WE NEED TO CHECK THIS AT SOME POINT??
        # e_num_fanins = {}

        # routing
        for elem_src_i, e in enumerate(route_elems):
            e = route_elems[elem_src_i]
            a = route_bits[elem_src_i]

            elem_src_name = "{}:X{}Y{}S{}I{}".format(
                elem_enum_types[e.m_element_enum], e.x, e.y, e.z, e.index)

            # e_num_fanins[elem_src_name] = len(e.fanins)

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
                    if cur_data is None:
                        new_data = (elem_dst_name, [elem_src_name])
                    else:
                        existing_dst_name, existing_srcs = cur_data
                        assert existing_dst_name == elem_dst_name
                        new_data = (elem_dst_name,
                                    existing_srcs + [elem_src_name])

                    bits_info[alteraY][-alteraX - 1] = new_data

        # print(e_num_fanins)
        # print(bits_info)

        # LEFT HAND SIDE IOs
        print("LEFT HAND IOs (please manually check me)")
        for labrow in range(LONG_ROWS):
            if dev == "240":
                tileX = 1
            else:
                tileX = 0

            tileY = 1 + SHORT_ROWS + labrow

            coordYbase = blockY(tileY)

            for wireI in range(8):
                my_name = 'R:X{}Y{}I{}'.format(tileX, tileY, wireI)

                if wireI % 2 == 0:
                    coordX = 3
                else:
                    coordX = 5

                if wireI // 2 == 0:
                    coordY = coordYbase + 1
                elif wireI // 2 == 1:
                    coordY = coordYbase + 3
                elif wireI // 2 == 2:
                    coordY = coordYbase + 42
                elif wireI // 2 == 3:
                    coordY = coordYbase + 44

                bits_info_mark[coordY][coordX + 0] = True
                bits_info_mark[coordY][coordX + 1] = True
                if bits_info[coordY][coordX + 0] is not None:
                    assert len(bits_info[coordY][coordX + 0][1]) == 1
                    left_src = bits_info[coordY][coordX + 0][1][0]
                else:
                    left_src = "???"
                if bits_info[coordY][coordX + 1] is not None:
                    assert len(bits_info[coordY][coordX + 1][1]) == 1
                    right_src = bits_info[coordY][coordX + 1][1][0]
                else:
                    right_src = "???"

                print("{} srcs: {} {}".format(
                    my_name, left_src, right_src))

        # TOP IOs
        print("*" * 80)
        print("TOP IOs (please manually check me)")
        for iocol in range(LONG_COLS):
            tileY = LONG_ROWS + SHORT_ROWS + 1

            if dev == "240":
                tileX = 2 + iocol
            else:
                tileX = 1 + iocol

            coordXbase = 11 + LAB_WIDTH * iocol

            for wireI in range(10):
                my_name = 'D:X{}Y{}I{}'.format(tileX, tileY, wireI)

                coordY = 1 + 2 * (wireI % 5)
                # print(coordY)

                if wireI < 5:
                    bits_info_mark[coordY + 1][coordXbase + 0] = True
                    bits_info_mark[coordY + 0][coordXbase + 2] = True
                    this_mux_bitdata = [
                        bits_info[coordY + 1][coordXbase + 0],
                        bits_info[coordY + 0][coordXbase + 2],
                    ]
                else:
                    bits_info_mark[coordY + 0][coordXbase + 25] = True
                    bits_info_mark[coordY + 1][coordXbase + 27] = True
                    this_mux_bitdata = [
                        bits_info[coordY + 0][coordXbase + 25],
                        bits_info[coordY + 1][coordXbase + 27],
                    ]

                if this_mux_bitdata[0] is not None:
                    assert len(this_mux_bitdata[0][1]) == 1
                    left_src = this_mux_bitdata[0][1][0]
                else:
                    left_src = "???"
                if this_mux_bitdata[1] is not None:
                    assert len(this_mux_bitdata[1][1]) == 1
                    right_src = this_mux_bitdata[1][1][0]
                else:
                    right_src = "???"

                print("{} srcs: {} {}".format(
                    my_name, left_src, right_src))

        # BOTTOM IOs
        print("*" * 80)
        print("BOTTOM IOs (please manually check me)")
        for iocol in range(LONG_COLS):
            if dev != "240" and iocol == (LONG_COLS - SHORT_COLS - 1):
                continue

            if iocol < (LONG_COLS - SHORT_COLS):
                tileY = SHORT_ROWS
                coordYbase = 11 + LONG_ROWS * LAB_HEIGHT + 1
                # XXX the last +1 is a hack for the clock
            else:
                tileY = 0
                coordYbase = 11 + (LONG_ROWS + SHORT_ROWS) * LAB_HEIGHT + 1
                # XXX the last +1 is a hack for the clock

            if dev == "240":
                tileX = 2 + iocol
            else:
                tileX = 1 + iocol

            coordXbase = 11 + LAB_WIDTH * iocol

            for wireI in range(10):
                my_name = 'U:X{}Y{}I{}'.format(tileX, tileY, wireI)

                coordY = coordYbase + 2 * (wireI % 5)
                # print(coordY)

                if wireI < 5:
                    bits_info_mark[coordY + 0][coordXbase + 0] = True
                    bits_info_mark[coordY + 1][coordXbase + 2] = True
                    this_mux_bitdata = [
                        bits_info[coordY + 0][coordXbase + 0],
                        bits_info[coordY + 1][coordXbase + 2],
                    ]
                else:
                    bits_info_mark[coordY + 1][coordXbase + 25] = True
                    bits_info_mark[coordY + 0][coordXbase + 27] = True
                    this_mux_bitdata = [
                        bits_info[coordY + 1][coordXbase + 25],
                        bits_info[coordY + 0][coordXbase + 27],
                    ]

                if this_mux_bitdata[0] is not None:
                    assert len(this_mux_bitdata[0][1]) == 1
                    left_src = this_mux_bitdata[0][1][0]
                else:
                    left_src = "???"
                if this_mux_bitdata[1] is not None:
                    assert len(this_mux_bitdata[1][1]) == 1
                    right_src = this_mux_bitdata[1][1][0]
                else:
                    right_src = "???"

                print("{} srcs: {} {}".format(
                    my_name, left_src, right_src))

        # MAIN interconnect area
        print("*" * 80)
        print("Processing main routing area...")

        def getbox(x, y):
            return getbox2(x, y)[0]

        def getbox2(x, y):
            ret = []
            out_name = None
            for yy in range(2):
                tmp = []
                for xx in range(4):
                    bits_info_mark[y + yy][x + xx] = True
                    if bits_info[y + yy][x + xx] is None:
                        tmp.append([])
                    else:
                        if out_name is None:
                            out_name = bits_info[y + yy][x + xx][0]
                        else:
                            assert out_name == bits_info[y + yy][x + xx][0]
                        tmp.append(bits_info[y + yy][x + xx][1])
                ret.append(tmp)
            return ret, out_name

        def reformatbox(inbox):
            outdata = {}

            h = len(inbox)
            w = len(inbox[0])

            # print(w, h, inbox)

            for x in range(w):
                for y in range(h):
                    inputs_here = inbox[y][x]
                    for input_ in inputs_here:
                        if input_ in quartus_wire_to_my_wire:
                            input_ = quartus_wire_to_my_wire[input_]

                        if input_ not in outdata:
                            tmp = []
                            for _ in range(h):
                                tmp.append([True] * w)
                            outdata[input_] = tmp

                        outdata[input_][y][x] = False

            return outdata

        for labrow in range(LONG_ROWS + SHORT_ROWS):
            if labrow < SHORT_ROWS:
                numcols = SHORT_COLS
            else:
                numcols = LONG_COLS
            for labcol in range(numcols + 1):
                tileY = 1 + labrow
                if labrow < SHORT_ROWS:
                    tileX = 1 + (LONG_COLS - SHORT_COLS) + labcol
                    coordXbase = 7 + LAB_WIDTH * (
                        labcol + (LONG_COLS - SHORT_COLS))
                else:
                    tileX = 1 + labcol
                    coordXbase = 7 + LAB_WIDTH * labcol
                if dev == "240":
                    tileX += 1

                coordYbase = blockY(tileY)

                print("Working on X{}Y{}".format(tileX, tileY))

                # UP
                for wireI in range(7):
                    my_name = 'U:X{}Y{}I{}'.format(tileX, tileY, wireI)

                    if wireI == 0:
                        this_mux_bitdata = getbox(
                            coordXbase + 0,
                            coordYbase + 0)
                    elif wireI == 1:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 4)
                    elif wireI == 2:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 10)
                    elif wireI == 3:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 16)
                    elif wireI == 4:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 32)
                    elif wireI == 5:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 36)
                    elif wireI == 6:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 42)

                    # print(wireI, this_mux_bitdata)
                    this_mux_routes = reformatbox(this_mux_bitdata)
                    # print(my_name, this_mux_routes)

                    assert len(this_mux_routes) <= 13
                    my_routing_dump[my_name] = this_mux_routes

                # DOWN
                for wireI in range(7):
                    my_name = 'D:X{}Y{}I{}'.format(tileX, tileY, wireI)

                    if wireI == 0:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 2)
                    elif wireI == 1:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 8)
                    elif wireI == 2:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 12)
                    elif wireI == 3:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 28)
                    elif wireI == 4:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 34)
                    elif wireI == 5:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 40)
                    elif wireI == 6:
                        this_mux_bitdata = getbox(
                            coordXbase + 0,
                            coordYbase + 44)

                    this_mux_routes = reformatbox(this_mux_bitdata)

                    assert len(this_mux_routes) <= 13
                    my_routing_dump[my_name] = this_mux_routes

                # RIGHT (except last col which is L2)
                for wireI in range(8):
                    if labcol != numcols:
                        my_name = 'R:X{}Y{}I{}'.format(tileX, tileY, wireI)
                    else:
                        my_name = 'L2:X{}Y{}I{}'.format(tileX, tileY, wireI)

                    if wireI == 0:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 0)
                    elif wireI == 1:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 6)
                    elif wireI == 2:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 14)
                    elif wireI == 3:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 18)
                    elif wireI == 4:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 26)
                    elif wireI == 5:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 30)
                    elif wireI == 6:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 38)
                    elif wireI == 7:
                        this_mux_bitdata = getbox(
                            coordXbase + 4,
                            coordYbase + 44)

                    this_mux_routes = reformatbox(this_mux_bitdata)

                    assert len(this_mux_routes) <= 13
                    my_routing_dump[my_name] = this_mux_routes

                # LEFT (except first col which doesn't have any or
                # the UFM corner which is R2)
                for wireI in range(8):
                    if labcol == 0 and labrow >= SHORT_ROWS:
                        continue

                    if labcol != 0:
                        my_name = 'L:X{}Y{}I{}'.format(tileX, tileY, wireI)
                    else:
                        my_name = 'R2:X{}Y{}I{}'.format(tileX, tileY, wireI)

                    if wireI < 4:
                        this_mux_bitdata = getbox(
                            coordXbase + 0,
                            coordYbase + 4 + 4 * wireI)
                    else:
                        this_mux_bitdata = getbox(
                            coordXbase + 0,
                            coordYbase + 28 + 4 * (wireI - 4))

                    this_mux_routes = reformatbox(this_mux_bitdata)

                    assert len(this_mux_routes) <= 13
                    my_routing_dump[my_name] = this_mux_routes

                # Local interconnect for LABs (except last col which isn't a
                # a LAB)
                if labcol != numcols:
                    for localI in range(26):
                        expected_name = \
                            'LOCAL_INTERCONNECT:X{}Y{}S0I{}'.format(
                                tileX, tileY, localI)

                        if localI < 5:
                            # top right of LUTs
                            this_mux_bitdata, mux_name = getbox2(
                                coordXbase + 28,
                                coordYbase + 2 + 4 * localI)
                        elif localI < 13:
                            # top left of LUTs
                            this_mux_bitdata, mux_name = getbox2(
                                coordXbase + 8,
                                coordYbase + 2 * (localI - 5))
                        elif localI < 18:
                            # bottom right of LUTs
                            this_mux_bitdata, mux_name = getbox2(
                                coordXbase + 28,
                                coordYbase + 42 - 4 * (localI - 13))
                        else:
                            # bottom left of LUTs
                            this_mux_bitdata, mux_name = getbox2(
                                coordXbase + 8,
                                coordYbase + 44 - 2 * (localI - 18))

                        # print(mux_name, expected_name)
                        assert mux_name == expected_name

                        this_mux_routes = reformatbox(this_mux_bitdata)

                        # GCLK workarounds
                        gclk_workaround_y = 0
                        if dev != "240":
                            if tileX == (LONG_COLS - SHORT_COLS):
                                # FIXME WTF IS GOING ON HERE?
                                gclk_workaround_y = 2
                            elif tileX < (LONG_COLS - SHORT_COLS):
                                gclk_workaround_y = SHORT_ROWS
                        # print(tileX, gclk_workaround_y)
                        if localI == 12:
                            bits_info_mark[coordYbase + 16][coordXbase + 10] =\
                                True
                            gclkbit = \
                                bits_info[coordYbase + 16][coordXbase + 10]
                            # print(gclkbit)
                            assert gclkbit[0] == expected_name
                            expected_clks = [
                                'LAB_CLK:X{}Y{}S0I0'.format(
                                    tileX, gclk_workaround_y),
                                'LAB_CLK:X{}Y{}S0I1'.format(
                                    tileX, gclk_workaround_y),
                                'LAB_CLK:X{}Y{}S0I2'.format(
                                    tileX, gclk_workaround_y),
                            ]
                            assert sorted(gclkbit[1]) == expected_clks
                            # print(this_mux_routes)
                            for clk in expected_clks:
                                del this_mux_routes[clk]
                            # print(this_mux_routes)
                        elif localI == 25:
                            bits_info_mark[coordYbase + 29][coordXbase + 10] =\
                                True
                            gclkbit = \
                                bits_info[coordYbase + 29][coordXbase + 10]
                            # print(gclkbit)
                            assert gclkbit[0] == expected_name
                            expected_clks = [
                                'LAB_CLK:X{}Y{}S0I0'.format(
                                    tileX, gclk_workaround_y),
                                'LAB_CLK:X{}Y{}S0I1'.format(
                                    tileX, gclk_workaround_y),
                                'LAB_CLK:X{}Y{}S0I3'.format(
                                    tileX, gclk_workaround_y),
                            ]
                            assert sorted(gclkbit[1]) == expected_clks
                            # print(this_mux_routes)
                            for clk in expected_clks:
                                del this_mux_routes[clk]
                            # print(this_mux_routes)

                        assert len(this_mux_routes) <= 13
                        my_routing_dump[expected_name] = this_mux_routes

        didnt_look_at = set()
        for x in range(CRAM_WIDTH - 1):
            for y in range(CRAM_HEIGHT):
                if not bits_info_mark[y][x]:
                    bit_data = bits_info[y][x]
                    if bit_data is not None:
                        # print("DIDN'T LOOK AT ({}, {}) {}".format(
                        #     x, y, bit_data))
                        didnt_look_at.add(bit_data[0])
        for x in sorted(list(didnt_look_at)):
            print("DIDN'T LOOK AT {}".format(x))


        with open(outfn, 'w', newline='') as f:
            json.dump(my_routing_dump, f, sort_keys=True,
                      indent=4, separators=(',', ': '))
    else:
        print("Invalid mode {}".format(mode))
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: {} dev mode asm.dmp routing.dmp asmdb.dmp".format(
            sys.argv[0]))
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
