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

def dumplogiccol(data):
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
            for lutiny in range(4):
                for lutinx in range(9):
                    bit = bit_at_my_coords(data, 13 + lutinx, starty + offy + lutiny)
                    print("1" if bit else "0", end='')
                print()
            print()


        print()

def main():
    fn = sys.argv[1]

    with open(fn, 'rb') as f:
        data = f.read()

    print("----- Unknown beginning 0xC0 bytes -----")
    hexdump(data[:0xC0])
    print()

    for x in range(6):
        print("----- Column X{} -----".format(x + 2))
        dumplogiccol(data[0xC0 + x * 0x380:0xC0 + (x + 1) * 0x380])
        print()

    print("----- Unknown ending 0x440 bytes -----")
    hexdump(data[0x15C0:])

if __name__=='__main__':
    main()
