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

def anybits(bits):
    for y in bits:
        for x in y:
            if not x:
                return True
    return False

def lut_input_decode(inp_encoding, lutinpbox):
    anydriver = False
    anybits = False
    ret = None

    for name, b1, b2 in inp_encoding:
        bit1 = lutinpbox[b1[1]][b1[0]]
        bit2 = lutinpbox[b2[1]][b2[0]]

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
            lutinpa = lut_input_decode(DATAA_INPUTS, lutinpbox)
            print("LUT X{}Y{}N{} DATAA: {}".format(X, Y, N, lutinpa))
            lutinpb = lut_input_decode(DATAB_INPUTS, lutinpbox)
            print("LUT X{}Y{}N{} DATAB: {}".format(X, Y, N, lutinpb))
            lutinpc = lut_input_decode(DATAC_INPUTS, lutinpbox)
            print("LUT X{}Y{}N{} DATAC: {}".format(X, Y, N, lutinpc))
            lutinpd = lut_input_decode(DATAD_INPUTS, lutinpbox)
            print("LUT X{}Y{}N{} DATAD: {}".format(X, Y, N, lutinpd))
        print()
    print()

def main():
    fn = sys.argv[1]

    with open(fn, 'rb') as f:
        data = f.read()

    print("******************** LOGIC COLUMNS ********************")
    for X in range(2, 8):
        dump_logic_col(data, X)

if __name__=='__main__':
    main()
