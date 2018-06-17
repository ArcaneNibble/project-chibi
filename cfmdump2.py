import sys

LUTYLOCS = [11, 57, 104, 150]

DATAA_INPUTS = [
    ['N3', (5, 1), (7, 0)],
    ['N4', (1, 1), (6, 0)],
    ['N5', (1, 1), (7, 0)],
    ['N6', (1, 1), (8, 0)],
    ['N8', (5, 1), (8, 0)],
    ['LAB0', (0, 0), (6, 0)],
    ['LAB1', (5, 0), (6, 0)],
    ['LAB3', (0, 0), (7, 0)],
    ['LAB6', (5, 0), (7, 0)],
    ['LAB8', (0, 0), (8, 0)],
    ['LAB9', (0, 1), (6, 0)],
    ['LAB11', (0, 1), (7, 0)],
    ['LAB14', (0, 1), (8, 0)],
    ['LAB15', (5, 0), (8, 0)],
    ['LAB18', (1, 0), (6, 0)],
    ['LAB19', (5, 1), (6, 0)],
    ['LAB22', (1, 0), (7, 0)],
    ['LAB25', (1, 0), (8, 0)],
]

DATAB_INPUTS = [
    ['N0', (2, 1), (7, 1)],
    ['N1', (4, 1), (8, 1)],
    ['N2', (4, 1), (7, 1)],
    ['N7', (2, 1), (6, 1)],
    ['N9', (4, 1), (6, 1)],
    ['LAB2', (2, 0), (8, 1)],
    ['LAB4', (3, 0), (8, 1)],
    ['LAB5', (3, 0), (7, 1)],
    ['LAB7', (2, 0), (7, 1)],
    ['LAB10', (3, 0), (6, 1)],
    ['LAB12', (3, 1), (8, 1)],
    ['LAB13', (3, 1), (7, 1)],
    ['LAB16', (3, 1), (6, 1)],
    ['LAB17', (2, 0), (6, 1)],
    ['LAB20', (4, 0), (8, 1)],
    ['LAB21', (2, 1), (8, 1)],
    ['LAB23', (4, 0), (7, 1)],
    ['LAB24', (4, 0), (6, 1)],
]

DATAC_INPUTS = [
    ['N0', (2, 3), (7, 2)],
    ['N4', (1, 3), (6, 2)],
    ['N5', (1, 3), (7, 2)],
    ['N6', (1, 3), (8, 2)],
    ['N7', (2, 3), (8, 2)],
    ['LAB0', (0, 2), (6, 2)],
    ['LAB2', (2, 2), (6, 2)],
    ['LAB3', (0, 2), (7, 2)],
    ['LAB7', (2, 2), (7, 2)],
    ['LAB8', (0, 2), (8, 2)],
    ['LAB9', (0, 3), (6, 2)],
    ['LAB11', (0, 3), (7, 2)],
    ['LAB14', (0, 3), (8, 2)],
    ['LAB17', (2, 2), (8, 2)],
    ['LAB18', (1, 2), (6, 2)],
    ['LAB21', (2, 3), (6, 2)],
    ['LAB22', (1, 2), (7, 2)],
    ['LAB25', (1, 2), (8, 2)],
]

DATAD_INPUTS = [
    ['N1', (4, 3), (8, 3)],
    ['N2', (4, 3), (7, 3)],
    ['N3', (5, 3), (7, 3)],
    ['N8', (5, 3), (6, 3)],
    ['N9', (4, 3), (6, 3)],
    ['LAB1', (5, 2), (8, 3)],
    ['LAB4', (3, 2), (8, 3)],
    ['LAB5', (3, 2), (7, 3)],
    ['LAB6', (5, 2), (7, 3)],
    ['LAB10', (3, 2), (6, 3)],
    ['LAB12', (3, 3), (8, 3)],
    ['LAB13', (3, 3), (7, 3)],
    ['LAB15', (5, 2), (6, 3)],
    ['LAB16', (3, 3), (6, 3)],
    ['LAB19', (5, 3), (8, 3)],
    ['LAB20', (4, 2), (8, 3)],
    ['LAB23', (4, 2), (7, 3)],
    ['LAB24', (4, 2), (6, 3)],
]

