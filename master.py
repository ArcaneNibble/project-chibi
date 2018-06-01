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
