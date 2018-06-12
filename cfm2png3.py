from PIL import Image
import sys
import math
import cfmdump

infn = sys.argv[1]
outfn = sys.argv[2]
with open(infn, 'rb') as f:
    indata = f.read()

im = Image.new("RGB", (208 * 8, 256 * 8))
pixels = im.load()

def drawlargepixel(px, x, y, color):
    for xx in range(8):
        for yy in range(8):
            px[x * 8 + xx, y * 8 + yy] = color

def drawbox(px, x, y, w, h, color):
    for xx in range(8 * w):
        px[x * 8 + xx, y * 8] = color
        px[x * 8 + xx, (y + h) * 8 - 1] = color
    for yy in range(8 * h):
        px[x * 8, y * 8 + yy] = color
        px[(x + w) * 8 - 1, y * 8 + yy] = color

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

for x in range(208):
    for y in range(256):
        byte_i, bit_i = my_coords_to_byte_bit(x, y)
        if indata[byte_i] & (1 << bit_i):
            drawlargepixel(pixels, x, y, (255, 255, 255))

for xx in range(208 * 8):
    pixels[xx, 232 * 8] = (255, 0, 255)

LUTYLOCS = [11, 57, 104, 150]

for x in range(2, 8):
    for y in [1, 2, 3, 4]:
        for n in range(10):
            boxY = LUTYLOCS[4 - y] + n * 4
            if n >= 5:
                boxY += 6

            # LUTs
            drawbox(pixels, (x - 1) * 28, boxY, 4, 4, (0, 0, 255))

            # LUT inputs
            drawbox(pixels, (x - 1) * 28 - 9, boxY, 9, 4, (0, 255, 0))

        # LAB lines [5-12], [18-25] (on the "left" of the LUTs)
        for nn in range(8):
            drawbox(pixels,
                (x - 1) * 28 - 13,
                LUTYLOCS[4 - y] + nn * 2,
                4, 2, (255, 0, 0))
            drawbox(pixels,
                (x - 1) * 28 - 13,
                LUTYLOCS[4 - y] + 30 + nn * 2,
                4, 2, (255, 0, 0))

        # LAB lines [0-4], [13-17] (on the "right" of the LUTs)
        for nn in range(5):
            drawbox(pixels,
                (x - 1) * 28 + 7,
                LUTYLOCS[4 - y] + nn * 4 + 2,
                4, 2, (255, 0, 0))
            drawbox(pixels,
                (x - 1) * 28 + 7,
                LUTYLOCS[4 - y] + nn * 4 + 26,
                4, 2, (255, 0, 0))

for x in range(2, 9):
    for y in [1, 2, 3, 4]:
        # R4 going left (not sure if X=2 has one yet)
        if x != 2:
            for nn in range(4):
                drawbox(pixels,
                    (x - 1) * 28 - 21,
                    LUTYLOCS[4 - y] + nn * 4 + 4,
                    4, 2, (132,98,213))
                drawbox(pixels,
                    (x - 1) * 28 - 21,
                    LUTYLOCS[4 - y] + nn * 4 + 28,
                    4, 2, (132,98,213))

for x in range(2, 8):
    for y in [1, 2, 3, 4]:
        # R4 going right
        drawbox(pixels,
            (x - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 0,
            4, 2, (101,161,14))
        drawbox(pixels,
            (x - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 6,
            4, 2, (101,161,14))
        drawbox(pixels,
            (x - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 14,
            4, 2, (101,161,14))
        drawbox(pixels,
            (x - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 18,
            4, 2, (101,161,14))

        drawbox(pixels,
            (x - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 26,
            4, 2, (101,161,14))
        drawbox(pixels,
            (x - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 30,
            4, 2, (101,161,14))
        drawbox(pixels,
            (x - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 38,
            4, 2, (101,161,14))
        drawbox(pixels,
            (x - 1) * 28 - 17,
            LUTYLOCS[4 - y] + 44,
            4, 2, (101,161,14))

for x in range(2, 9):
    for y in [1, 2, 3, 4]:
        # C4 going up (not sure if Y=4 has one yet)
            if y != 4:
                drawbox(pixels,
                    (x - 1) * 28 - 21,
                    LUTYLOCS[4 - y] + 0,
                    4, 2, (250,99,213))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 4,
                    4, 2, (250,99,213))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 10,
                    4, 2, (250,99,213))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 16,
                    4, 2, (250,99,213))

                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 32,
                    4, 2, (250,99,213))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 36,
                    4, 2, (250,99,213))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 42,
                    4, 2, (250,99,213))

        # C4 going down (not sure if Y=1 has one yet)
            if y != 1:
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 2,
                    4, 2, (184,228,80))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 8,
                    4, 2, (184,228,80))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 12,
                    4, 2, (184,228,80))

                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 28,
                    4, 2, (184,228,80))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 34,
                    4, 2, (184,228,80))
                drawbox(pixels,
                    (x - 1) * 28 - 17,
                    LUTYLOCS[4 - y] + 40,
                    4, 2, (184,228,80))
                drawbox(pixels,
                    (x - 1) * 28 - 21,
                    LUTYLOCS[4 - y] + 44,
                    4, 2, (184,228,80))

# RH IO tiles
for y in [1, 2, 3, 4]:
    for nn in range(9):
        drawbox(pixels, 183, LUTYLOCS[4 - y] + 2 + 2 * nn, 4, 2, (255, 0, 0))
        drawbox(pixels, 183, LUTYLOCS[4 - y] + 26 + 2 * nn, 4, 2, (255, 0, 0))

# LH IO tiles
for y in [1, 2, 3, 4]:
    for nn in range(9):
        drawbox(pixels, 7, LUTYLOCS[4 - y] + 2 + 2 * nn, 4, 2, (255, 0, 0))
        drawbox(pixels, 7, LUTYLOCS[4 - y] + 26 + 2 * nn, 4, 2, (255, 0, 0))

# TOP IO tiles
for x in range(2, 8):
    for nn in range(5):
        drawbox(pixels,
            (x - 1) * 28 + 3,
            1 + 2 * nn,
            4, 2,
            (255, 0, 0))
        drawbox(pixels,
            (x - 1) * 28 - 13,
            1 + 2 * nn,
            4, 2,
            (255, 0, 0))

# Bottom IO tiles (guessed)
for x in range(2, 8):
    for nn in range(5):
        drawbox(pixels,
            (x - 1) * 28 + 3,
            196 + 2 * nn,
            4, 2,
            (255, 0, 0))
        drawbox(pixels,
            (x - 1) * 28 - 13,
            196 + 2 * nn,
            4, 2,
            (255, 0, 0))

# USERCODE
drawbox(pixels, 1, 202, 10, 3, (255, 0, 255))
drawbox(pixels, 9, 205, 2, 1, (255, 0, 255))

im.save(outfn)