ROW_IO_INPUTS = [
    ['0', (2, 0), (3, 0)],
    ['1', (2, 0), (4, 0)],
    ['2', (2, 0), (3, 1)],

    ['3', (2, 1), (3, 0)],
    ['4', (2, 1), (4, 0)],
    ['5', (2, 1), (3, 1)],

    ['6', (1, 0), (3, 0)],
    ['7', (1, 0), (4, 0)],
    ['8', (1, 0), (3, 1)],

    ['9', (1, 1), (3, 0)],
    ['10', (1, 1), (4, 0)],
    ['11', (1, 1), (3, 1)],

    ['12', (0, 0), (3, 0)],
    ['13', (0, 0), (4, 0)],
    ['14', (0, 0), (3, 1)],

    ['15', (0, 1), (3, 0)],
    ['16', (0, 1), (4, 0)],
    ['17', (0, 1), (3, 1)],
]

COL_IO_INPUTS = [
    ['0', (2, 0), (0, 0)],
    ['UNK 2 !!!', (2, 0), (1, 0)],
    ['1', (2, 0), (1, 1)],

    ['2', (2, 1), (1, 0)],
    ['3', (2, 1), (0, 0)],
    ['4', (2, 1), (1, 1)],

    ['5', (3, 0), (0, 0)],
    ['VDD ???', (3, 0), (1, 0)],
    ['6', (3, 0), (1, 1)],

    ['7', (3, 1), (1, 0)],
    ['8', (3, 1), (0, 0)],
    ['9', (3, 1), (1, 1)],
]

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

def getbox(data, x, y, w, h, fliph=False, flipv=False):
    ret = []
    for yy in range(h) if not flipv else reversed(range(h)):
        reti = []
        for xx in range(w) if not fliph else reversed(range(w)):
            byte_i, bit_i = my_coords_to_byte_bit(x + xx, y + yy)
            reti.append(bool(data[byte_i] & (1 << bit_i)))
        ret.append(reti)
    return ret

def getbit(data, x, y):
    return getbox(data, x, y, 1, 1)[0][0]

def twohot_decode(inp_encoding, box):
    anydriver = False
    anybits = False
    ret = None

    for name, b1, b2 in inp_encoding:
        bit1 = box[b1[1]][b1[0]]
        bit2 = box[b2[1]][b2[0]]

        if not bit1 or not bit2:
            anybits = True

        if not bit1 and not bit2:
            assert not anydriver
            anydriver = True
            ret = name

    if not anydriver:
        assert not anybits
        return "<NONE>"
    return ret

def lut_untwiddle(lutbox):
    b0 = lutbox[3][1]
    b1 = lutbox[3][0]
    b2 = lutbox[2][1]
    b3 = lutbox[2][0]

    b4 = lutbox[2][3]
    b5 = lutbox[2][2]
    b6 = lutbox[3][3]
    b7 = lutbox[3][2]

    b8 = lutbox[1][1]
    b9 = lutbox[1][0]
    b10 = lutbox[0][1]
    b11 = lutbox[0][0]

    b12 = lutbox[1][3]
    b13 = lutbox[1][2]
    b14 = lutbox[0][3]
    b15 = lutbox[0][2]

    lut = 0
    if b0:
        lut |= 1 << 0
    if b1:
        lut |= 1 << 1
    if b2:
        lut |= 1 << 2
    if b3:
        lut |= 1 << 3
    if b4:
        lut |= 1 << 4
    if b5:
        lut |= 1 << 5
    if b6:
        lut |= 1 << 6
    if b7:
        lut |= 1 << 7
    if b8:
        lut |= 1 << 8
    if b9:
        lut |= 1 << 9
    if b10:
        lut |= 1 << 10
    if b11:
        lut |= 1 << 11
    if b12:
        lut |= 1 << 12
    if b13:
        lut |= 1 << 13
    if b14:
        lut |= 1 << 14
    if b15:
        lut |= 1 << 15

    return lut

def dump_logic_col(data, X):
    for Y in range(1, 5):
        lutX = (X - 1) * 28

        # LUTs and inputs
        for N in range(10):
            if N < 5:
                lutY = LUTYLOCS[4 - Y] + N * 4
            else:
                lutY = LUTYLOCS[4 - Y] + 46 - (N - 5) * 4 - 4

            lutbox = getbox(data, lutX, lutY, 4, 4, flipv=N >= 5)
            lutval = lut_untwiddle(lutbox)
            print("LUT X{}Y{}N{}: {:04X}".format(X, Y, N, lutval))

            lutinpbox = getbox(data, lutX - 9, lutY, 9, 4, flipv=N >= 5)
            lutinpa = twohot_decode(DATAA_INPUTS, lutinpbox)
            print("LUT X{}Y{}N{} DATAA: {}".format(X, Y, N, lutinpa))
            lutinpb = twohot_decode(DATAB_INPUTS, lutinpbox)
            print("LUT X{}Y{}N{} DATAB: {}".format(X, Y, N, lutinpb))
            lutinpc = twohot_decode(DATAC_INPUTS, lutinpbox)
            print("LUT X{}Y{}N{} DATAC: {}".format(X, Y, N, lutinpc))
            lutinpd = twohot_decode(DATAD_INPUTS, lutinpbox)
            print("LUT X{}Y{}N{} DATAD: {}".format(X, Y, N, lutinpd))
        print()
    print()

