import cfmdiff

def main():
    bits = []
    for _ in range(112):
        bits.append([None] * 64)

    ##### Dummy bits?
    for y in range(112):
        bits[y][0] = (b"?0", b"DUMMY0", b"Appears to be constantly 0")
        bits[y][33] = (b"?0", b"DUMMY0", b"Appears to be constantly 0")

    ##### LUT bits
    LUT_FN_TMPL = "lutfuzz-cfm/lutfuzz_X{}_Y{}_N{}_bits{:04X}.pof-cfm.bin"
    for luty in [1, 2, 3, 4]:
        for lutn in range(10):
            # Zero and one are special
            setbits, unsetbits = cfmdiff.diffcfm(
                LUT_FN_TMPL.format(2, luty, lutn, 1),
                LUT_FN_TMPL.format(2, luty, lutn, 2))
            # print(setbits, unsetbits)

            assert len(setbits) == 1
            assert len(unsetbits) == 1

            # Unset bits are bit 0
            byte_i, bit_i = unsetbits[0]
            byte_i -= 0xC0
            assert byte_i >= 0

            row_i = byte_i // 8
            row_byte = byte_i % 8
            bits[row_i][row_byte * 8 + bit_i] = (b"LU", b"LUT", "XnY{}N{} - LUT[0]".format(luty, lutn).encode('ascii'))

            # Set bits are bit 1
            byte_i, bit_i = setbits[0]
            byte_i -= 0xC0
            assert byte_i >= 0

            row_i = byte_i // 8
            row_byte = byte_i % 8
            bits[row_i][row_byte * 8 + bit_i] = (b"LU", b"LUT", "XnY{}N{} - LUT[1]".format(luty, lutn).encode('ascii'))

            for lutbit in range(2, 16):
                setbits, _ = cfmdiff.diffcfm(
                    LUT_FN_TMPL.format(2, luty, lutn, 1),
                    LUT_FN_TMPL.format(2, luty, lutn, 2**lutbit))

                # HACK HACK HACK
                setbits = [x for x in setbits if x[0] >= 0x200]
                # print(setbits)
                assert len(setbits) == 1

                byte_i, bit_i = setbits[0]
                byte_i -= 0xC0
                assert byte_i >= 0

                row_i = byte_i // 8
                row_byte = byte_i % 8
                bits[row_i][row_byte * 8 + bit_i] = (b"LU", b"LUT", "XnY{}N{} - LUT[{}]".format(luty, lutn, lutbit).encode('ascii'))

    ##### Local feedback track to LUT inputs
    LOCALFEEDBACK_FN_TMPL = "localfeedbackfuzz-cfm/localfeedbackfuzz_X5_Y{}_N{}_DATA{}_from_N{}.pof-cfm.bin"
    for tgtluty in [1, 2, 3, 4]:
        for tgtlutinp in ['A', 'B', 'C', 'D']:

            if tgtlutinp == 'A':
                srclutlocs = [3, 4, 5, 6, 8]
            elif tgtlutinp == 'B':
                srclutlocs = [0, 1, 2, 7, 9]
            elif tgtlutinp == 'C':
                srclutlocs = [0, 4, 5, 6, 7]
            elif tgtlutinp == 'D':
                srclutlocs = [1, 2, 3, 8, 9]

            overall_control_bits_for_entering_this_input = list()
            for _ in range(10):
                overall_control_bits_for_entering_this_input.append(set())

            # Compare this input use with all of the other inputs used
            for first_comp_choice_idx in range(5):
                for second_comp_choice_idx in range(5):
                    if first_comp_choice_idx == second_comp_choice_idx:
                        continue

                    setunset_results = []
                    for tgtlutn in range(10):
                        if srclutlocs[first_comp_choice_idx] == tgtlutn:
                            continue
                        if srclutlocs[second_comp_choice_idx] == tgtlutn:
                            continue

                        # print("comparing {} {}".format(
                        #     LOCALFEEDBACK_FN_TMPL.format(tgtluty, tgtlutn, tgtlutinp, srclutlocs[first_comp_choice_idx]),
                        #     LOCALFEEDBACK_FN_TMPL.format(tgtluty, tgtlutn, tgtlutinp, srclutlocs[second_comp_choice_idx])))

                        setbits, unsetbits = cfmdiff.diffcfm(
                            LOCALFEEDBACK_FN_TMPL.format(tgtluty, tgtlutn, tgtlutinp, srclutlocs[first_comp_choice_idx]),
                            LOCALFEEDBACK_FN_TMPL.format(tgtluty, tgtlutn, tgtlutinp, srclutlocs[second_comp_choice_idx]))

                        # Filter any that are not in the column of interest
                        setbits = [x for x in setbits if x[0] >= 0xB40 and x[0] < 0xEC0]
                        unsetbits = [x for x in unsetbits if x[0] >= 0xB40 and x[0] < 0xEC0]

                        # Filter any that are known to be LUT bits
                        setbits = [x for x in setbits if bits[(x[0] - 0xB40) // 8][(x[0] - 0xB40) % 8 + x[1]] is None]
                        unsetbits = [x for x in unsetbits if bits[(x[0] - 0xB40) // 8][(x[0] - 0xB40) % 8 + x[1]] is None]

                        # for byte_i, bit_i in setbits:
                        #     print("Bit became   SET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

                        # for byte_i, bit_i in unsetbits:
                        #     print("Bit became UNSET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

                        setunset_results.append([setbits, unsetbits, tgtlutn])

                    common_setbits = []
                    for setbit_in_0 in setunset_results[0][0]:
                        notfound = False
                        for i in range(1, len(setunset_results)):
                            if setbit_in_0 not in setunset_results[i][0]:
                                notfound = True
                                break
                        if not notfound:
                            common_setbits.append(setbit_in_0)
                    common_unsetbits = []
                    for unsetbit_in_0 in setunset_results[0][1]:
                        notfound = False
                        for i in range(1, len(setunset_results)):
                            if unsetbit_in_0 not in setunset_results[i][1]:
                                notfound = True
                                break
                        if not notfound:
                            common_unsetbits.append(unsetbit_in_0)

                    # print("*" * 80)

                    # print("Common to change from N{} to N{} via DATA{} into Nx".format(srclutlocs[first_comp_choice_idx], srclutlocs[second_comp_choice_idx], tgtlutinp))

                    # for byte_i, bit_i in common_setbits:
                    #     print("Bit became   SET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

                    # for byte_i, bit_i in common_unsetbits:
                    #     print("Bit became UNSET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

                    # Filter for the things _not_ in common
                    for i in range(len(setunset_results)):
                        setunset_results[i][0] = [x for x in setunset_results[i][0] if x not in common_setbits]
                        setunset_results[i][1] = [x for x in setunset_results[i][1] if x not in common_unsetbits]

                    # for x in setunset_results:
                    #     # if x[2] != 0:
                    #     #     continue

                    #     print("Unique to change from N{} to N{} via DATA{} into N{}".format(srclutlocs[first_comp_choice_idx], srclutlocs[second_comp_choice_idx], tgtlutinp, x[2]))

                    #     for byte_i, bit_i in x[0]:
                    #         print("Bit became   SET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

                    #     for byte_i, bit_i in x[1]:
                    #         print("Bit became UNSET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

                    for x in setunset_results:
                        for bit in x[0]:
                            overall_control_bits_for_entering_this_input[x[2]].add(bit)
                        for bit in x[1]:
                            overall_control_bits_for_entering_this_input[x[2]].add(bit)

            for i in range(len(overall_control_bits_for_entering_this_input)):
                overall_control_bits_for_entering_this_input[i] = sorted(list(overall_control_bits_for_entering_this_input[i]))
            for n in range(len(overall_control_bits_for_entering_this_input)):
                assert len(overall_control_bits_for_entering_this_input[i]) == 5
                for byte_i, bit_i in overall_control_bits_for_entering_this_input[i]:
                    print("Bit at 0x{:04X} bit {} ({:03X}) is important for entering Y{}N{} DATA{}".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380, tgtluty, n, tgtlutinp))

    tabletabletable = b'<table id="thetable">'

    tabletabletable += b'<tr><th>Byte</th><th colspan="8">+0</th><th colspan="8">+1</th><th colspan="8">+2</th><th colspan="8">+3</th><th colspan="8">+4</th><th colspan="8">+5</th><th colspan="8">+6</th><th colspan="8">+7</th></tr>'

    tabletabletable += b'<tr><th>Bit</th>'
    for _ in range(8):
        tabletabletable += b'<th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th>'
    tabletabletable += b'</tr>'

    for y in range(112):
        tabletabletable += b'<tr>'

        byterange = "<th>0x{:03X}-0x{:03X}</th>".format(y * 8, y * 8 + 7).encode('ascii')
        tabletabletable += byterange

        for x in range(64):
            bit = bits[y][x]
            if bit is None:
                tabletabletable += b'<td>?</td>'
            else:
                shortdesc, bitclass, longdesc = bit

                tooltip = b'<div class="tooltip">' + shortdesc + \
                    b'<span class="tooltiptext">' + longdesc + b'</span></div>'

                tabletabletable += b'<td class="' + bitclass + b'">' + tooltip + b'</td>'
        tabletabletable += b'</tr>'
    tabletabletable += b'</table>'

    # print(bits)
    with open("tmpl.html", "rb") as f:
        TMPL = f.read()

    outoutout = TMPL.replace(b'_____CONTENTHERE_____', tabletabletable)
    with open("outoutout.html", "wb") as f:
        f.write(outoutout)

if __name__=='__main__':
    main()
