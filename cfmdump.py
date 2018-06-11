import sys

def hexdump(x):
    for i in range(len(x)):
        print("{:02X} ".format(x[i]), end='')
        if i % 16 == 15:
            print()

def our_tile_coords_to_byte_bit(x, y):
    byte_i = y * 8 + x // 8
    bit_i = x % 8
    return (byte_i, bit_i)

def our_shuffle_coords_to_tile_coords(x, y):
    oldy = x * 4 + y // 58
    oldx = y % 58 + 3
    if oldx >= 32:
        oldx += 3
    return (oldx, oldy)

def bit_at_my_coords(data, x, y):
    tilex, tiley = our_shuffle_coords_to_tile_coords(x, y)
    byte_i, bit_i = our_tile_coords_to_byte_bit(tilex, tiley)
    return data[byte_i] & (1 << bit_i)

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

def dumplogiccol(data, data2):
    print("Unknown stripe bits")
    for y in range(112):
        for x in [0, 1, 2, 32, 33, 34]:
            byte_i, bit_i = our_tile_coords_to_byte_bit(x, y)
            bit = data[byte_i] & (1 << bit_i)
            print("1 " if bit else "0 ", end='')
        print()
    print()

    for y in range(4):
        print("~~~ Y{} LAB ~~~".format(y + 1))

        starty = [179, 133, 86, 40][y]

        for n in range(10):
            print("N{} LUT: ".format(n), end='')

            if n < 5:
                offy = n * 4
            else:
                offy = (9 - n) * 4 + 26

            # print(starty + offy)

            if n < 5:
                b0 = bit_at_my_coords(data, 23, starty + offy + 3)
                b1 = bit_at_my_coords(data, 22, starty + offy + 3)
                b2 = bit_at_my_coords(data, 23, starty + offy + 2)
                b3 = bit_at_my_coords(data, 22, starty + offy + 2)

                b4 = bit_at_my_coords(data, 25, starty + offy + 2)
                b5 = bit_at_my_coords(data, 24, starty + offy + 2)
                b6 = bit_at_my_coords(data, 25, starty + offy + 3)
                b7 = bit_at_my_coords(data, 24, starty + offy + 3)

                b8 = bit_at_my_coords(data, 23, starty + offy + 1)
                b9 = bit_at_my_coords(data, 22, starty + offy + 1)
                b10 = bit_at_my_coords(data, 23, starty + offy + 0)
                b11 = bit_at_my_coords(data, 22, starty + offy + 0)

                b12 = bit_at_my_coords(data, 25, starty + offy + 1)
                b13 = bit_at_my_coords(data, 24, starty + offy + 1)
                b14 = bit_at_my_coords(data, 25, starty + offy + 0)
                b15 = bit_at_my_coords(data, 24, starty + offy + 0)
            else:
                b0 = bit_at_my_coords(data, 23, starty + offy + 0)
                b1 = bit_at_my_coords(data, 22, starty + offy + 0)
                b2 = bit_at_my_coords(data, 23, starty + offy + 1)
                b3 = bit_at_my_coords(data, 22, starty + offy + 1)

                b4 = bit_at_my_coords(data, 25, starty + offy + 1)
                b5 = bit_at_my_coords(data, 24, starty + offy + 1)
                b6 = bit_at_my_coords(data, 25, starty + offy + 0)
                b7 = bit_at_my_coords(data, 24, starty + offy + 0)

                b8 = bit_at_my_coords(data, 23, starty + offy + 2)
                b9 = bit_at_my_coords(data, 22, starty + offy + 2)
                b10 = bit_at_my_coords(data, 23, starty + offy + 3)
                b11 = bit_at_my_coords(data, 22, starty + offy + 3)

                b12 = bit_at_my_coords(data, 25, starty + offy + 2)
                b13 = bit_at_my_coords(data, 24, starty + offy + 2)
                b14 = bit_at_my_coords(data, 25, starty + offy + 3)
                b15 = bit_at_my_coords(data, 24, starty + offy + 3)

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

            print("{:04X}".format(lut))


            print("LUT input bits:")

            print("DATAA: ", end='')
            anydriver = False
            for name, b1, b2 in DATAA_INPUTS:
                if n < 5:
                    bit1 = bit_at_my_coords(data, 13 + b1[0], starty + offy + b1[1])
                    bit2 = bit_at_my_coords(data, 13 + b2[0], starty + offy + b2[1])
                else:
                    bit1 = bit_at_my_coords(data, 13 + b1[0], starty + offy + 3 - b1[1])
                    bit2 = bit_at_my_coords(data, 13 + b2[0], starty + offy + 3 - b2[1])
                if not bit1 and not bit2:
                    anydriver = True
                    print(name)
            if not anydriver:
                print("<NONE>")

            print("DATAB: ", end='')
            anydriver = False
            for name, b1, b2 in DATAB_INPUTS:
                if n < 5:
                    bit1 = bit_at_my_coords(data, 13 + b1[0], starty + offy + b1[1])
                    bit2 = bit_at_my_coords(data, 13 + b2[0], starty + offy + b2[1])
                else:
                    bit1 = bit_at_my_coords(data, 13 + b1[0], starty + offy + 3 - b1[1])
                    bit2 = bit_at_my_coords(data, 13 + b2[0], starty + offy + 3 - b2[1])
                if not bit1 and not bit2:
                    anydriver = True
                    print(name)
            if not anydriver:
                print("<NONE>")

            print("DATAC: ", end='')
            anydriver = False
            for name, b1, b2 in DATAC_INPUTS:
                if n < 5:
                    bit1 = bit_at_my_coords(data, 13 + b1[0], starty + offy + b1[1])
                    bit2 = bit_at_my_coords(data, 13 + b2[0], starty + offy + b2[1])
                else:
                    bit1 = bit_at_my_coords(data, 13 + b1[0], starty + offy + 3 - b1[1])
                    bit2 = bit_at_my_coords(data, 13 + b2[0], starty + offy + 3 - b2[1])
                if not bit1 and not bit2:
                    anydriver = True
                    print(name)
            if not anydriver:
                print("<NONE>")

            print("DATAD: ", end='')
            anydriver = False
            for name, b1, b2 in DATAD_INPUTS:
                if n < 5:
                    bit1 = bit_at_my_coords(data, 13 + b1[0], starty + offy + b1[1])
                    bit2 = bit_at_my_coords(data, 13 + b2[0], starty + offy + b2[1])
                else:
                    bit1 = bit_at_my_coords(data, 13 + b1[0], starty + offy + 3 - b1[1])
                    bit2 = bit_at_my_coords(data, 13 + b2[0], starty + offy + 3 - b2[1])
                if not bit1 and not bit2:
                    anydriver = True
                    print(name)
            if not anydriver:
                print("<NONE>")

        print()

        print("LAB inputs:")
        def dump2x4(data, x, y, flipH=False):
            for yy in range(2):
                for xx in range(4) if not flipH else reversed(range(4)):
                    print("1" if bit_at_my_coords(data, x + xx, y + yy) else "0", end='')
                print()
        def dump2x4inv(data, x, y, flipH=False):
            for yy in range(2):
                for xx in range(4) if not flipH else reversed(range(4)):
                    print("1" if bit_at_my_coords(data, x + xx, y - yy) else "0", end='')
                print()
        print("LAB0:")
        dump2x4(data2, 1, starty + 2, True)
        print("LAB1:")
        dump2x4(data2, 1, starty + 6, True)
        print("LAB2:")
        dump2x4(data2, 1, starty + 10, True)
        print("LAB3:")
        dump2x4(data2, 1, starty + 14, True)
        print("LAB4:")
        dump2x4(data2, 1, starty + 18, True)

        print("LAB5:")
        dump2x4(data, 9, starty + 0)
        print("LAB6:")
        dump2x4(data, 9, starty + 2)
        print("LAB7:")
        dump2x4(data, 9, starty + 4)
        print("LAB8:")
        dump2x4(data, 9, starty + 6)
        print("LAB9:")
        dump2x4(data, 9, starty + 8)
        print("LAB10:")
        dump2x4(data, 9, starty + 10)
        print("LAB11:")
        dump2x4(data, 9, starty + 12)
        print("LAB12:")
        dump2x4(data, 9, starty + 14)

        print("LAB13:")
        dump2x4inv(data2, 1, starty + 43, True)
        print("LAB14:")
        dump2x4inv(data2, 1, starty + 39, True)
        print("LAB15:")
        dump2x4inv(data2, 1, starty + 35, True)
        print("LAB16:")
        dump2x4inv(data2, 1, starty + 31, True)
        print("LAB17:")
        dump2x4inv(data2, 1, starty + 27, True)

        print("LAB18:")
        dump2x4inv(data, 9, starty + 45)
        print("LAB19:")
        dump2x4inv(data, 9, starty + 43)
        print("LAB20:")
        dump2x4inv(data, 9, starty + 41)
        print("LAB21:")
        dump2x4inv(data, 9, starty + 39)
        print("LAB22:")
        dump2x4inv(data, 9, starty + 37)
        print("LAB23:")
        dump2x4inv(data, 9, starty + 35)
        print("LAB24:")
        dump2x4inv(data, 9, starty + 33)
        print("LAB25:")
        dump2x4inv(data, 9, starty + 31)

def main():
    fn = sys.argv[1]

    with open(fn, 'rb') as f:
        data = f.read()

    print("----- Unknown beginning 0xC0 bytes -----")
    hexdump(data[:0xC0])
    print()

    for x in range(6):
        print("----- Column X{} -----".format(x + 2))
        dumplogiccol(data[0xC0 + x * 0x380:0xC0 + (x + 1) * 0x380],
                     data[0xC0 + (x + 1) * 0x380:0xC0 + (x + 2) * 0x380])
        print()

    print("----- Unknown ending 0x440 bytes -----")
    hexdump(data[0x15C0:])

if __name__=='__main__':
    main()
