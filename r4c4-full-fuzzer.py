import sys
import json

def prep_all_routes(outfn, my_wire_to_quartus_wire):
    all_routes_to_try = {}

    all_my_wires = []
    for x in range(2, 9):
        for y in range(1, 5):
            if x >= 2 and x <= 7:
                if x != 2:
                    for nn in range(8):
                        all_my_wires.append(('L', x, y, nn))
                for nn in range(8):
                    all_my_wires.append(('R', x, y, nn))
                for nn in range(7):
                    all_my_wires.append(('U', x, y, nn))
                for nn in range(7):
                    all_my_wires.append(('D', x, y, nn))
            elif x == 8:
                for nn in range(8):
                    all_my_wires.append(('L', x, y, nn))
                for nn in range(8):
                    all_my_wires.append(('L2', x, y, nn))
                for nn in range(7):
                    all_my_wires.append(('U', x, y, nn))
                for nn in range(7):
                    all_my_wires.append(('D', x, y, nn))
    # Local interconnect into the IO cells
    for y in range(1, 5):
        for nn in range(18):
            all_my_wires.append(('LOCAL_INTERCONNECT', 1, y, nn))
            all_my_wires.append(('LOCAL_INTERCONNECT', 8, y, nn))
    for x in range(2, 8):
        for nn in range(10):
            all_my_wires.append(('LOCAL_INTERCONNECT', x, 0, nn))
            all_my_wires.append(('LOCAL_INTERCONNECT', x, 5, nn))
    # print(all_my_wires)
    # print(len(all_my_wires))

    for direction, dstX, dstY, dstI in all_my_wires:
        this_inputs = {}

        if direction == "LOCAL_INTERCONNECT" and (dstY == 0 or dstY == 5):
            # Column local interconnect
            if dstI < 5:
                # Next column hack
                dstX += 1

            for srcY in range(1, 5):
                for srcI in range(7):
                    this_inputs["U:X{}Y{}I{}".format(dstX, srcY, srcI)] = "maybe"
                    this_inputs["D:X{}Y{}I{}".format(dstX, srcY, srcI)] = "maybe"
            # "Left" part of the bottom IOs in this column
            if dstX != 8:
                for srcI in range(5):
                    this_inputs["U:X{}Y0I{}".format(dstX, srcI)] = "maybe"
            # "Right" part of the bottom IOs in the column to the left
            if dstX != 2:
                for srcI in range(5):
                    this_inputs["U:X{}Y0I{}".format(dstX - 1, srcI + 5)] = "maybe"
            # "Left" part of the top IOs in this column
            if dstX != 8:
                for srcI in range(5):
                    this_inputs["D:X{}Y5I{}".format(dstX, srcI)] = "maybe"
            # "Right" part of the top IOs in the column to the left
            if dstX != 2:
                for srcI in range(5):
                    this_inputs["D:X{}Y5I{}".format(dstX - 1, srcI + 5)] = "maybe"

            if dstI < 5:
                # Next column hack
                dstX -= 1
        else:
            if direction == "LOCAL_INTERCONNECT" and dstX == 1:
                # HACK
                dstX = 2

            # All up wires below this
            for srcY in range(1, dstY + 1):
                for srcI in range(7):
                    this_inputs["U:X{}Y{}I{}".format(dstX, srcY, srcI)] = "maybe"
            # "Left" part of the bottom IOs in this column
            if dstX != 8:
                for srcI in range(5):
                    this_inputs["U:X{}Y0I{}".format(dstX, srcI)] = "maybe"
            # "Right" part of the bottom IOs in the column to the left
            if dstX != 2:
                for srcI in range(5):
                    this_inputs["U:X{}Y0I{}".format(dstX - 1, srcI + 5)] = "maybe"

            # All down wires above this
            for srcY in range(dstY, 5):
                for srcI in range(7):
                    this_inputs["D:X{}Y{}I{}".format(dstX, srcY, srcI)] = "maybe"
            # "Left" part of the top IOs in this column
            if dstX != 8:
                for srcI in range(5):
                    this_inputs["D:X{}Y5I{}".format(dstX, srcI)] = "maybe"
            # "Right" part of the top IOs in the column to the left
            if dstX != 2:
                for srcI in range(5):
                    this_inputs["D:X{}Y5I{}".format(dstX - 1, srcI + 5)] = "maybe"

            # All right wires to the left of this (including IOs)
            for srcX in range(1, min(8, dstX + 1)):
                for srcI in range(8):
                    this_inputs["R:X{}Y{}I{}".format(srcX, dstY, srcI)] = "maybe"

            # All left wires to the right of this (IOs not fully understood)
            for srcX in range(max(3, dstX), 9):
                for srcI in range(8):
                    this_inputs["L:X{}Y{}I{}".format(srcX, dstY, srcI)] = "maybe"
            for srcI in range(8):
                this_inputs["L2:X8Y{}I{}".format(dstY, srcI)] = "maybe"

        if direction == "LOCAL_INTERCONNECT":
            if dstX == 2 and dstY != 0 and dstY != 5:
                dstX = 1
            all_routes_to_try["{}:X{}Y{}S0I{}".format(direction, dstX, dstY, dstI)] = this_inputs
        else:
            all_routes_to_try["{}:X{}Y{}I{}".format(direction, dstX, dstY, dstI)] = this_inputs

    for k, v in all_routes_to_try.items():
        if k.startswith("LOCAL_INTERCONNECT"):
            continue
        if k not in my_wire_to_quartus_wire:
            print(k)
        assert k in my_wire_to_quartus_wire
        for k in v:
            if k not in my_wire_to_quartus_wire:
                print(k)
            assert k in my_wire_to_quartus_wire

    # What do we already know?
    with open('initial-interconnect.json', 'r') as f:
        initial_interconnect_map = json.load(f)

    for dstnode, srcnodes in initial_interconnect_map.items():
        if dstnode.startswith("LOCAL_INTERCONNECT") and dstnode not in all_routes_to_try:
            continue
        for srcnode in srcnodes:
            if srcnode.startswith("IO_DATAIN") or srcnode.startswith("LE_BUFFER"):
                continue
            # print(dstnode, srcnode)
            assert all_routes_to_try[dstnode][srcnode] != False
            all_routes_to_try[dstnode][srcnode] = True

    # print(all_routes_to_try)
    with open(outfn, 'w') as f:
        json.dump(all_routes_to_try, f, sort_keys=True, indent=4, separators=(',', ': '))

