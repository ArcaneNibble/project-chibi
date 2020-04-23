import os

def my_coords_to_byte_bit(x, y):
    if y < 232:
        intermed_biti = x * 232 + y

        # Seems to work better this way
        intermed_biti += 29
        intermed_biti %= (208 * 232)

        bytegroup_i = intermed_biti // 29
        bytegroup_biti = intermed_biti % 29

        bytegroup_biti += 3

        return (bytegroup_i * 4 + bytegroup_biti // 8, bytegroup_biti % 8)
    else:
        bytegroup_i = (y - 232) // 3
        bytegroup_biti = (y - 232) % 3

        return (bytegroup_i * 4 + x * 32, bytegroup_biti)

LUTYLOCS = [11, 57, 104, 150]

def getbox(data, x, y, w, h):
    ret = []
    for yy in range(h):
        reti = []
        for xx in range(w):
            byte_i, bit_i = my_coords_to_byte_bit(x + xx, y + yy)
            reti.append(bool(data[byte_i] & (1 << bit_i)))
        ret.append(reti)
    return ret

def getbit(data, x, y):
    return getbox(data, x, y, 1, 1)[0][0]

def anybits(bits):
    for y in bits:
        for x in y:
            if not x:
                return True
    return False

def set_bits_in_each(cfmfn, rcffn):
    rcfwires = set()
    cfmwires = set()

    ## RCF dumb parser
    with open(rcffn, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            if l.startswith("C4:") or l.startswith("R4:"):
                if l.endswith(";"):
                    l = l[:-1]
                rcfwires.add(l)

    ## CFM, whee
    with open(cfmfn, 'rb') as f:
        cfmdata = f.read()

    for x in range(3, 9):
        for y in [1, 2, 3, 4]:
            # R4 going left
            for nn in range(4):
                bitsbits = getbox(cfmdata,
                    (x - 1) * 28 - 21,
                    LUTYLOCS[4 - y] + nn * 4 + 4,
                    4, 2)
                if anybits(bitsbits):
                    cfmwires.add("L:X{}Y{}I{}".format(x, y, nn))

                bitsbits = getbox(cfmdata,
                    (x - 1) * 28 - 21,
                    LUTYLOCS[4 - y] + nn * 4 + 28,
                    4, 2)
                if anybits(bitsbits):
                    cfmwires.add("L:X{}Y{}I{}".format(x, y, 4 + nn))

    for x in range(2, 8):
        for y in [1, 2, 3, 4]:
            # R4 going right
            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 0,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("R:X{}Y{}I{}".format(x, y, 0))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 6,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("R:X{}Y{}I{}".format(x, y, 1))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 14,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("R:X{}Y{}I{}".format(x, y, 2))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 18,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("R:X{}Y{}I{}".format(x, y, 3))


            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 26,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("R:X{}Y{}I{}".format(x, y, 4))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 30,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("R:X{}Y{}I{}".format(x, y, 5))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 38,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("R:X{}Y{}I{}".format(x, y, 6))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 44,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("R:X{}Y{}I{}".format(x, y, 7))

    # Extra set of R4 (R1?) going left in the last column
    for y in [1, 2, 3, 4]:
        bitsbits = getbox(cfmdata,
            (8 - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 0,
            4, 2)
        if anybits(bitsbits):
            cfmwires.add("L2:X{}Y{}I{}".format(8, y, 0))

        bitsbits = getbox(cfmdata,
            (8 - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 6,
            4, 2)
        if anybits(bitsbits):
            cfmwires.add("L2:X{}Y{}I{}".format(8, y, 1))

        bitsbits = getbox(cfmdata,
            (8 - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 14,
            4, 2)
        if anybits(bitsbits):
            cfmwires.add("L2:X{}Y{}I{}".format(8, y, 2))

        bitsbits = getbox(cfmdata,
            (8 - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 18,
            4, 2)
        if anybits(bitsbits):
            cfmwires.add("L2:X{}Y{}I{}".format(8, y, 3))


        bitsbits = getbox(cfmdata,
            (8 - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 26,
            4, 2)
        if anybits(bitsbits):
            cfmwires.add("L2:X{}Y{}I{}".format(8, y, 4))

        bitsbits = getbox(cfmdata,
            (8 - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 30,
            4, 2)
        if anybits(bitsbits):
            cfmwires.add("L2:X{}Y{}I{}".format(8, y, 5))

        bitsbits = getbox(cfmdata,
            (8 - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 38,
            4, 2)
        if anybits(bitsbits):
            cfmwires.add("L2:X{}Y{}I{}".format(8, y, 6))

        bitsbits = getbox(cfmdata,
            (8 - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 44,
            4, 2)
        if anybits(bitsbits):
            cfmwires.add("L2:X{}Y{}I{}".format(8, y, 7))

    # Extra set of R4 going right in the first column
    for y in [1, 2, 3, 4]:
        # R4 going right
        bitsbits = getbox(cfmdata,
            3,
            LUTYLOCS[4 - y] + 1,
            2, 1)
        if anybits(bitsbits):
            cfmwires.add("R:X{}Y{}I{}".format(1, y, 0))

        bitsbits = getbox(cfmdata,
            5,
            LUTYLOCS[4 - y] + 1,
            2, 1)
        if anybits(bitsbits):
            cfmwires.add("R:X{}Y{}I{}".format(1, y, 1))


        bitsbits = getbox(cfmdata,
            3,
            LUTYLOCS[4 - y] + 3,
            2, 1)
        if anybits(bitsbits):
            cfmwires.add("R:X{}Y{}I{}".format(1, y, 2))

        bitsbits = getbox(cfmdata,
            5,
            LUTYLOCS[4 - y] + 3,
            2, 1)
        if anybits(bitsbits):
            cfmwires.add("R:X{}Y{}I{}".format(1, y, 3))


        bitsbits = getbox(cfmdata,
            3,
            LUTYLOCS[4 - y] + 42,
            2, 1)
        if anybits(bitsbits):
            cfmwires.add("R:X{}Y{}I{}".format(1, y, 4))

        bitsbits = getbox(cfmdata,
            5,
            LUTYLOCS[4 - y] + 42,
            2, 1)
        if anybits(bitsbits):
            cfmwires.add("R:X{}Y{}I{}".format(1, y, 5))


        bitsbits = getbox(cfmdata,
            3,
            LUTYLOCS[4 - y] + 44,
            2, 1)
        if anybits(bitsbits):
            cfmwires.add("R:X{}Y{}I{}".format(1, y, 6))

        bitsbits = getbox(cfmdata,
            5,
            LUTYLOCS[4 - y] + 44,
            2, 1)
        if anybits(bitsbits):
            cfmwires.add("R:X{}Y{}I{}".format(1, y, 7))


    for x in range(2, 9):
        for y in [1, 2, 3, 4]:
            # C4 up
            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 21,
                LUTYLOCS[4 - y] + 0,
                4, 2)
            if anybits(bitsbits):
                # print(bitsbits)
                cfmwires.add("U:X{}Y{}I{}".format(x, y, 0))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 4,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("U:X{}Y{}I{}".format(x, y, 1))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 10,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("U:X{}Y{}I{}".format(x, y, 2))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 16,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("U:X{}Y{}I{}".format(x, y, 3))


            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 32,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("U:X{}Y{}I{}".format(x, y, 4))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 36,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("U:X{}Y{}I{}".format(x, y, 5))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 42,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("U:X{}Y{}I{}".format(x, y, 6))


            # C4 down
            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 2,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("D:X{}Y{}I{}".format(x, y, 0))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 8,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("D:X{}Y{}I{}".format(x, y, 1))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 12,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("D:X{}Y{}I{}".format(x, y, 2))


            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 28,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("D:X{}Y{}I{}".format(x, y, 3))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 34,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("D:X{}Y{}I{}".format(x, y, 4))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 17,
                LUTYLOCS[4 - y] + 40,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("D:X{}Y{}I{}".format(x, y, 5))

            bitsbits = getbox(cfmdata,
                (x - 1) * 28 - 21,
                LUTYLOCS[4 - y] + 44,
                4, 2)
            if anybits(bitsbits):
                cfmwires.add("D:X{}Y{}I{}".format(x, y, 6))

    # Top IO tiles
    for x in range(2, 8):
        for nn in range(5):
            b0 = getbit(cfmdata,
                (x - 1) * 28 - 15,
                1 + 2 * nn)
            b1 = getbit(cfmdata,
                (x - 1) * 28 - 17,
                2 + 2 * nn)
            if not b0 or not b1:
                cfmwires.add("D:X{}Y{}I{}".format(x, 5, nn))

            b0 = getbit(cfmdata,
                (x - 1) * 28 + 8,
                1 + 2 * nn)
            b1 = getbit(cfmdata,
                (x - 1) * 28 + 10,
                2 + 2 * nn)
            if not b0 or not b1:
                cfmwires.add("D:X{}Y{}I{}".format(x, 5, 5 + nn))

    # Bottom IO tiles
    for x in range(2, 8):
        for nn in range(5):
            b0 = getbit(cfmdata,
                (x - 1) * 28 - 15,
                197 + 2 * nn)
            b1 = getbit(cfmdata,
                (x - 1) * 28 - 17,
                196 + 2 * nn)
            if not b0 or not b1:
                cfmwires.add("U:X{}Y{}I{}".format(x, 0, nn))

            b0 = getbit(cfmdata,
                (x - 1) * 28 + 8,
                197 + 2 * nn)
            b1 = getbit(cfmdata,
                (x - 1) * 28 + 10,
                196 + 2 * nn)
            if not b0 or not b1:
                cfmwires.add("U:X{}Y{}I{}".format(x, 0, 5 + nn))

    if len(cfmwires) != len(rcfwires):
        print("Warning: {} and {} do not have matching wire counts".format(cfmfn, rcffn))
    return (cfmwires, rcfwires)

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
    'manual-more-wire-names-fuzz',
    'manual-more-wire-names-fuzz-2',
    'manual-more-wire-names-fuzz-3',
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
    else:
        raise Exception()

def main():
    all_teh_bits = []

    for workdir_cfm in WORKDIRS:
        print("Working in {}".format(workdir_cfm))
        for fn in os.listdir(workdir_cfm):
            cfmfn = workdir_cfm + '/' + fn
            if not cfmfn.endswith(".bin") and not cfmfn.endswith(".cfm"):
                continue

            rcffn = xlat_cfm_to_pof(cfmfn)
            # print(cfmfn, rcffn)
            # print("Loading {}".format(cfmfn))
            cfmwires, rcfwires = set_bits_in_each(cfmfn, rcffn)
            all_teh_bits.append((cfmfn, cfmwires, rcfwires))

    # print(all_teh_bits)

    all_my_wires = []
    for x in range(1, 9):
        for y in range(0, 6):
            if x == 1:
                if y >= 1 and y <= 4:
                    for nn in range(8):
                        all_my_wires.append("R:X{}Y{}I{}".format(x, y, nn))
            elif x >= 2 and x <= 7:
                if y >= 1 and y <= 4:
                    if x != 2:
                        for nn in range(8):
                            all_my_wires.append("L:X{}Y{}I{}".format(x, y, nn))
                    for nn in range(8):
                        all_my_wires.append("R:X{}Y{}I{}".format(x, y, nn))
                    for nn in range(7):
                        all_my_wires.append("U:X{}Y{}I{}".format(x, y, nn))
                    for nn in range(7):
                        all_my_wires.append("D:X{}Y{}I{}".format(x, y, nn))
                elif y == 0:
                    for nn in range(10):
                        all_my_wires.append("U:X{}Y{}I{}".format(x, y, nn))
                elif y == 5:
                    for nn in range(10):
                        all_my_wires.append("D:X{}Y{}I{}".format(x, y, nn))
            elif x == 8:
                if y >= 1 and y <= 4:
                    for nn in range(8):
                        all_my_wires.append("L:X{}Y{}I{}".format(x, y, nn))
                    for nn in range(8):
                        all_my_wires.append("L2:X{}Y{}I{}".format(x, y, nn))
                    for nn in range(7):
                        all_my_wires.append("U:X{}Y{}I{}".format(x, y, nn))
                    for nn in range(7):
                        all_my_wires.append("D:X{}Y{}I{}".format(x, y, nn))

    # print(all_my_wires)
    # First step - if a mux gets used, it must show up in all the rcf files
    wire_to_potential_sites_map = {}
    for my_wire_name in all_my_wires:
        for cfmfn, cfmwires, rcfwires in all_teh_bits:
            if my_wire_name in cfmwires:
                # print("Found {} in {}".format(my_wire_name, cfmfn))

                if my_wire_name not in wire_to_potential_sites_map:
                    wire_to_potential_sites_map[my_wire_name] = set(rcfwires)
                else:
                    wire_to_potential_sites_map[my_wire_name] &= rcfwires
                    if len(wire_to_potential_sites_map[my_wire_name]) == 0:
                        print("Warning: {} made {} go to zero".format(cfmfn, my_wire_name))

                # print("Possible RCF names for {} now {}".format(my_wire_name, wire_to_potential_sites_map[my_wire_name]))

    # Second step - it must _not_ show up in _any_ rcf files where the mux isn't used
    for my_wire_name in all_my_wires:
        if my_wire_name in wire_to_potential_sites_map:
            all_wires_in_files_not_using_this_wire = set()
            for cfmfn, cfmwires, rcfwires in all_teh_bits:
                if my_wire_name not in cfmwires:
                    all_wires_in_files_not_using_this_wire |= rcfwires

            wire_to_potential_sites_map[my_wire_name] -= all_wires_in_files_not_using_this_wire

    # print(wire_to_potential_sites_map)
    # Now report
    for my_wire_name in all_my_wires:
        print("Wire {}  =  ".format(my_wire_name), end='')
        if my_wire_name not in wire_to_potential_sites_map:
            print("UNKNOWN! PLZ 2 FUZZ MOAR")
        else:
            potential_sites = wire_to_potential_sites_map[my_wire_name]
            if len(potential_sites) == 0:
                print("BAD! Zero sites!")
            elif len(potential_sites) != 1:
                print("Multiple! Fuzz more! {}".format(sorted(list(potential_sites))))
            else:
                print(list(potential_sites)[0])

if __name__=='__main__':
    main()
