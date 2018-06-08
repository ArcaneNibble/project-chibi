import cfmdiff
import cfmdump
import os.path

def main():
    bits = []
    for _ in range(112):
        bits.append([None] * 64)

    ##### Dummy bits?
    for y in range(112):
        bits[y][0] = (b"?0", b"DUMMY0", b"Appears to be constantly 0")
        bits[y][33] = (b"?0", b"DUMMY0", b"Appears to be constantly 0")

    def bits_lookup(x, byteoff):
        byte_i, bit_i = x
        byte_i -= byteoff
        assert byte_i >= 0

        row_i = byte_i // 8
        row_byte = byte_i % 8
        return bits[row_i][row_byte * 8 + bit_i]

    def bits_set(x, byteoff, tup):
        byte_i, bit_i = x
        byte_i -= byteoff
        assert byte_i >= 0

        row_i = byte_i // 8
        row_byte = byte_i % 8
        bits[row_i][row_byte * 8 + bit_i] = tup

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
            bits_set(unsetbits[0], 0xC0, (b"LU", b"LUT", "XnY{}N{} - LUT[0]".format(luty, lutn).encode('ascii')))

            # Set bits are bit 1
            bits_set(setbits[0], 0xC0, (b"LU", b"LUT", "XnY{}N{} - LUT[1]".format(luty, lutn).encode('ascii')))

            for lutbit in range(2, 16):
                setbits, _ = cfmdiff.diffcfm(
                    LUT_FN_TMPL.format(2, luty, lutn, 1),
                    LUT_FN_TMPL.format(2, luty, lutn, 2**lutbit))

                # HACK HACK HACK
                setbits = [x for x in setbits if x[0] >= 0x200]
                # print(setbits)
                assert len(setbits) == 1

                bits_set(setbits[0], 0xC0, (b"LU", b"LUT", "XnY{}N{} - LUT[{}]".format(luty, lutn, lutbit).encode('ascii')))


    ##### Local feedback part of local tracks into LUT inputs

    lut_input_settings = {}

    # Note that this section requires a little bit of cheating. It requires the old code (that was broken) to show
    # the overall structure. This new code then fuzzes based on knowledge obtained from that
    LOCALFEEDBACK_FN_TMPL = "localfeedbackfuzz-cfm/localfeedbackfuzz_X5_Y{}_N{}_DATA{}_from_N{}.pof-cfm.bin"
    for tgtluty in [1, 2, 3, 4]:
        for tgtlutn in range(10):

            starty = [179, 133, 86, 40][tgtluty - 1]
            if tgtlutn < 5:
                offy = tgtlutn * 4
            else:
                offy = (9 - tgtlutn) * 4 + 26

            for tgtlutinp in ['A', 'B', 'C', 'D']:
                if tgtlutinp == 'A':
                    srclutlocs = [3, 4, 5, 6, 8]
                elif tgtlutinp == 'B':
                    srclutlocs = [0, 1, 2, 7, 9]
                elif tgtlutinp == 'C':
                    srclutlocs = [0, 4, 5, 6, 7]
                elif tgtlutinp == 'D':
                    srclutlocs = [1, 2, 3, 8, 9]

                collected_line_to_lut_bits = []

                for srcidx in range(len(srclutlocs)):
                    srclutn = srclutlocs[srcidx]

                    if srclutn == tgtlutn:
                        continue

                    with open(LOCALFEEDBACK_FN_TMPL.format(tgtluty, tgtlutn, tgtlutinp, srclutn), 'rb') as f:
                        bitstream = f.read()

                    col = bitstream[0xB40:0xB40 + 0x380]

                    my_line_to_lut_bits = []
                    for yy in range(4):
                        row = []
                        for xx in range(9):
                            row.append(cfmdump.bit_at_my_coords(col, 13 + xx, starty + offy + yy) != 0)
                        my_line_to_lut_bits.append(row)
                    
                    collected_line_to_lut_bits.append((my_line_to_lut_bits, srclutn))

                common_zero_bits = []
                for yy in range(4):
                    for xx in range(9):
                        allunset = True
                        for inpinp in range(len(collected_line_to_lut_bits)):
                            if collected_line_to_lut_bits[inpinp][0][yy][xx]:
                                allunset = False
                                break
                        if allunset:
                            common_zero_bits.append((xx, yy))
                assert len(common_zero_bits) == 2

                for srcidx in range(len(collected_line_to_lut_bits)):
                    myzerobits = []
                    for yy in range(4):
                        for xx in range(9):
                            if not collected_line_to_lut_bits[srcidx][0][yy][xx] and (xx, yy) not in common_zero_bits:
                                myzerobits.append((xx, yy))
                    assert len(myzerobits) == 2

                    srclutn = collected_line_to_lut_bits[srcidx][1]

                    myrearrangedzerobits = []
                    for lutinx, lutiny in myzerobits:
                        if tgtlutn >= 5:
                            lutiny_ = 3 - lutiny
                        else:
                            lutiny_ = lutiny
                        myrearrangedzerobits.append((lutinx, lutiny_))
                    myrearrangedzerobits.sort()

                    if (tgtlutinp, "N{}".format(srclutn)) in lut_input_settings:
                        assert lut_input_settings[(tgtlutinp, "N{}".format(srclutn))] == myrearrangedzerobits
                    lut_input_settings[(tgtlutinp, "N{}".format(srclutn))] = myrearrangedzerobits

                    for lutinx, lutiny in myzerobits:
                        mycoordx = lutinx + 13
                        mycoordy = lutiny + starty + offy

                        tile_coords_x, tile_coords_y = cfmdump.our_shuffle_coords_to_tile_coords(mycoordx, mycoordy)
                        x = cfmdump.our_tile_coords_to_byte_bit(tile_coords_x, tile_coords_y)

                        origbit = bits_lookup(x, 0)
                        newbit = (b"LI", b"LUTIN", "XnY{}N{} LUT DATA{} source".format(tgtluty, tgtlutn, tgtlutinp).encode('ascii'))
                        if origbit is not None and origbit != newbit:
                            print(origbit)
                        assert origbit is None or origbit == newbit
                        bits_set(x, 0, newbit)

    ##### LAB tracks into LUT inputs
    LABTRACK_FN_TMPL = "lablinefuzz-cfm/labtrackfuzz_X5_Y{}_N{}_DATA{}_from_labline{}.pof-cfm.bin"
    for tgtluty in [1, 2, 3, 4]:
        for tgtlutn in range(10):

            starty = [179, 133, 86, 40][tgtluty - 1]
            if tgtlutn < 5:
                offy = tgtlutn * 4
            else:
                offy = (9 - tgtlutn) * 4 + 26

            for tgtlutinp in ['A', 'B', 'C', 'D']:
                if tgtlutinp == 'A':
                    tracks = [ 0,  1,  3,  6,  8,  9, 11, 14, 15, 18, 19, 22, 25]
                elif tgtlutinp == 'B':
                    tracks = [ 2,  4,  5,  7, 10, 12, 13, 16, 17, 20, 21, 23, 24]
                elif tgtlutinp == 'C':
                    tracks = [ 0,  2,  3,  7,  8,  9, 11, 14, 17, 18, 21, 22, 25]
                elif tgtlutinp == 'D':
                    tracks = [ 1,  4,  5,  6, 10, 12, 13, 15, 16, 19, 20, 23, 24]

                collected_line_to_lut_bits = []

                for srcidx in range(len(tracks)):
                    srctrack = tracks[srcidx]

                    with open(LABTRACK_FN_TMPL.format(tgtluty, tgtlutn, tgtlutinp, srctrack), 'rb') as f:
                        bitstream = f.read()

                    col = bitstream[0xB40:0xB40 + 0x380]

                    my_line_to_lut_bits = []
                    for yy in range(4):
                        row = []
                        for xx in range(9):
                            row.append(cfmdump.bit_at_my_coords(col, 13 + xx, starty + offy + yy) != 0)
                        my_line_to_lut_bits.append(row)
                    
                    collected_line_to_lut_bits.append(my_line_to_lut_bits)

                common_zero_bits = []
                for yy in range(4):
                    for xx in range(9):
                        numunset = 0
                        for inpinp in range(len(collected_line_to_lut_bits)):
                            if not collected_line_to_lut_bits[inpinp][yy][xx]:
                                numunset += 1
                        # ALSO HUGE HACK
                        if numunset >= 6:
                            common_zero_bits.append((xx, yy))

                for srcidx in range(len(collected_line_to_lut_bits)):
                    myzerobits = []
                    # HUGE HACKS
                    if tgtlutinp == 'C' or tgtlutinp == 'D':
                        if tgtlutn < 5:
                            yrange = range(2, 4)
                        else:
                            yrange = range(2)
                    else:
                        yrange = range(4)
                    for yy in yrange:
                        for xx in range(9):
                            if not collected_line_to_lut_bits[srcidx][yy][xx] and (xx, yy) not in common_zero_bits:
                                myzerobits.append((xx, yy))
                    if len(myzerobits) != 2:
                        # print("problem2 {} {} DATA{} line {}".format(tgtluty, tgtlutn, tgtlutinp, tracks[srcidx]))
                        continue

                    myrearrangedzerobits = []
                    for lutinx, lutiny in myzerobits:
                        if tgtlutn >= 5:
                            lutiny_ = 3 - lutiny
                        else:
                            lutiny_ = lutiny
                        myrearrangedzerobits.append((lutinx, lutiny_))
                    myrearrangedzerobits.sort()

                    if (tgtlutinp, "LAB{}".format(tracks[srcidx])) in lut_input_settings:
                        assert lut_input_settings[(tgtlutinp, "LAB{}".format(tracks[srcidx]))] == myrearrangedzerobits
                    lut_input_settings[(tgtlutinp, "LAB{}".format(tracks[srcidx]))] = myrearrangedzerobits

                    for lutinx, lutiny in myzerobits:
                        mycoordx = lutinx + 13
                        mycoordy = lutiny + starty + offy

                        tile_coords_x, tile_coords_y = cfmdump.our_shuffle_coords_to_tile_coords(mycoordx, mycoordy)
                        x = cfmdump.our_tile_coords_to_byte_bit(tile_coords_x, tile_coords_y)

                        origbit = bits_lookup(x, 0)
                        newbit = (b"LI", b"LUTIN", "XnY{}N{} LUT DATA{} source".format(tgtluty, tgtlutn, tgtlutinp).encode('ascii'))
                        if origbit is not None and origbit != newbit:
                            print(origbit, newbit)
                        assert origbit is None or origbit == newbit
                        bits_set(x, 0, newbit)

    # ##### C4 to LAB tracks (only finding involved bits for now)
    # LABTRACK_FN_TMPL = "c4-to-lab-fuzz-Y2-cfm/c4-to-lab-fuzz_X{}Y{}I{}_to_LAB{}.pof-cfm.bin"
    # for x in [4, 5]:
    #     for y in [0, 1, 2, 3, 4, 5]:
    #         for i in range(64):
    #             all_files = []
    #             for lablinei in range(26):
    #                 fn = LABTRACK_FN_TMPL.format(x, y, i, lablinei)
    #                 if os.path.isfile(fn):
    #                     all_files.append(fn)
    #             # print(all_files)
    #             if len(all_files) < 2:
    #                 if len(all_files) == 1:
    #                     print("Oops, can't fuzz C4:X{}Y{}I{} -> LAB{} this way (not enough files)".format(x, y, i, lablinei))
    #                 continue

    #             for filei in range(1, len(all_files)):
    #                 setbits, unsetbits = cfmdiff.diffcfm(all_files[0], all_files[filei])

    #                 # Filter any that are not in the column of interest
    #                 setbits = [x for x in setbits if x[0] >= 0xB40 and x[0] < 0xEC0]
    #                 unsetbits = [x for x in unsetbits if x[0] >= 0xB40 and x[0] < 0xEC0]

    #                 # Filter any that are known to be LUT bits or LUT input bits
    #                 setbits = [x for x in setbits if bits_lookup(x, 0xB40) is None or (bits_lookup(x, 0xB40)[1] != b"LUT" and bits_lookup(x, 0xB40)[1] != b"LUTIN")]
    #                 unsetbits = [x for x in unsetbits if bits_lookup(x, 0xB40) is None or (bits_lookup(x, 0xB40)[1] != b"LUT" and bits_lookup(x, 0xB40)[1] != b"LUTIN")]

    #                 # for byte_i, bit_i in setbits:
    #                 #     print("Bit became   SET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))
    #                 # for byte_i, bit_i in unsetbits:
    #                 #     print("Bit became UNSET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

    #                 for x in setbits:
    #                     bits_set(x, 0xB40, (b"LL", b"LABIN", b"XnY2 LAB line input mux"))
    #                 for x in unsetbits:
    #                     bits_set(x, 0xB40, (b"LL", b"LABIN", b"XnY2 LAB line input mux"))

    # # This one cannot stay; it will definitely false-positive
    # for lablinei in range(26):
    #     all_files = []
    #     for x in [4, 5]:
    #         for y in [0, 1, 2, 3, 4, 5]:
    #             for i in range(64):
    #                 fn = LABTRACK_FN_TMPL.format(x, y, i, lablinei)
    #                 if os.path.isfile(fn):
    #                     all_files.append(fn)
    #     # print(all_files)
    #     if len(all_files) < 2:
    #         if len(all_files) == 1:
    #             print("Oops, can't fuzz C4 -> LAB{} this way (not enough files)".format(lablinei))
    #         continue

    #     for filei in range(1, len(all_files)):
    #         setbits, unsetbits = cfmdiff.diffcfm(all_files[0], all_files[filei])

    #         # Filter any that are not in the column of interest
    #         setbits = [x for x in setbits if x[0] >= 0xB40 and x[0] < 0xEC0]
    #         unsetbits = [x for x in unsetbits if x[0] >= 0xB40 and x[0] < 0xEC0]

    #         # Filter any that are known to be LUT bits or LUT input bits
    #         setbits = [x for x in setbits if bits_lookup(x, 0xB40) is None or (bits_lookup(x, 0xB40)[1] != b"LUT" and bits_lookup(x, 0xB40)[1] != b"LUTIN")]
    #         unsetbits = [x for x in unsetbits if bits_lookup(x, 0xB40) is None or (bits_lookup(x, 0xB40)[1] != b"LUT" and bits_lookup(x, 0xB40)[1] != b"LUTIN")]

    #         # for byte_i, bit_i in setbits:
    #         #     print("Bit became   SET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))
    #         # for byte_i, bit_i in unsetbits:
    #         #     print("Bit became UNSET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

    #         for x in setbits:
    #             bits_set(x, 0xB40, (b"LL", b"LABIN", b"XnY2 LAB line input mux"))
    #         for x in unsetbits:
    #             bits_set(x, 0xB40, (b"LL", b"LABIN", b"XnY2 LAB line input mux"))

    ##### R4 to LAB tracks (only finding involved bits for now)
    R4_LABTRACK_FN_TMPL = "r4-to-lab-fuzz-cfm/r4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.pof-cfm.bin"
    for tiley in [1, 2, 3, 4]:
        for chanx in range(9):
            for chany in [1, 2, 3, 4]:
                for chani in range(64):
                    all_files = []
                    for lablinei in range(26):
                        fn = R4_LABTRACK_FN_TMPL.format(chanx, chany, chani, tiley, lablinei)
                        if os.path.isfile(fn):
                            all_files.append(fn)
                    # print(all_files)
                    if len(all_files) < 2:
                        if len(all_files) == 1:
                            print("Oops, can't fuzz R4:X{}Y{}I{} -> X5Y{} LAB{} this way (not enough files)".format(chanx, chany, chani, tiley, lablinei))
                        continue

                    for filei in range(1, len(all_files)):
                        setbits, unsetbits = cfmdiff.diffcfm(all_files[0], all_files[filei])

                        # Filter any that are not in the column of interest
                        setbits = [x for x in setbits if x[0] >= 0xB40 and x[0] < 0xEC0]
                        unsetbits = [x for x in unsetbits if x[0] >= 0xB40 and x[0] < 0xEC0]

                        # Filter any that are known to be LUT bits or LUT input bits
                        setbits = [x for x in setbits if bits_lookup(x, 0xB40) is None or (bits_lookup(x, 0xB40)[1] != b"LUT" and bits_lookup(x, 0xB40)[1] != b"LUTIN")]
                        unsetbits = [x for x in unsetbits if bits_lookup(x, 0xB40) is None or (bits_lookup(x, 0xB40)[1] != b"LUT" and bits_lookup(x, 0xB40)[1] != b"LUTIN")]

                        # for byte_i, bit_i in setbits:
                        #     print("Bit became   SET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))
                        # for byte_i, bit_i in unsetbits:
                        #     print("Bit became UNSET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0 - 3 * 0x380))

                        for x in setbits:
                            bits_set(x, 0xB40, (b"LL", b"LABIN", b"XnY2 LAB line input mux"))
                        for x in unsetbits:
                            bits_set(x, 0xB40, (b"LL", b"LABIN", b"XnY2 LAB line input mux"))

    print(lut_input_settings)

    tabletabletable = b'<h1>Byte-based arrangement</h1>'

    tabletabletable += b'<table id="thetable">'

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






    tabletabletable += b'<h1>Rearranged tables</h1>'

    tabletabletable += b'<h2>Unknown column bits</h2><table id="rearranged-unkcols">'

    tabletabletable += b'<tr><th>Byte</th><th colspan="3">+0</th><th colspan="3">+4</th></tr>'

    tabletabletable += b'<tr><th>Bit</th>'
    for _ in range(2):
        tabletabletable += b'<th>0</th><th>1</th><th>2</th>'
    tabletabletable += b'</tr>'

    for y in range(112):
        tabletabletable += b'<tr>'

        byterange = "<th>0x{:03X}-0x{:03X}</th>".format(y * 8, y * 8 + 7).encode('ascii')
        tabletabletable += byterange

        for x in [0, 1, 2, 32, 33, 34]:
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

    tabletabletable += b'<h2>"Main" bits</h2><table id="rearranged-superrows">'
    tabletabletable += b'<tr><th></th>'
    for x in range(28):
        tabletabletable += '<th>{}</th>'.format(x).encode('ascii')
    tabletabletable += b'</tr>'
    for y in range(232):
        tabletabletable += b'<tr>'
        tabletabletable += '<th>{}</th>'.format(y).encode('ascii')
        for x in range(28):
            oldy = x * 4 + y // 58
            oldx = y % 58 + 3
            if oldx >= 32:
                oldx += 3

            bit = bits[oldy][oldx]
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