def parse_xyi(inp):
    xpos = inp.find('X')
    ypos = inp.find('Y')
    ipos = inp.find('I')

    assert xpos >= 0
    assert ypos > xpos
    assert ipos > ypos

    return (int(inp[xpos + 1:ypos]), int(inp[ypos + 1:ipos]), int(inp[ipos + 1:]))

def parse_xysi(inp):
    xpos = inp.find('X')
    ypos = inp.find('Y')
    spos = inp.find('S')
    ipos = inp.find('I')

    assert xpos >= 0
    assert ypos > xpos
    assert spos > ypos
    assert ipos > spos

    sval = int(inp[spos + 1:ipos])
    assert sval == 0

    return (int(inp[xpos + 1:ypos]), int(inp[ypos + 1:spos]), int(inp[ipos + 1:]))

def route_to_output(routing_graph_srcs_dsts, node):
    fringe = []
    closed_set = set()

    fringe.append((node, []))

    while len(fringe) > 0:
        work_node, cur_path = fringe[0]
        del fringe[0]

        # Is this an output?
        is_an_output = False
        if work_node.startswith("LOCAL_INTERCONNECT"):
            X, Y, I = parse_xysi(work_node[19:])
            if (X == 1 or X == 8):
                assert Y in range(1, 5)
                assert I in range(18)
                is_an_output = True
            elif (Y == 0 or Y == 5):
                assert X in range(2, 8)
                assert I in range(10)
                is_an_output = True
            else:
                # It's not a local interconnect we care about right now (goes to LUT)
                continue

        if is_an_output:
            return cur_path + [work_node]

        # Not an output
        for dst in routing_graph_srcs_dsts[work_node]:
            if dst not in closed_set:
                fringe.append((dst, cur_path + [work_node]))

        closed_set.add(dst)

    return None

