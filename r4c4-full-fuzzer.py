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
    # print(all_my_wires)
    # print(len(all_my_wires))

    for direction, dstX, dstY, dstI in all_my_wires:
        this_inputs = {}

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

        all_routes_to_try["{}:X{}Y{}I{}".format(direction, dstX, dstY, dstI)] = this_inputs

    for k, v in all_routes_to_try.items():
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
        if dstnode.startswith("LOCAL_INTERCONNECT"):
            continue
        for srcnode in srcnodes:
            if srcnode.startswith("IO_DATAIN") or srcnode.startswith("LE_BUFFER"):
                continue
            assert all_routes_to_try[dstnode][srcnode] != False
            all_routes_to_try[dstnode][srcnode] = True

    # print(all_routes_to_try)
    with open(outfn, 'w') as f:
        json.dump(all_routes_to_try, f, sort_keys=True, indent=4, separators=(',', ': '))

def main():
    with open('my_wire_to_quartus_wire.json', 'r') as f:
        my_wire_to_quartus_wire = json.load(f)
    quartus_wire_to_my_wire = {v: k for (k, v) in my_wire_to_quartus_wire.items()}

    cmd = sys.argv[1]
    if cmd=='prep':
        prep_all_routes(sys.argv[2], my_wire_to_quartus_wire)
    else:
        raise Exception()

if __name__=='__main__':
    main()