def dump_left_ios(data):
    for Y in range(1, 5):
        for N in range(5):
            localY = LUTYLOCS[4 - Y] + 8 + N * 4
            if N >= 3:
                localY += 8

            print("L IO Y{}N{} invert: {}".format(Y, N,
                not getbit(data, 2, localY + (1 if N < 3 else 0))))

            outbox = getbox(data, 2, localY, 5, 2, fliph=True, flipv=N >= 3)
            outinp = twohot_decode(ROW_IO_INPUTS, outbox)

            if not getbit(data, 1, localY + (1 if N < 3 else 0)):
                print("L IO Y{}N{} output: Bypass path".format(Y, N))
                assert outinp == "<NONE>"
            else:
                print("L IO Y{}N{} output: local track {}".format(Y, N, outinp))
        print()

def dump_right_ios(data):
    for Y in range(1, 5):
        for N in range(5):
            localY = LUTYLOCS[4 - Y] + 8 + N * 4
            if N >= 3:
                localY += 8

            print("R IO Y{}N{} invert: {}".format(Y, N,
                not getbit(data, 191, localY + (1 if N < 3 else 0))))

            outbox = getbox(data, 187, localY, 5, 2, fliph=False, flipv=N >= 3)
            outinp = twohot_decode(ROW_IO_INPUTS, outbox)

            if not getbit(data, 192, localY + (1 if N < 3 else 0)):
                print("R IO Y{}N{} output: Bypass path".format(Y, N))
                assert outinp == "<NONE>"
            else:
                print("R IO Y{}N{} output: local track {}".format(Y, N, outinp))
        print()

def dump_top_ios(data):
    for X in range(2, 8):
        tileX = (X - 1) * 28 - 17

        for N in range(4):
            outpY = 1 if N == 0 or N == 2 else 3

            print("T IO X{}N{} invert: {}".format(X, N,
                not getbit(data, tileX + (11 if N >= 2 else 15), outpY + 1)))

            if N >= 2:
                outbox = getbox(data, tileX + 8, outpY, 4, 2, fliph=True)
            else:
                outbox = getbox(data, tileX + 15, outpY, 5, 2)
                for i in range(len(outbox)):
                    del outbox[i][1]
            # print(outbox)
            outinp = twohot_decode(COL_IO_INPUTS, outbox)

            if not getbit(data, tileX + (12 if N >= 2 else 14), outpY + 1):
                print("T IO X{}N{} output: Bypass path".format(X, N))
                assert outinp == "VDD ???"
            else:
                print("T IO X{}N{} output: local track {}".format(X, N, outinp))
        print()

def dump_bot_ios(data):
    for X in range(2, 8):
        tileX = (X - 1) * 28 - 17

        for N in range(4):
            outpY = 204 if N == 0 or N == 2 else 202

            print("B IO X{}N{} invert: {}".format(X, N,
                not getbit(data, tileX + (11 if N >= 2 else 15), outpY)))

            if N >= 2:
                outbox = getbox(data, tileX + 8, outpY, 4, 2, fliph=True, flipv=True)
            else:
                outbox = getbox(data, tileX + 15, outpY, 5, 2, flipv=True)
                for i in range(len(outbox)):
                    del outbox[i][1]
            # print(outbox)
            outinp = twohot_decode(COL_IO_INPUTS, outbox)

            if not getbit(data, tileX + (12 if N >= 2 else 14), outpY):
                print("B IO X{}N{} output: Bypass path".format(X, N))
                assert outinp == "VDD ???"
            else:
                print("B IO X{}N{} output: local track {}".format(X, N, outinp))
        print()

def main():
    fn = sys.argv[1]

    with open(fn, 'rb') as f:
        data = f.read()

    print("******************** LOGIC COLUMNS ********************")
    for X in range(2, 8):
        dump_logic_col(data, X)

    print("******************** LEFT IOs ********************")
    dump_left_ios(data)

    print("******************** RIGHT IOs ********************")
    dump_right_ios(data)

    print("******************** TOP IOs ********************")
    dump_top_ios(data)

    print("******************** BOTTOM IOs ********************")
    dump_bot_ios(data)

if __name__=='__main__':
    main()
