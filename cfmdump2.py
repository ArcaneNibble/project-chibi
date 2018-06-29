import sys
import json

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
#     ['UNK 2 !!!', (2, 0), (1, 0)],
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

LH_IO_TRACK_MUX = [
    ["N3", "N2"],   ["N3", "N2"],
    ["UNK !!!", "N0"],   ["UNK !!!", "N0"],
    ["N2", "UNK !!!"],   ["N2", "UNK !!!"],
    ["N1", "UNK !!!"],   ["N1", "UNK !!!"],
]

BOT_IO_TRACK_MUX = [
    ["N3", "N0"],
    ["N3", "N1"],
    ["N2", "N0"],
    ["N3", "N2"],
    ["N1", "N0"],
]

EVEN_CONTROL_MUX_INPUTS = [
    ['LAB0', (6, 0), (0, 0)],
    ['LAB2', (6, 0), (2, 0)],
    ['LAB3', (7, 0), (0, 0)],
    ['LAB7', (7, 0), (2, 0)],
    ['LAB8', (8, 0), (0, 0)],
    ['LAB9', (6, 0), (0, 1)],
    ['LAB11', (7, 0), (0, 1)],
    ['LAB14', (8, 0), (0, 1)],
    ['LAB17', (8, 0), (2, 0)],
    ['LAB18', (6, 0), (1, 0)],
    ['LAB21', (6, 0), (2, 1)],
    ['LAB22', (7, 0), (1, 0)],
    ['LAB25', (8, 0), (1, 0)],

    ['N0', (7, 0), (2, 1)],
    ['N4', (6, 0), (1, 1)],
    ['N5', (7, 0), (1, 1)],
    ['N6', (8, 0), (1, 1)],
    ['N7', (8, 0), (2, 1)],
]

