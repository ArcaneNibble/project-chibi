from cfmdump2 import getbox, getbit, LUTYLOCS
import os
import json
import sys

WORKDIRS = [
    'r4-to-lab-fuzz-cfm',
    'c4-to-lab-fuzz-cfm',
    'c4-to-lab-fuzz-Y2-cfm',
    'localfeedbackfuzz-cfm',
    'lablinefuzz-cfm',
    'lh-io-local-manualfuzz',
    'lh-io-outwire-manualfuzz',
    'rh-io-local-manualfuzz',
    'rh-io-outwire-manualfuzz',
    'top-io-local-manualfuzz',
    'bot-io-outwire-manualfuzz',
    'manual-more-wire-names-fuzz',
    'manual-more-wire-names-fuzz-2',
    'manual-more-wire-names-fuzz-3',
    'r4c4-new-fuzz',
    'lutfuzz2',
    'labr4c4-new-fuzz',
    'neigh-fuzz',
    'row-io-neigh',
    'row-io-to-li',
    'row-io-to-li-wrong',
    'ioout-full-fuzz',
    'lab-self-connection',
    'io-self-connection',
    'top-io-gclk-fuzz',
    'jtagblock',
    'ufmblock',
]

def xlat_cfm_to_pof(cfmfn):
    if cfmfn.startswith('r4-to-lab-fuzz-cfm'):
        return cfmfn[:-11].replace('r4-to-lab-fuzz-cfm', 'r4-to-lab-fuzz-pofrcf') + 'rcf'
    elif cfmfn.startswith('c4-to-lab-fuzz-cfm'):
        return cfmfn[:-11].replace('c4-to-lab-fuzz-cfm', 'c4-to-lab-fuzz-pofrcf') + 'rcf'
    elif cfmfn.startswith('c4-to-lab-fuzz-Y2-cfm'):
        return cfmfn[:-11].replace('c4-to-lab-fuzz-Y2-cfm', 'c4-to-lab-fuzz-Y2-pofrcf') + 'rcf'
    elif cfmfn.startswith('localfeedbackfuzz-cfm'):
        return cfmfn[:-11].replace('localfeedbackfuzz-cfm', 'localfeedbackfuzz-pofrcf') + 'rcf'
    elif cfmfn.startswith('lablinefuzz-cfm'):
        return cfmfn[:-11].replace('lablinefuzz-cfm', 'lablinefuzz-pofrcf') + 'rcf'
    elif cfmfn.startswith('lh-io-local-manualfuzz'):
        return cfmfn[:-3] + 'rcf'
    elif cfmfn.startswith('lh-io-outwire-manualfuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('rh-io-local-manualfuzz'):
        return cfmfn[:-3] + 'rcf'
    elif cfmfn.startswith('rh-io-outwire-manualfuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('top-io-local-manualfuzz'):
        return cfmfn[:-3] + 'rcf'
    elif cfmfn.startswith('manual-more-wire-names-fuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('manual-more-wire-names-fuzz-2'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('manual-more-wire-names-fuzz-3'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('bot-io-outwire-manualfuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('r4c4-new-fuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('lutfuzz2'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('labr4c4-new-fuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('neigh-fuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('row-io-neigh'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('row-io-to-li'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('row-io-to-li-wrong'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('ioout-full-fuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('lab-self-connection'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('io-self-connection'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('top-io-gclk-fuzz'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('jtagblock'):
        return cfmfn[:-7] + 'rcf'
    elif cfmfn.startswith('ufmblock'):
        return cfmfn[:-7] + 'rcf'
    else:
        raise Exception()

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

def anybits(bits):
    for y in bits:
        for x in y:
            if not x:
                return True
    return False

def extract_mux_bits(data, muxname):
    if muxname.startswith("L:"):
        X, Y, I = parse_xyi(muxname)
        # print(X, Y, I)
        
        assert X in range(3, 9)
        assert Y in range(1, 5)
        assert I in range(8)

        boxX = (X - 1) * 28 - 21
        if I < 4:
            boxY = LUTYLOCS[4 - Y] + I * 4 + 4
        else:
            boxY = LUTYLOCS[4 - Y] + (I - 4) * 4 + 28

        return getbox(data, boxX, boxY, 4, 2)

    elif muxname.startswith("L2:"):
        X, Y, I = parse_xyi(muxname)
        # print(X, Y, I)
        
        assert X == 8
        assert Y in range(1, 5)
        assert I in range(8)
        
        boxX = (X - 1) * 28 - 17
        if I == 0:
            boxY = LUTYLOCS[4 - Y] + 0
        elif I == 1:
            boxY = LUTYLOCS[4 - Y] + 6
        elif I == 2:
            boxY = LUTYLOCS[4 - Y] + 14
        elif I == 3:
            boxY = LUTYLOCS[4 - Y] + 18
        elif I == 4:
            boxY = LUTYLOCS[4 - Y] + 26
        elif I == 5:
            boxY = LUTYLOCS[4 - Y] + 30
        elif I == 6:
            boxY = LUTYLOCS[4 - Y] + 38
        elif I == 7:
            boxY = LUTYLOCS[4 - Y] + 44

        return getbox(data, boxX, boxY, 4, 2)

    elif muxname.startswith("R:"):
        X, Y, I = parse_xyi(muxname)
        # print(X, Y, I)
        
        assert X in range(2, 8)
        assert Y in range(1, 5)
        assert I in range(8)
        
        boxX = (X - 1) * 28 - 17
        if I == 0:
            boxY = LUTYLOCS[4 - Y] + 0
        elif I == 1:
            boxY = LUTYLOCS[4 - Y] + 6
        elif I == 2:
            boxY = LUTYLOCS[4 - Y] + 14
        elif I == 3:
            boxY = LUTYLOCS[4 - Y] + 18
        elif I == 4:
            boxY = LUTYLOCS[4 - Y] + 26
        elif I == 5:
            boxY = LUTYLOCS[4 - Y] + 30
        elif I == 6:
            boxY = LUTYLOCS[4 - Y] + 38
        elif I == 7:
            boxY = LUTYLOCS[4 - Y] + 44

        return getbox(data, boxX, boxY, 4, 2)

    elif muxname.startswith("U:"):
        X, Y, I = parse_xyi(muxname)
        # print(X, Y, I)
        
        assert X in range(2, 9)
        assert Y in range(1, 5)
        assert I in range(7)
        
        if I == 0:
            boxX = (X - 1) * 28 - 21
        else:
            boxX = (X - 1) * 28 - 17

        if I == 0:
            boxY = LUTYLOCS[4 - Y] + 0
        elif I == 1:
            boxY = LUTYLOCS[4 - Y] + 4
        elif I == 2:
            boxY = LUTYLOCS[4 - Y] + 10
        elif I == 3:
            boxY = LUTYLOCS[4 - Y] + 16
        elif I == 4:
            boxY = LUTYLOCS[4 - Y] + 32
        elif I == 5:
            boxY = LUTYLOCS[4 - Y] + 36
        elif I == 6:
            boxY = LUTYLOCS[4 - Y] + 42

        return getbox(data, boxX, boxY, 4, 2)

    elif muxname.startswith("D:"):
        X, Y, I = parse_xyi(muxname)
        # print(X, Y, I)
        
        assert X in range(2, 9)
        assert Y in range(1, 5)
        assert I in range(7)
        
        if I == 6:
            boxX = (X - 1) * 28 - 21
        else:
            boxX = (X - 1) * 28 - 17

        if I == 0:
            boxY = LUTYLOCS[4 - Y] + 2
        elif I == 1:
            boxY = LUTYLOCS[4 - Y] + 8
        elif I == 2:
            boxY = LUTYLOCS[4 - Y] + 12
        elif I == 3:
            boxY = LUTYLOCS[4 - Y] + 28
        elif I == 4:
            boxY = LUTYLOCS[4 - Y] + 34
        elif I == 5:
            boxY = LUTYLOCS[4 - Y] + 40
        elif I == 6:
            boxY = LUTYLOCS[4 - Y] + 44

        return getbox(data, boxX, boxY, 4, 2)

    elif muxname.startswith("LOCAL_INTERCONNECT"):
        X, Y, I = parse_xysi(muxname[19:])

        assert X in range(1, 9)
        if X == 1:
            # Left IO
            assert I in range(18)

            boxX = 7
            if I in range(9):
                boxY = LUTYLOCS[4 - Y] + 2 * I + 2
            else:
                boxY = LUTYLOCS[4 - Y] + 2 * (17 - I) + 26

            return getbox(data, boxX, boxY, 4, 2)

        elif X == 8:
            # Right IO
            assert I in range(18)

            boxX = 183
            if I in range(9):
                boxY = LUTYLOCS[4 - Y] + 2 * I + 2
            else:
                boxY = LUTYLOCS[4 - Y] + 2 * (17 - I) + 26

            return getbox(data, boxX, boxY, 4, 2)

        else:
            assert Y in range(6)
            if Y == 0:
                # Bottom IO
                assert I in range(10)

                if I < 5:
                    boxX = (X - 1) * 28 + 3
                    boxY = 196 + 2 * (4 - I)
                else:
                    boxX = (X - 1) * 28 - 13
                    boxY = 196 + 2 * (4 - (I - 5))

                return getbox(data, boxX, boxY, 4, 2)
            elif Y == 5:
                # Top IO
                assert I in range(10)

                if I < 5:
                    boxX = (X - 1) * 28 + 3
                    boxY = 1 + 2 * I
                else:
                    boxX = (X - 1) * 28 - 13
                    boxY = 1 + 2 * (I - 5)

                return getbox(data, boxX, boxY, 4, 2)
            else:
                # Logic
                assert I in range(26)

                if I in range(0, 5) or I in range(13, 18):
                    # To the right of the LUT
                    boxX = (X - 1) * 28 + 7
                    if I in range(0, 5):
                        # Top half
                        boxY = LUTYLOCS[4 - Y] + I * 4 + 2
                    else:
                        # Bottom half
                        boxY = LUTYLOCS[4 - Y] + (17 - I) * 4 + 26
                else:
                    # To the left of the LUT
                    boxX = (X - 1) * 28 - 13
                    if I in range(5, 13):
                        # Top half
                        boxY = LUTYLOCS[4 - Y] + (I - 5) * 2
                    else:
                        # Bottom half
                        boxY = LUTYLOCS[4 - Y] + (25 - I) * 2 + 30

                return getbox(data, boxX, boxY, 4, 2)
    else:
        print("ERROR: Do not understand {}".format(muxname))
        raise Exception()

def handle_file(cfmfn, rcffn, nodes_to_sources_map, quartus_wire_to_my_wire):
    print("Working on {}".format(cfmfn))

    with open(cfmfn, 'rb') as f:
        cfmdata = f.read()

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

                    # print(current_path_lines)

                    for i in range(1, len(current_path_lines)):
                        wire = current_path_lines[i]
                        srcnode = current_path_lines[i - 1]

                        assert wire[-1] == ';'
                        assert srcnode[-1] == ';'
                        wire = wire[:-1]
                        srcnode = srcnode[:-1]

                        if srcnode in quartus_wire_to_my_wire:
                            srcnode_my = quartus_wire_to_my_wire[srcnode]
                        elif srcnode.startswith("IO_DATAIN") or srcnode.startswith("LE_BUFFER") or srcnode.startswith('JTAG_') or srcnode.startswith('UFM_'):
                            srcnode_my = srcnode
                        elif srcnode.startswith("LOCAL_INTERCONNECT"):
                            # HACK
                            assert wire.startswith("IO_DATAOUT") or wire.startswith('JTAG_') or wire.startswith('GLOBAL_CLK_MUX')
                            continue
                        elif srcnode.startswith("CLK_BUFFER") or srcnode.startswith("GLOBAL_CLK_MUX"):
                            assert wire.startswith("GLOBAL_CLK_H")
                            continue
                        elif srcnode.startswith("GLOBAL_CLK_H"):
                            assert wire.startswith("LAB_CLK")
                            continue
                        elif srcnode.startswith("LAB_CLK"):
                            if wire.startswith("LOCAL_INTERCONNECT:X8"):
                                continue
                            srcnode_my = srcnode
                        else:
                            print("ERROR: Do not understand {}".format(srcnode))
                            raise Exception()

                        if wire in quartus_wire_to_my_wire:
                            dstnode_my = quartus_wire_to_my_wire[wire]
                        elif wire.startswith("LOCAL_INTERCONNECT"):
                            dstnode_my = wire
                        elif wire.startswith("IO_BYPASS_OUT"):
                            # HACK
                            continue
                        else:
                            print("ERROR: Do not understand {}".format(wire))
                            raise Exception()

                        # Skip manually-done IO wires
                        if dstnode_my.startswith("R:X1Y"):
                            # print("Skipping manual LH IO wire {}".format(dstnode_my))
                            assert int(dstnode_my[7:]) in range(8)
                            continue
                        if dstnode_my[0:3] == 'U:X' and dstnode_my[4:7] == 'Y0I':
                            # print("Skipping manual bottom IO wire {}".format(dstnode_my))
                            assert int(dstnode_my[3]) in range(2, 8)
                            assert int(dstnode_my[7:]) in range(10)
                            continue
                        if dstnode_my[0:3] == 'D:X' and dstnode_my[4:7] == 'Y5I':
                            # print("Skipping manual top IO wire {}".format(dstnode_my))
                            assert int(dstnode_my[3]) in range(2, 8)
                            assert int(dstnode_my[7:]) in range(10)
                            continue

                        # print("{} -> {}".format(srcnode, wire))
                        print("{} -> {}".format(srcnode_my, dstnode_my))

                        mux_settings = extract_mux_bits(cfmdata, dstnode_my)
                        assert anybits(mux_settings)

                        if dstnode_my not in nodes_to_sources_map:
                            nodes_to_sources_map[dstnode_my] = {srcnode_my: mux_settings}
                        else:
                            dstnode_sources = nodes_to_sources_map[dstnode_my]
                            if srcnode_my in dstnode_sources:
                                assert dstnode_sources[srcnode_my] == mux_settings
                            else:
                                dstnode_sources[srcnode_my] = mux_settings

                    current_path_lines = []
                else:
                    # print(l)
                    current_path_lines.append(l)

def main():
    with open('my_wire_to_quartus_wire.json', 'r') as f:
        my_wire_to_quartus_wire = json.load(f)
    quartus_wire_to_my_wire = {v: k for (k, v) in my_wire_to_quartus_wire.items()}
    # print(quartus_wire_to_my_wire)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'r') as f:
            nodes_to_sources_map = json.load(f)
    else:
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