def route_to_input(routing_graph_dsts_srcs, node, extra_closed_nodes=[]):
    fringe = []
    closed_set = set()

    closed_set |= set(extra_closed_nodes)

    fringe.append((node, []))

    while len(fringe) > 0:
        work_node, cur_path = fringe[0]
        del fringe[0]

        # Is this an input?
        is_an_input = False
        if work_node.startswith("LE_BUFFER"):
            continue
        elif work_node.startswith("IO_DATAIN"):
            is_an_input = True
        elif work_node.startswith("R:"):
            X, _, _ = parse_xyi(work_node)
            if X == 1:
                is_an_input = True
        elif work_node.startswith("D:"):
            _, Y, _ = parse_xyi(work_node)
            if Y == 5:
                is_an_input = True
        elif work_node.startswith("U:"):
            _, Y, _ = parse_xyi(work_node)
            if Y == 0:
                is_an_input = True

        if is_an_input:
            return cur_path + [work_node]

        # Not an input
        for src in routing_graph_dsts_srcs[work_node]:
            if src not in closed_set:
                fringe.append((src, cur_path + [work_node]))

        closed_set.add(src)

    return None

def do_fuzz(inp_state_fn, inp_route_fn, my_wire_to_quartus_wire):
    with open(inp_state_fn, 'r') as f:
        fuzzing_state = json.load(f)
    with open(inp_route_fn, 'r') as f:
        # Index first by dst, then by src
        # Lists ways to get _onto_ a wire
        routing_graph_dsts_srcs = json.load(f)

    # print(routing_graph_dsts_srcs)

    # Invert the routing graph
    routing_graph_srcs_dsts = {}
    for dst, srcs in routing_graph_dsts_srcs.items():
        for src in srcs:
            # print(dst, src)
            if src not in routing_graph_srcs_dsts:
                routing_graph_srcs_dsts[src] = {dst}
            else:
                routing_graph_srcs_dsts[src].add(dst)

    # print(routing_graph_srcs_dsts)
    with open("debug-invert-graph.json", 'w') as f:
        json.dump({k: list(v) for k, v in routing_graph_srcs_dsts.items()}, f, sort_keys=True, indent=4, separators=(',', ': '))

    print(route_to_output(routing_graph_srcs_dsts, "LOCAL_INTERCONNECT:X2Y0S0I9"))
    print(route_to_output(routing_graph_srcs_dsts, "D:X2Y1I0"))
    print(route_to_output(routing_graph_srcs_dsts, "L:X3Y1I0"))

    print(route_to_input(routing_graph_dsts_srcs, "R:X1Y1I0"))
    print(route_to_input(routing_graph_dsts_srcs, "R:X4Y1I1"))
    print(route_to_input(routing_graph_dsts_srcs, "U:X8Y1I3"))
    print(route_to_input(routing_graph_dsts_srcs, "U:X8Y1I3", ["R:X4Y1I1"]))

def main():
    with open('my_wire_to_quartus_wire.json', 'r') as f:
        my_wire_to_quartus_wire = json.load(f)
    quartus_wire_to_my_wire = {v: k for (k, v) in my_wire_to_quartus_wire.items()}

    cmd = sys.argv[1]
    if cmd=='prep':
        prep_all_routes(sys.argv[2], my_wire_to_quartus_wire)
    elif cmd=='fuzz':
        do_fuzz(sys.argv[2], sys.argv[3], my_wire_to_quartus_wire)
    else:
        raise Exception()

if __name__=='__main__':
    main()
