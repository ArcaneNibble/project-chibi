#!/usr/bin/env python3

import sys
from collections import namedtuple

route_elem = namedtuple('route_elem', 'x y z index m_element_enum m_length m_metal_layer m_direction fanouts fanins')
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

def main():
    infn = sys.argv[1]

    route_elems = parse_routing(infn)

    for i in range(len(route_elems)):
        e = route_elems[i]
        print("Element {}:".format(i))
        print("    {}:X{}Y{}S{}I{}".format(elem_enum_types[e.m_element_enum], e.x, e.y, e.z, e.index))

        if e.m_direction == 0:
            assert e.m_length == 0 or e.m_length == 1
            assert e.m_metal_layer == 0
            if e.m_length == 1:
                print("    m_length: {}".format(e.m_length))
        else:
            print("    m_length: {}".format(e.m_length))
            print("    m_direction: {}".format(directions[e.m_direction-1]))
            print("    m_metal_layer: {}".format(e.m_metal_layer))

        print("    Fanouts:")
        for x in e.fanouts:
            assert x & 0x80000000 # TODO WHAT DOES THIS DO?
            print("        element {}".format(x & 0x7FFFFFFF))

        print("    Fanins:")
        for x in e.fanins:
            assert x & 0x80000000 # TODO WHAT DOES THIS DO?
            print("        element {}".format(x & 0x7FFFFFFF))

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

                m_route_element_list.append((m_x, m_y, m_fanout_edge_base, m_template))
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

            m_route_element_templates[addr] = (m_element_enum, m_z, m_index, m_length, m_metal_layer, m_direction, m_fanout_list_offsets)
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

                m_node_data.append((m_fanin_edge_base, m_num_fanin_edges, m_starting_offset_idx))
        elif l.endswith('ptr.m_fanin_map.m_offsets\n'):
            num_offsets = int(l[4:12], 16)

            for _ in range(num_offsets):
                l = inlines[i]
                i += 1
                offset = int(l[4:12], 16)

                m_offsets.append(offset)

    assert len(m_route_element_list) == len(m_node_data)

    # put the piesces together
    route_elems = []
    for i in range(len(m_route_element_list)):
        m_x, m_y, m_fanout_edge_base, m_template = m_route_element_list[i]

        m_element_enum, m_z, m_index, m_length, m_metal_layer, m_direction, m_fanout_list_offsets = m_route_element_templates[m_template]

        fanouts = []
        for x in m_fanout_list_offsets:
            x = x + m_fanout_edge_base
            x = x & 0xFFFFFFFF
            fanouts.append(x)

        fanins = []
        m_fanin_edge_base, m_num_fanin_edges, m_starting_offset_idx = m_node_data[i]
        for j in range(m_num_fanin_edges):
            offset = m_offsets[m_starting_offset_idx + j]
            x = m_fanin_edge_base + offset
            x = x & 0xFFFFFFFF
            fanins.append(x)

        route_elems.append(route_elem(m_x, m_y, m_z, m_index, m_element_enum, m_length, m_metal_layer, m_direction, fanouts, fanins))

    return route_elems

if __name__=='__main__':
    main()