ODD_CONTROL_MUX_INPUTS = [
    ['LAB1', (8, 1), (5, 0)],
    ['LAB4', (8, 1), (3, 0)],
    ['LAB5', (7, 1), (3, 0)],
    ['LAB6', (7, 1), (5, 0)],
    ['LAB10', (6, 1), (3, 0)],
    ['LAB12', (8, 1), (3, 1)],
    ['LAB13', (7, 1), (3, 1)],
    ['LAB15', (6, 1), (5, 0)],
    ['LAB16', (6, 1), (3, 1)],
    ['LAB19', (8, 1), (5, 1)],
    ['LAB20', (8, 1), (4, 0)],
    ['LAB23', (7, 1), (4, 0)],
    ['LAB24', (6, 1), (4, 0)],

    ['N1', (8, 1), (4, 1)],
    ['N2', (7, 1), (4, 1)],
    ['N3', (7, 1), (5, 1)],
    ['N8', (6, 1), (5, 1)],
    ['N9', (6, 1), (4, 1)],
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
        return None
    return ret

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

def dump_logic_col(interconnect_map, data, X):
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
            if lutinpa is not None:
                print("LUT X{}Y{}N{} DATAA: {}".format(X, Y, N, lutinpa))


            lutinpb = twohot_decode(DATAB_INPUTS, lutinpbox)
            if lutinpb is not None:
                print("LUT X{}Y{}N{} DATAB: {}".format(X, Y, N, lutinpb))


            lutinpc = twohot_decode(DATAC_INPUTS, lutinpbox)

            usecin = not getbit(data, lutX + 5, lutY + (0 if N < 5 else 3))
            useqfbk = not getbit(data, lutX + 4, lutY + (0 if N < 5 else 3))

            assert not (usecin and useqfbk)
            if usecin or useqfbk:
                assert lutinpc is None
            if usecin:
                print("LUT X{}Y{}N{} DATAC: using cin".format(X, Y, N))
            if useqfbk:
                print("LUT X{}Y{}N{} DATAC: using register feedback".format(X, Y, N))
            if lutinpc is not None:
                print("LUT X{}Y{}N{} DATAC: {}".format(X, Y, N, lutinpc))


            lutinpd = twohot_decode(DATAD_INPUTS, lutinpbox)

            lutchain = getbit(data, lutX + 4, lutY + (3 if N < 5 else 0))

            if lutchain:
                assert lutinpd is None
                print("LUT X{}Y{}N{} DATAD: LUT chain".format(X, Y, N))
            else:
                if lutinpd is not None:
                    print("LUT X{}Y{}N{} DATAD: {}".format(X, Y, N, lutinpd))

            if getbit(data, lutX + 5, lutY + (1 if N < 5 else 2)):
                print("LE X{}Y{}N{} Buffer 0: Register".format(X, Y, N))
            else:
                print("LE X{}Y{}N{} Buffer 0: LUT".format(X, Y, N))
            if getbit(data, lutX + 4, lutY + (1 if N < 5 else 2)):
                print("LE X{}Y{}N{} Buffer 1: Register".format(X, Y, N))
            else:
                print("LE X{}Y{}N{} Buffer 1: LUT".format(X, Y, N))
            if getbit(data, lutX + 6, lutY + (3 if N < 5 else 0)):
                print("LE X{}Y{}N{} Local line: Register".format(X, Y, N))
            else:
                print("LE X{}Y{}N{} Local line: LUT".format(X, Y, N))

            if getbit(data, lutX + 5, lutY + (2 if N < 5 else 1)):
                print("LE X{}Y{}N{} is using register cascade".format(X, Y, N))

            synchmode = not getbit(data, lutX + 6, lutY + (0 if N < 5 else 3))
            if synchmode:
                print("LE X{}Y{}N{} register is using synchronous mode".format(X, Y, N))

            if getbit(data, lutX + 4, lutY + (2 if N < 5 else 1)):
                print("LE X{}Y{}N{} register is using local clock line 0".format(X, Y, N))
            else:
                print("LE X{}Y{}N{} register is using local clock line 1".format(X, Y, N))

            if getbit(data, lutX + 5, lutY + (3 if N < 5 else 0)):
                print("LE X{}Y{}N{} register is using local aclr line 0".format(X, Y, N))
            else:
                print("LE X{}Y{}N{} register is using local aclr line 1".format(X, Y, N))

            if not getbit(data, lutX + 6, lutY + (1 if N < 5 else 2)):
                # Unknown bit
                assert False
            if not getbit(data, lutX + 6, lutY + (2 if N < 5 else 1)):
                # Unknown bit
                assert False

            print()
        print()

        # Control muxes
        for i in range(6):
            boxY = LUTYLOCS[4 - Y] + 20 + 2 * (i // 2)
            controlmuxbox = getbox(data, lutX - 9, boxY, 9, 2)
            if i % 2 == 0:
                controlmuxinp = twohot_decode(EVEN_CONTROL_MUX_INPUTS, controlmuxbox)
            else:
                controlmuxinp = twohot_decode(ODD_CONTROL_MUX_INPUTS, controlmuxbox)
            if controlmuxinp is not None:
                print("LAB X{}Y{} ControlMux{}: {}".format(X, Y, i, controlmuxinp))
        print()

        # Control gunk
        muxalpha = getbit(data, lutX + 1, LUTYLOCS[4 - Y] + 20)
        muxbeta = getbit(data, lutX, LUTYLOCS[4 - Y] + 22)
        muxgamma = getbit(data, lutX - 10, LUTYLOCS[4 - Y] + 20)
        muxdelta = getbit(data, lutX - 10, LUTYLOCS[4 - Y] + 25)
        muxepsilon = getbit(data, lutX + 2, LUTYLOCS[4 - Y] + 20)
        muxzeta = getbit(data, lutX + 1, LUTYLOCS[4 - Y] + 22)
        muxeta = getbit(data, lutX, LUTYLOCS[4 - Y] + 24)
        muxtheta = getbit(data, lutX, LUTYLOCS[4 - Y] + 23)
        inverteta = not getbit(data, lutX + 5, LUTYLOCS[4 - Y] + 24)

        clock0_gclk0 = not getbit(data, lutX - 12, LUTYLOCS[4 - Y] + 18)
        clock0_gclk1 = not getbit(data, lutX - 12, LUTYLOCS[4 - Y] + 19)
        clock0_gclk2 = not getbit(data, lutX - 12, LUTYLOCS[4 - Y] + 27)
        clock0_gclk3 = not getbit(data, lutX - 12, LUTYLOCS[4 - Y] + 26)
        clock0_local = not getbit(data, lutX, LUTYLOCS[4 - Y] + 20)
        clock0_invert = not getbit(data, lutX, LUTYLOCS[4 - Y] + 21)

        assert clock0_gclk0 + clock0_gclk1 + clock0_gclk2 + clock0_gclk3 + clock0_local <= 1
        if clock0_gclk0:
            print("LAB X{}Y{} local clock line 0: GCLK0".format(X, Y))
        if clock0_gclk1:
            print("LAB X{}Y{} local clock line 0: GCLK1".format(X, Y))
        if clock0_gclk2:
            print("LAB X{}Y{} local clock line 0: GCLK2".format(X, Y))
        if clock0_gclk3:
            print("LAB X{}Y{} local clock line 0: GCLK3".format(X, Y))
        if clock0_local:
            if muxalpha:
                print("LAB X{}Y{} local clock line 0: ControlMux1".format(X, Y))
            else:
                print("LAB X{}Y{} local clock line 0: ControlMux0".format(X, Y))
        if clock0_invert:
            print("LAB X{}Y{} local clock line 0 is inverted".format(X, Y))

        clock1_gclk0 = not getbit(data, lutX - 11, LUTYLOCS[4 - Y] + 18)
        clock1_gclk1 = not getbit(data, lutX - 11, LUTYLOCS[4 - Y] + 19)
        clock1_gclk2 = not getbit(data, lutX - 11, LUTYLOCS[4 - Y] + 27)
        clock1_gclk3 = not getbit(data, lutX - 11, LUTYLOCS[4 - Y] + 26)
        clock1_local = not getbit(data, lutX + 1, LUTYLOCS[4 - Y] + 23)
        clock1_invert = not getbit(data, lutX + 4, LUTYLOCS[4 - Y] + 22)

        assert clock1_gclk0 + clock1_gclk1 + clock1_gclk2 + clock1_gclk3 + clock1_local <= 1
        if clock1_gclk0:
            print("LAB X{}Y{} local clock line 1: GCLK0".format(X, Y))
        if clock1_gclk1:
            print("LAB X{}Y{} local clock line 1: GCLK1".format(X, Y))
        if clock1_gclk2:
            print("LAB X{}Y{} local clock line 1: GCLK2".format(X, Y))
        if clock1_gclk3:
            print("LAB X{}Y{} local clock line 1: GCLK3".format(X, Y))
        if clock1_local:
            if muxbeta:
                print("LAB X{}Y{} local clock line 1: ControlMux2".format(X, Y))
            else:
                print("LAB X{}Y{} local clock line 1: ControlMux3".format(X, Y))
        if clock1_invert:
            print("LAB X{}Y{} local clock line 1 is inverted".format(X, Y))


        aclr_gclk0 = not getbit(data, lutX - 10, LUTYLOCS[4 - Y] + 18)
        aclr_gclk1 = not getbit(data, lutX - 10, LUTYLOCS[4 - Y] + 19)
        aclr_gclk2 = not getbit(data, lutX - 10, LUTYLOCS[4 - Y] + 27)
        aclr_gclk3 = not getbit(data, lutX - 10, LUTYLOCS[4 - Y] + 26)
        assert aclr_gclk0 + aclr_gclk1 + aclr_gclk2 + aclr_gclk3 <= 1
        aclr_gclk = None
        if aclr_gclk0:
            aclr_gclk = "GCLK0"
        if aclr_gclk1:
            aclr_gclk = "GCLK1"
        if aclr_gclk2:
            aclr_gclk = "GCLK2"
        if aclr_gclk3:
            aclr_gclk = "GCLK3"

        aclr0_local = getbit(data, lutX, LUTYLOCS[4 - Y] + 25)
        aclr0_disable = not getbit(data, lutX + 6, LUTYLOCS[4 - Y] + 25)
        aclr0_invert = getbit(data, lutX + 6, LUTYLOCS[4 - Y] + 24)
        if not aclr0_disable:
            if not aclr0_local:
                assert aclr_gclk is not None
                print("LAB X{}Y{} local aclr line 0: {}".format(X, Y, aclr_gclk))
            else:
                if muxgamma:
                    print("LAB X{}Y{} local aclr line 0: ControlMux4".format(X, Y))
                else:
                    print("LAB X{}Y{} local aclr line 0: ControlMux5".format(X, Y))
            if aclr0_invert:
                print("LAB X{}Y{} local aclr line 0 is inverted".format(X, Y))

        aclr1_local = getbit(data, lutX + 5, LUTYLOCS[4 - Y] + 21)
        aclr1_disable = not getbit(data, lutX + 5, LUTYLOCS[4 - Y] + 25)
        aclr1_invert = getbit(data, lutX + 6, LUTYLOCS[4 - Y] + 23)
        if not aclr1_disable:
            if not aclr1_local:
                assert aclr_gclk is not None
                print("LAB X{}Y{} local aclr line 1: {}".format(X, Y, aclr_gclk))
            else:
                if muxdelta:
                    print("LAB X{}Y{} local aclr line 1: ControlMux4".format(X, Y))
                else:
                    print("LAB X{}Y{} local aclr line 1: ControlMux5".format(X, Y))
            if aclr1_invert:
                print("LAB X{}Y{} local aclr line 1 is inverted".format(X, Y))

        aload_disable = getbit(data, lutX + 6, LUTYLOCS[4 - Y] + 22)
        aload_invert = not getbit(data, lutX + 4, LUTYLOCS[4 - Y] + 25)
        if not aload_disable:
            if muxbeta:
                print("LAB X{}Y{} local aload line: ControlMux2".format(X, Y))
            else:
                print("LAB X{}Y{} local aload line: ControlMux3".format(X, Y))
            if aload_invert:
                print("LAB X{}Y{} local aload line is inverted".format(X, Y))


        ena_disable_0 = not getbit(data, lutX + 1, LUTYLOCS[4 - Y] + 24)
        ena_invert_0 = not getbit(data, lutX + 1, LUTYLOCS[4 - Y] + 21)
        if not ena_disable_0:
            if muxzeta:
                print("LAB X{}Y{} local ena line 0: ControlMux2".format(X, Y))
            else:
                print("LAB X{}Y{} local ena line 0: ControlMux3".format(X, Y))
            if ena_invert_0:
                print("LAB X{}Y{} local ena line 0 is inverted".format(X, Y))

        ena_disable_1 = not getbit(data, lutX + 4, LUTYLOCS[4 - Y] + 20)
        if not ena_disable_1:
            if muxepsilon:
                print("LAB X{}Y{} local ena line 1: ControlMux1".format(X, Y))
            else:
                print("LAB X{}Y{} local ena line 1: ControlMux0".format(X, Y))
            if inverteta:
                print("LAB X{}Y{} local ena line 1 is inverted".format(X, Y))

        sync_load_disable = getbit(data, lutX + 4, LUTYLOCS[4 - Y] + 21)
        sync_load_tieoff_vcc = getbit(data, lutX + 5, LUTYLOCS[4 - Y] + 20)
        assert not (sync_load_tieoff_vcc and not sync_load_disable)
        if sync_load_tieoff_vcc:
            print("LAB X{}Y{} local sload line: VCC".format(X, Y))
        if not sync_load_disable:
            if muxepsilon:
                print("LAB X{}Y{} local sload line: ControlMux1".format(X, Y))
            else:
                print("LAB X{}Y{} local sload line: ControlMux0".format(X, Y))
            if inverteta:
                print("LAB X{}Y{} local sload line is inverted".format(X, Y))

        sync_clear_disable = getbit(data, lutX + 6, LUTYLOCS[4 - Y] + 20)
        sync_clear_invert = not getbit(data, lutX + 6, LUTYLOCS[4 - Y] + 21)
        if not sync_clear_disable:
            if muxeta:
                print("LAB X{}Y{} local sclr line: ControlMux4".format(X, Y))
            else:
                print("LAB X{}Y{} local sclr line: ControlMux5".format(X, Y))
            if sync_clear_invert:
                print("LAB X{}Y{} local sclr line is inverted".format(X, Y))

        inverta_disable = getbit(data, lutX + 5, LUTYLOCS[4 - Y] + 22)
        inverta_to_cin0 = not getbit(data, lutX + 7, LUTYLOCS[4 - Y] + 24)
        if not inverta_disable:
            if muxtheta:
                print("LAB X{}Y{} local inverta line: ControlMux3".format(X, Y))
            else:
                print("LAB X{}Y{} local inverta line: ControlMux4".format(X, Y))
        if inverta_to_cin0:
                print("LAB X{}Y{} inverta is driving LE0 cin".format(X, Y))

        print()

        # Local interconnect
        for labI in range(26):
            muxname = "LOCAL_INTERCONNECT:X{}Y{}S0I{}".format(X, Y, labI)
            muxbits = extract_mux_bits(data, muxname)

            used_gclk = False
            if labI == 12:
                if not getbit(data, lutX - 11, LUTYLOCS[4 - Y] + 16):
                    if muxbits == [[True, True, True, True], [True, True, True, False]]:
                        print("LAB{}: GCLK0".format(labI))
                        used_gclk = True
                    elif muxbits == [[True, True, True, False], [True, True, True, True]]:
                        print("LAB{}: GCLK1".format(labI))
                        used_gclk = True
                    elif muxbits == [[True, True, False, True], [True, True, True, True]]:
                        print("LAB{}: GCLK2".format(labI))
                        used_gclk = True
                    else:
                        assert False
            if labI == 25:
                if not getbit(data, lutX - 11, LUTYLOCS[4 - Y] + 29):
                    if muxbits == [[True, True, True, False], [True, True, True, True]]:
                        print("LAB{}: GCLK0".format(labI))
                        used_gclk = True
                    elif muxbits == [[True, True, True, True], [True, True, True, False]]:
                        print("LAB{}: GCLK1".format(labI))
                        used_gclk = True
                    elif muxbits == [[True, True, True, True], [True, True, False, True]]:
                        print("LAB{}: GCLK3".format(labI))
                        used_gclk = True
                    else:
                        assert False

            if not used_gclk:
                if anybits(muxbits):
                    found_name = None
                    for srcname, srcbits in interconnect_map[muxname].items():
                        if srcbits == muxbits:
                            assert found_name is None
                            found_name = srcname
                    if found_name is None:
                        raise Exception("Unknown mux setting")
                    print("LAB{}: {}".format(labI, found_name))
        print()

        # R
        for trackI in range(8):
            muxname = "R:X{}Y{}I{}".format(X, Y, trackI)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    raise Exception("Unknown mux setting")
                print("{}: {}".format(muxname, found_name))
        print()

        # L
        if X != 2:
            for trackI in range(8):
                muxname = "L:X{}Y{}I{}".format(X, Y, trackI)
                muxbits = extract_mux_bits(data, muxname)
                if anybits(muxbits):
                    found_name = None
                    for srcname, srcbits in interconnect_map[muxname].items():
                        if srcbits == muxbits:
                            assert found_name is None
                            found_name = srcname
                    if found_name is None:
                        raise Exception("Unknown mux setting")
                    print("{}: {}".format(muxname, found_name))
            print()

        # U
        for trackI in range(7):
            muxname = "U:X{}Y{}I{}".format(X, Y, trackI)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    raise Exception("Unknown mux setting")
                print("{}: {}".format(muxname, found_name))
        print()

        # D
        for trackI in range(7):
            muxname = "D:X{}Y{}I{}".format(X, Y, trackI)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    raise Exception("Unknown mux setting")
                print("{}: {}".format(muxname, found_name))
        print()
    print()

def dump_left_ios(interconnect_map, data, busholdbits, pullupbits, slewratebits, lowcurrentbits):
    for Y in range(1, 5):
        for N in range(4):
            localY = LUTYLOCS[4 - Y] + 8 + N * 4
            if N >= 3:
                localY += 8

            slewbitloc = slewratebits['IOC_X{}_Y{}_N{}'.format(1, Y, N)]
            slew_is_slow = getbit(data, slewbitloc[0], slewbitloc[1])
            if slew_is_slow:
                print("L IO Y{}N{} slew: slow".format(Y, N))
            else:
                print("L IO Y{}N{} slew: fast".format(Y, N))

            pullupbitloc = pullupbits['IOC_X{}_Y{}_N{}'.format(1, Y, N)]
            pullup_is_enabled = not getbit(data, pullupbitloc[0], pullupbitloc[1])
            if pullup_is_enabled:
                print("L IO Y{}N{} pullup enabled".format(Y, N))

            busholdbitloc = busholdbits['IOC_X{}_Y{}_N{}'.format(1, Y, N)]
            bushold_is_enabled = not getbit(data, busholdbitloc[0], busholdbitloc[1])
            if bushold_is_enabled:
                print("L IO Y{}N{} bus hold enabled".format(Y, N))

            currentbitlocs = lowcurrentbits['IOC_X{}_Y{}_N{}'.format(1, Y, N)]
            currentbit1 = getbit(data, currentbitlocs[0][0], currentbitlocs[0][1])
            currentbit2 = getbit(data, currentbitlocs[1][0], currentbitlocs[1][1])
            assert currentbit1 == currentbit2
            if currentbit1 and currentbit2:
                print("L IO Y{}N{} drive strength: high".format(Y, N))
            else:
                print("L IO Y{}N{} drive strength: low".format(Y, N))

            print("L IO Y{}N{} invert: {}".format(Y, N,
                not getbit(data, 2, localY + (1 if N < 3 else 0))))

            outbox = getbox(data, 2, localY, 5, 2, fliph=True, flipv=N >= 3)
            outinp = twohot_decode(ROW_IO_INPUTS, outbox)

            if not getbit(data, 1, localY + (1 if N < 3 else 0)):
                print("L IO Y{}N{} output: Bypass path".format(Y, N))
                assert outinp is None
            else:
                if outinp is not None:
                    print("L IO Y{}N{} output: local track {}".format(Y, N, outinp))
        print()

        # Local interconnect
        for II in range(18):
            muxname = "LOCAL_INTERCONNECT:X1Y{}S0I{}".format(Y, II)
            muxbits = extract_mux_bits(data, muxname)

            used_gclk = False
            if II == 8:
                if not getbit(data, 10, LUTYLOCS[4 - Y] + 20):
                    if muxbits == [[True, True, True, True], [False, True, True, True]]:
                        print("Local {}: GCLK0".format(II))
                        used_gclk = True
                    elif muxbits == [[False, True, True, True], [True, True, True, True]]:
                        print("Local {}: GCLK1".format(II))
                        used_gclk = True
                    elif muxbits == [[True, False, True, True], [True, True, True, True]]:
                        print("Local {}: GCLK2".format(II))
                        used_gclk = True
                    else:
                        assert False
            if II == 17:
                if not getbit(data, 10, LUTYLOCS[4 - Y] + 25):
                    if muxbits == [[False, True, True, True], [True, True, True, True]]:
                        print("Local {}: GCLK0".format(II))
                        used_gclk = True
                    elif muxbits == [[True, True, True, True], [False, True, True, True]]:
                        print("Local {}: GCLK1".format(II))
                        used_gclk = True
                    elif muxbits == [[True, True, True, True], [True, False, True, True]]:
                        print("Local {}: GCLK3".format(II))
                        used_gclk = True
                    else:
                        assert False

            if not used_gclk:
                if anybits(muxbits):
                    found_name = None
                    for srcname, srcbits in interconnect_map[muxname].items():
                        if srcbits == muxbits:
                            assert found_name is None
                            found_name = srcname
                    if found_name is None:
                        raise Exception("Unknown mux setting")
                    print("Local {}: {}".format(II, found_name))
        print()

        # Routing tracks
        for N in range(8):
            if N < 2:
                trackY = LUTYLOCS[4 - Y] + 1
            elif N < 4:
                trackY = LUTYLOCS[4 - Y] + 3
            elif N < 6:
                trackY = LUTYLOCS[4 - Y] + 42
            elif N < 8:
                trackY = LUTYLOCS[4 - Y] + 44

            trackX = 3 if N % 2 == 0 else 5

            bitL = getbit(data, trackX + 0, trackY)
            bitR = getbit(data, trackX + 1, trackY)

            assert not (not bitL and not bitR)

            if not bitL:
                outp = LH_IO_TRACK_MUX[N][0]
            elif not bitR:
                outp = LH_IO_TRACK_MUX[N][1]
            else:
                outp = None

            if outp is not None:
                print("Wire R:X1Y{}I{} = {}".format(Y, N, outp))

        print()

def dump_right_ios(interconnect_map, data, busholdbits, pullupbits, slewratebits, lowcurrentbits):
    for Y in range(1, 5):
        for N in range(5 if Y != 2 else 4):
            localY = LUTYLOCS[4 - Y] + 8 + N * 4
            if N >= 3:
                localY += 8

            slewbitloc = slewratebits['IOC_X{}_Y{}_N{}'.format(8, Y, N)]
            slew_is_slow = getbit(data, slewbitloc[0], slewbitloc[1])
            if slew_is_slow:
                print("R IO Y{}N{} slew: slow".format(Y, N))
            else:
                print("R IO Y{}N{} slew: fast".format(Y, N))

            pullupbitloc = pullupbits['IOC_X{}_Y{}_N{}'.format(8, Y, N)]
            pullup_is_enabled = not getbit(data, pullupbitloc[0], pullupbitloc[1])
            if pullup_is_enabled:
                print("R IO Y{}N{} pullup enabled".format(Y, N))

            busholdbitloc = busholdbits['IOC_X{}_Y{}_N{}'.format(8, Y, N)]
            bushold_is_enabled = not getbit(data, busholdbitloc[0], busholdbitloc[1])
            if bushold_is_enabled:
                print("R IO Y{}N{} bus hold enabled".format(Y, N))

            currentbitlocs = lowcurrentbits['IOC_X{}_Y{}_N{}'.format(8, Y, N)]
            currentbit1 = getbit(data, currentbitlocs[0][0], currentbitlocs[0][1])
            currentbit2 = getbit(data, currentbitlocs[1][0], currentbitlocs[1][1])
            assert currentbit1 == currentbit2
            if currentbit1 and currentbit2:
                print("R IO Y{}N{} drive strength: high".format(Y, N))
            else:
                print("R IO Y{}N{} drive strength: low".format(Y, N))

            print("R IO Y{}N{} invert: {}".format(Y, N,
                not getbit(data, 191, localY + (1 if N < 3 else 0))))

            outbox = getbox(data, 187, localY, 5, 2, fliph=False, flipv=N >= 3)
            outinp = twohot_decode(ROW_IO_INPUTS, outbox)

            if not getbit(data, 192, localY + (1 if N < 3 else 0)):
                print("R IO Y{}N{} output: Bypass path".format(Y, N))
                assert outinp is None
            else:
                if outinp is not None:
                    print("R IO Y{}N{} output: local track {}".format(Y, N, outinp))
        print()

        # Local interconnect
        for II in range(18):
            muxname = "LOCAL_INTERCONNECT:X8Y{}S0I{}".format(Y, II)
            muxbits = extract_mux_bits(data, muxname)

            used_gclk = False
            if II == 8:
                if not getbit(data, 186, LUTYLOCS[4 - Y] + 20):
                    if muxbits == [[True, True, True, True], [True, True, True, False]]:
                        print("Local {}: GCLK0".format(II))
                        used_gclk = True
                    elif muxbits == [[True, True, True, False], [True, True, True, True]]:
                        print("Local {}: GCLK1".format(II))
                        used_gclk = True
                    elif muxbits == [[True, True, False, True], [True, True, True, True]]:
                        print("Local {}: GCLK2".format(II))
                        used_gclk = True
                    else:
                        assert False
            if II == 17:
                if not getbit(data, 186, LUTYLOCS[4 - Y] + 25):
                    if muxbits == [[True, True, True, False], [True, True, True, True]]:
                        print("Local {}: GCLK0".format(II))
                        used_gclk = True
                    elif muxbits == [[True, True, True, True], [True, True, True, False]]:
                        print("Local {}: GCLK1".format(II))
                        used_gclk = True
                    elif muxbits == [[True, True, True, True], [True, True, False, True]]:
                        print("Local {}: GCLK3".format(II))
                        used_gclk = True
                    else:
                        assert False

            if not used_gclk:
                if anybits(muxbits):
                    found_name = None
                    for srcname, srcbits in interconnect_map[muxname].items():
                        if srcbits == muxbits:
                            assert found_name is None
                            found_name = srcname
                    if found_name is None:
                        raise Exception("Unknown mux setting")
                    print("Local {}: {}".format(II, found_name))
        print()

        # L
        for trackI in range(8):
            muxname = "L:X8Y{}I{}".format(Y, trackI)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    raise Exception("Unknown mux setting")
                print("{}: {}".format(muxname, found_name))
        print()

        # L2
        for trackI in range(8):
            muxname = "L2:X8Y{}I{}".format(Y, trackI)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    raise Exception("Unknown mux setting")
                print("{}: {}".format(muxname, found_name))
        print()

        # U
        for trackI in range(7):
            muxname = "U:X8Y{}I{}".format(Y, trackI)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    raise Exception("Unknown mux setting")
                print("{}: {}".format(muxname, found_name))
        print()

        # D
        for trackI in range(7):
            muxname = "D:X8Y{}I{}".format(Y, trackI)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    raise Exception("Unknown mux setting")
                print("{}: {}".format(muxname, found_name))
        print()

def dump_top_ios(interconnect_map, data, busholdbits, pullupbits, slewratebits, lowcurrentbits):
    for X in range(2, 8):
        tileX = (X - 1) * 28 - 17

        for N in range(4 if X != 2 and X != 4 else 3):
            outpY = 1 if N == 0 or N == 2 else 3

            print("T IO X{}N{} invert: {}".format(X, N,
                not getbit(data, tileX + (11 if N >= 2 else 15), outpY + 1)))

            slewbitloc = slewratebits['IOC_X{}_Y{}_N{}'.format(X, 5, N)]
            slew_is_slow = getbit(data, slewbitloc[0], slewbitloc[1])
            if slew_is_slow:
                print("T IO X{}N{} slew: slow".format(X, N))
            else:
                print("T IO X{}N{} slew: fast".format(X, N))

            pullupbitloc = pullupbits['IOC_X{}_Y{}_N{}'.format(X, 5, N)]
            pullup_is_enabled = not getbit(data, pullupbitloc[0], pullupbitloc[1])
            if pullup_is_enabled:
                print("T IO X{}N{} pullup enabled".format(X, N))

            busholdbitloc = busholdbits['IOC_X{}_Y{}_N{}'.format(X, 5, N)]
            bushold_is_enabled = not getbit(data, busholdbitloc[0], busholdbitloc[1])
            if bushold_is_enabled:
                print("T IO X{}N{} bus hold enabled".format(X, N))

            currentbitlocs = lowcurrentbits['IOC_X{}_Y{}_N{}'.format(X, 5, N)]
            currentbit1 = getbit(data, currentbitlocs[0][0], currentbitlocs[0][1])
            currentbit2 = getbit(data, currentbitlocs[1][0], currentbitlocs[1][1])
            assert currentbit1 == currentbit2
            if currentbit1 and currentbit2:
                print("T IO X{}N{} drive strength: high".format(X, N))
            else:
                print("T IO X{}N{} drive strength: low".format(X, N))

            if N >= 2:
                outbox = getbox(data, tileX + 8, outpY, 4, 2, fliph=True)
            else:
                outbox = getbox(data, tileX + 15, outpY, 5, 2)
                for i in range(len(outbox)):
                    del outbox[i][1]
            outinp = twohot_decode(COL_IO_INPUTS, outbox)

            if not getbit(data, tileX + (12 if N >= 2 else 14), outpY + 1):
                print("T IO X{}N{} output: Bypass path".format(X, N))
                assert outinp == "VDD ???"
            else:
                if outinp is not None and outinp != "VDD ???":
                    print("T IO X{}N{} output: local track {}".format(X, N, outinp))
        print()

        # Local interconnect
        for II in range(10):
            muxname = "LOCAL_INTERCONNECT:X{}Y5S0I{}".format(X, II)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    # raise Exception("Unknown mux setting")
                    print("Unknown mux setting")
                print("Local {}: {}".format(II, found_name))
        print()

        # Routing tracks
        for N in range(10):
            trackX = tileX + (0 if N < 5 else 24)
            trackY = 1 + 2 * (N % 5)

            if N < 5:
                bitL = getbit(data, trackX + 0, trackY + 1)
                bitR = getbit(data, trackX + 2, trackY + 0)
            else:
                bitR = getbit(data, trackX + 1, trackY + 0)
                bitL = getbit(data, trackX + 3, trackY + 1)

            assert not (not bitL and not bitR)

            if not bitL:
                outp = BOT_IO_TRACK_MUX[4 - (N % 5)][0]
            elif not bitR:
                outp = BOT_IO_TRACK_MUX[4 - (N % 5)][1]
            else:
                outp = None

            if outp is not None:
                print("Wire D:X{}Y5I{} = {}".format(X, N, outp))
        print()

def dump_bot_ios(interconnect_map, data, busholdbits, pullupbits, slewratebits, lowcurrentbits):
    for X in range(2, 8):
        tileX = (X - 1) * 28 - 17

        for N in range(4 if X != 4 and X != 7 else 3):
            outpY = 204 if N == 0 or N == 2 else 202

            print("B IO X{}N{} invert: {}".format(X, N,
                not getbit(data, tileX + (11 if N >= 2 else 15), outpY)))

            slewbitloc = slewratebits['IOC_X{}_Y{}_N{}'.format(X, 0, N)]
            slew_is_slow = getbit(data, slewbitloc[0], slewbitloc[1])
            if slew_is_slow:
                print("B IO X{}N{} slew: slow".format(X, N))
            else:
                print("B IO X{}N{} slew: fast".format(X, N))

            pullupbitloc = pullupbits['IOC_X{}_Y{}_N{}'.format(X, 0, N)]
            pullup_is_enabled = not getbit(data, pullupbitloc[0], pullupbitloc[1])
            if pullup_is_enabled:
                print("B IO X{}N{} pullup enabled".format(X, N))

            busholdbitloc = busholdbits['IOC_X{}_Y{}_N{}'.format(X, 0, N)]
            bushold_is_enabled = not getbit(data, busholdbitloc[0], busholdbitloc[1])
            if bushold_is_enabled:
                print("B IO X{}N{} bus hold enabled".format(X, N))

            currentbitlocs = lowcurrentbits['IOC_X{}_Y{}_N{}'.format(X, 0, N)]
            currentbit1 = getbit(data, currentbitlocs[0][0], currentbitlocs[0][1])
            currentbit2 = getbit(data, currentbitlocs[1][0], currentbitlocs[1][1])
            assert currentbit1 == currentbit2
            if currentbit1 and currentbit2:
                print("B IO X{}N{} drive strength: high".format(X, N))
            else:
                print("B IO X{}N{} drive strength: low".format(X, N))

            if N >= 2:
                outbox = getbox(data, tileX + 8, outpY, 4, 2, fliph=True, flipv=True)
            else:
                outbox = getbox(data, tileX + 15, outpY, 5, 2, flipv=True)
                for i in range(len(outbox)):
                    del outbox[i][1]
            outinp = twohot_decode(COL_IO_INPUTS, outbox)

            if not getbit(data, tileX + (12 if N >= 2 else 14), outpY):
                print("B IO X{}N{} output: Bypass path".format(X, N))
                assert outinp == "VDD ???"
            else:
                if outinp is not None and outinp != "VDD ???":
                    print("B IO X{}N{} output: local track {}".format(X, N, outinp))
        print()

        # Local interconnect
        for II in range(10):
            muxname = "LOCAL_INTERCONNECT:X{}Y0S0I{}".format(X, II)
            muxbits = extract_mux_bits(data, muxname)
            if anybits(muxbits):
                found_name = None
                for srcname, srcbits in interconnect_map[muxname].items():
                    if srcbits == muxbits:
                        assert found_name is None
                        found_name = srcname
                if found_name is None:
                    # raise Exception("Unknown mux setting")
                    print("Unknown mux setting")
                print("Local {}: {}".format(II, found_name))
        print()

        # Routing tracks
        for N in range(10):
            trackX = tileX + (0 if N < 5 else 24)
            trackY = 196 + 2 * (N % 5)

            if N < 5:
                bitL = getbit(data, trackX + 0, trackY + 0)
                bitR = getbit(data, trackX + 2, trackY + 1)
            else:
                bitR = getbit(data, trackX + 1, trackY + 1)
                bitL = getbit(data, trackX + 3, trackY + 0)

            assert not (not bitL and not bitR)

            if not bitL:
                outp = BOT_IO_TRACK_MUX[N % 5][0]
            elif not bitR:
                outp = BOT_IO_TRACK_MUX[N % 5][1]
            else:
                outp = None

            if outp is not None:
                print("Wire U:X{}Y0I{} = {}".format(X, N, outp))
        print()

def main():
    fn = sys.argv[1]

    with open(fn, 'rb') as f:
        data = f.read()

    with open('initial-interconnect.json', 'r') as f:
        interconnect_map = json.load(f)
    with open('io-bus-hold.json', 'r') as f:
        busholdbits = json.load(f)
    with open('io-pull-up.json', 'r') as f:
        pullupbits = json.load(f)
    with open('io-fast-slew.json', 'r') as f:
        slewratebits = json.load(f)
    with open('io-low-current.json', 'r') as f:
        lowcurrentbits = json.load(f)

    print("******************** LOGIC COLUMNS ********************")
    for X in range(2, 8):
        dump_logic_col(interconnect_map, data, X)

    print("******************** LEFT IOs ********************")
    dump_left_ios(interconnect_map, data, busholdbits, pullupbits, slewratebits, lowcurrentbits)

    print("******************** RIGHT IOs ********************")
    dump_right_ios(interconnect_map, data, busholdbits, pullupbits, slewratebits, lowcurrentbits)

    print("******************** TOP IOs ********************")
    dump_top_ios(interconnect_map, data, busholdbits, pullupbits, slewratebits, lowcurrentbits)

    print("******************** BOTTOM IOs ********************")
    dump_bot_ios(interconnect_map, data, busholdbits, pullupbits, slewratebits, lowcurrentbits)

    print("******************** Global buffers ********************")
    gclk_en = getbit(data, 18, 103)
    gclk_logicen = not getbit(data, 17, 103)
    gclk_box = getbox(data, 2, 57 + 30 + 2, 5, 2, fliph=True, flipv=True)
    gclk_logic_val = twohot_decode(ROW_IO_INPUTS, gclk_box)
    assert not (gclk_logicen and not gclk_en)
    if gclk_en:
        if not gclk_logicen:
            assert gclk_logic_val is None
            print("GCLK0: Dedicated pin")
        else:
            assert gclk_logic_val is not None
            # XXX Something weird
            assert gclk_logic_val != "0"
            print("GCLK0: From logic, local {}".format(gclk_logic_val))

    gclk_en = getbit(data, 14, 103)
    gclk_logicen = not getbit(data, 11, 103)
    gclk_box = getbox(data, 2, 57 + 30 + 0, 5, 2, fliph=True)
    gclk_logic_val = twohot_decode(ROW_IO_INPUTS, gclk_box)
    assert not (gclk_logicen and not gclk_en)
    if gclk_en:
        if not gclk_logicen:
            assert gclk_logic_val is None
            print("GCLK1: Dedicated pin")
        else:
            assert gclk_logic_val is not None
            # XXX Something weird
            assert gclk_logic_val != "0"
            print("GCLK1: From logic, local {}".format(gclk_logic_val))

    gclk_en = getbit(data, 4, 103)
    gclk_logicen = not getbit(data, 3, 103)
    gclk_box = getbox(data, 2, 57 + 30 + 6, 5, 2, fliph=True, flipv=True)
    gclk_logic_val = twohot_decode(ROW_IO_INPUTS, gclk_box)
    assert not (gclk_logicen and not gclk_en)
    if gclk_en:
        if not gclk_logicen:
            assert gclk_logic_val is None
            print("GCLK2: Dedicated pin")
        else:
            assert gclk_logic_val is not None
            # XXX Something weird
            assert gclk_logic_val != "0"
            print("GCLK2: From logic, local {}".format(gclk_logic_val))

    gclk_en = getbit(data, 10, 103)
    gclk_logicen = not getbit(data, 9, 103)
    gclk_box = getbox(data, 2, 57 + 30 + 4, 5, 2, fliph=True)
    gclk_logic_val = twohot_decode(ROW_IO_INPUTS, gclk_box)
    assert not (gclk_logicen and not gclk_en)
    if gclk_en:
        if not gclk_logicen:
            assert gclk_logic_val is None
            print("GCLK3: Dedicated pin")
        else:
            assert gclk_logic_val is not None
            # XXX Something weird
            assert gclk_logic_val != "0"
            print("GCLK3: From logic, local {}".format(gclk_logic_val))
    print()


    if getbit(data, 5, 103):
        print("X1 GCLK0 buffer enabled")
    if getbit(data, 6, 103):
        print("X1 GCLK1 buffer enabled")
    if getbit(data, 7, 103):
        print("X1 GCLK2 buffer enabled")
    if getbit(data, 8, 103):
        print("X1 GCLK3 buffer enabled")
    for X in range(2, 9):
        if getbit(data, (X - 1) * 28 - 16, 103):
            print("X{} GCLK0 buffer enabled".format(X))
        if getbit(data, (X - 1) * 28 - 15, 103):
            print("X{} GCLK1 buffer enabled".format(X))
        if getbit(data, (X - 1) * 28 - 13, 103):
            print("X{} GCLK2 buffer enabled".format(X))
        if getbit(data, (X - 1) * 28 - 12, 103):
            print("X{} GCLK3 buffer enabled".format(X))

    print()
    if not getbit(data, 8, 205):
        print("DEV_OE is used")
    if not getbit(data, 7, 205):
        print("DEV_CLRn is used")
    usercode = 0
    for i in range(10):
        if not getbit(data, 1 + i, 202):
            usercode |= (1 << i)
    for i in range(10):
        if not getbit(data, 1 + i, 203):
            usercode |= (1 << i + 10)
    for i in range(10):
        if not getbit(data, 1 + i, 204):
            usercode |= (1 << i + 20)
    if not getbit(data, 9, 205):
        usercode |= (1 << 30)
    if not getbit(data, 10, 205):
        usercode |= (1 << 31)
    print("USERCODE is 0x{:08X}".format(usercode))

if __name__=='__main__':
    main()
