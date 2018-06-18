from cfmdump2 import getbox, getbit
import os
import json
import sys

WORKDIRS = [
    'r4-to-lab-fuzz-cfm',
]

def xlat_cfm_to_pof(cfmfn):
    if cfmfn.startswith('r4-to-lab-fuzz-cfm'):
        return cfmfn[:-11].replace('r4-to-lab-fuzz-cfm', 'r4-to-lab-fuzz-pofrcf') + 'rcf'
    else:
        raise Exception()

def handle_file(cfmfn, rcffn, nodes_to_sources_map, quartus_wire_to_my_wire):
    print("Working on {}".format(cfmfn))

    inside_signal = False
    current_path_lines = []
    with open(rcffn, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            if not inside_signal:
                if l.startswith("signal_name = "):
                    inside_signal = True
            else:
                if l == "}":
                    inside_signal = False
                    # print("end of signal")

                    assert current_path_lines[-1].startswith("dest = ")
                    del current_path_lines[-1]

                    print(current_path_lines)

                    for i in range(1, len(current_path_lines)):
                        wire = current_path_lines[i]
                        srcnode = current_path_lines[i - 1]

                        assert wire[-1] == ';'
                        assert srcnode[-1] == ';'
                        wire = wire[:-1]
                        srcnode = srcnode[:-1]

                        if srcnode in quartus_wire_to_my_wire:
                            srcnode_my = quartus_wire_to_my_wire[srcnode]
                        elif srcnode.startswith("IO_DATAIN") or srcnode.startswith("LE_BUFFER"):
                            srcnode_my = srcnode
                        elif srcnode.startswith("LOCAL_INTERCONNECT"):
                            # HACK
                            assert wire.startswith("IO_DATAOUT")
                            continue
                        else:
                            print("ERROR: Do not understand {}".format(srcnode))
                            raise Exception()

                        if wire in quartus_wire_to_my_wire:
                            dstnode_my = quartus_wire_to_my_wire[wire]
                        elif wire.startswith("LOCAL_INTERCONNECT"):
                            dstnode_my = wire
                        else:
                            print("ERROR: Do not understand {}".format(wire))
                            raise Exception()

                        # print("{} -> {}".format(srcnode, wire))
                        print("{} -> {}".format(srcnode_my, dstnode_my))

                        if dstnode_my not in nodes_to_sources_map:
                            nodes_to_sources_map[dstnode_my] = {srcnode_my: "TODOTODO"}
                        else:
                            dstnode_sources = nodes_to_sources_map[dstnode_my]
                            if srcnode_my in dstnode_sources:
                                # TODO: Check that it's the same
                                ...
                            else:
                                dstnode_sources[srcnode_my] = "TODOTODO"

                    current_path_lines = []
                else:
                    # print(l)
                    current_path_lines.append(l)

def main():
    with open('my_wire_to_quartus_wire.json', 'r') as f:
        my_wire_to_quartus_wire = json.load(f)
    quartus_wire_to_my_wire = {v: k for (k, v) in my_wire_to_quartus_wire.items()}
    # print(quartus_wire_to_my_wire)

    nodes_to_sources_map = {}

    for workdir_cfm in WORKDIRS:
        print("Working in {}".format(workdir_cfm))
        for fn in os.listdir(workdir_cfm):
            cfmfn = workdir_cfm + '/' + fn
            if not cfmfn.endswith(".bin") and not cfmfn.endswith(".cfm"):
                continue

            rcffn = xlat_cfm_to_pof(cfmfn)

            handle_file(cfmfn, rcffn, nodes_to_sources_map, quartus_wire_to_my_wire)

            # break

    # print(nodes_to_sources_map)
    if len(sys.argv) < 2:
        outfn = "initial-interconnect.json"
    else:
        outfn = sys.argv[1]
    with open(outfn, 'w') as f:
        json.dump(nodes_to_sources_map, f, sort_keys=True, indent=4, separators=(',', ': '))

if __name__=='__main__':
    main()
