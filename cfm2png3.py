from PIL import Image
import sys
import math
import cfmdump
import json

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

def draw_wire_t(px, x, y, l, color):
    for xx in range(8 * l):
        px[x * 8 + xx, y * 8] = color
def draw_wire_b(px, x, y, l, color):
    for xx in range(8 * l):
        px[x * 8 + xx, y * 8 + 7] = color
def draw_wire_l(px, x, y, h, color):
    for yy in range(8 * h):
        px[x * 8, y * 8 + yy] = color
def draw_wire_r(px, x, y, h, color):
    for yy in range(8 * h):
        px[x * 8 + 7, y * 8 + yy] = color

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
    for yy in range(8):
        pixels[xx, 232 * 8 + yy * 3 * 8] = (255, 0, 255)

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

for x in range(3, 9):
    for y in [1, 2, 3, 4]:
        # R4 going left
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

# Extra set of R4 (R1?) going left in the last column
for y in [1, 2, 3, 4]:
    drawbox(pixels,
        (8 - 1) * 28 - 17,
        LUTYLOCS[4 - y] + 0,
        4, 2, (132,98,213))
    drawbox(pixels,
        (8 - 1) * 28 - 17,
        LUTYLOCS[4 - y] + 6,
        4, 2, (132,98,213))
    drawbox(pixels,
        (8 - 1) * 28 - 17,
        LUTYLOCS[4 - y] + 14,
        4, 2, (132,98,213))
    drawbox(pixels,
        (8 - 1) * 28 - 17,
        LUTYLOCS[4 - y] + 18,
        4, 2, (132,98,213))

    drawbox(pixels,
        (8 - 1) * 28 - 17,
        LUTYLOCS[4 - y] + 26,
        4, 2, (132,98,213))
    drawbox(pixels,
        (8 - 1) * 28 - 17,
        LUTYLOCS[4 - y] + 30,
        4, 2, (132,98,213))
    drawbox(pixels,
        (8 - 1) * 28 - 17,
        LUTYLOCS[4 - y] + 38,
        4, 2, (132,98,213))
    drawbox(pixels,
        (8 - 1) * 28 - 17,
        LUTYLOCS[4 - y] + 44,
        4, 2, (132,98,213))

# Extra set of R4 going right in the first column
for y in [1, 2, 3, 4]:
    # R4 going right
    drawbox(pixels,
        3,
        LUTYLOCS[4 - y] + 1,
        2, 1, (101,161,14))
    drawbox(pixels,
        5,
        LUTYLOCS[4 - y] + 1,
        2, 1, (101,161,14))

    drawbox(pixels,
        3,
        LUTYLOCS[4 - y] + 3,
        2, 1, (101,161,14))
    drawbox(pixels,
        5,
        LUTYLOCS[4 - y] + 3,
        2, 1, (101,161,14))

    drawbox(pixels,
        3,
        LUTYLOCS[4 - y] + 42,
        2, 1, (101,161,14))
    drawbox(pixels,
        5,
        LUTYLOCS[4 - y] + 42,
        2, 1, (101,161,14))

    drawbox(pixels,
        3,
        LUTYLOCS[4 - y] + 44,
        2, 1, (101,161,14))
    drawbox(pixels,
        5,
        LUTYLOCS[4 - y] + 44,
        2, 1, (101,161,14))

for x in range(2, 9):
    for y in [1, 2, 3, 4]:
            # C4 up
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

            # C4 down
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

    for nn in range(3):
        draw_wire_t(pixels, 187, LUTYLOCS[4 - y] + 8 + 4 * nn,
            5, (0, 255, 0))
        draw_wire_b(pixels, 187, LUTYLOCS[4 - y] + 9 + 4 * nn,
            4, (0, 255, 0))
        draw_wire_b(pixels, 191, LUTYLOCS[4 - y] + 8 + 4 * nn,
            1, (0, 255, 0))
        draw_wire_l(pixels, 187, LUTYLOCS[4 - y] + 8 + 4 * nn,
            2, (0, 255, 0))
        draw_wire_r(pixels, 191, LUTYLOCS[4 - y] + 8 + 4 * nn,
            1, (0, 255, 0))
        draw_wire_r(pixels, 190, LUTYLOCS[4 - y] + 9 + 4 * nn,
            1, (0, 255, 0))

        drawbox(pixels,
            192, LUTYLOCS[4 - y] + 9 + 4 * nn,
            1, 1,
            (0, 255, 0))

        draw_wire_t(pixels, 187, LUTYLOCS[4 - y] + 10 + 4 * nn,
            4, (255, 200, 0))
        draw_wire_b(pixels, 187, LUTYLOCS[4 - y] + 11 + 4 * nn,
            5, (255, 200, 0))
        draw_wire_t(pixels, 191, LUTYLOCS[4 - y] + 11 + 4 * nn,
            1, (255, 200, 0))
        draw_wire_l(pixels, 187, LUTYLOCS[4 - y] + 10 + 4 * nn,
            2, (255, 200, 0))
        draw_wire_r(pixels, 191, LUTYLOCS[4 - y] + 11 + 4 * nn,
            1, (255, 200, 0))
        draw_wire_r(pixels, 190, LUTYLOCS[4 - y] + 10 + 4 * nn,
            1, (255, 200, 0))

    for nn in range(2):
        draw_wire_t(pixels, 187, LUTYLOCS[4 - y] + 28 + 4 * nn,
            4, (0, 255, 0))
        draw_wire_b(pixels, 187, LUTYLOCS[4 - y] + 29 + 4 * nn,
            5, (0, 255, 0))
        draw_wire_t(pixels, 191, LUTYLOCS[4 - y] + 29 + 4 * nn,
            1, (0, 255, 0))
        draw_wire_l(pixels, 187, LUTYLOCS[4 - y] + 28 + 4 * nn,
            2, (0, 255, 0))
        draw_wire_r(pixels, 191, LUTYLOCS[4 - y] + 29 + 4 * nn,
            1, (0, 255, 0))
        draw_wire_r(pixels, 190, LUTYLOCS[4 - y] + 28 + 4 * nn,
            1, (0, 255, 0))

        drawbox(pixels,
            192, LUTYLOCS[4 - y] + 28 + 4 * nn,
            1, 1,
            (0, 255, 0))

        draw_wire_t(pixels, 187, LUTYLOCS[4 - y] + 26 + 4 * nn,
            5, (255, 200, 0))
        draw_wire_b(pixels, 187, LUTYLOCS[4 - y] + 27 + 4 * nn,
            4, (255, 200, 0))
        draw_wire_b(pixels, 191, LUTYLOCS[4 - y] + 26 + 4 * nn,
            1, (255, 200, 0))
        draw_wire_l(pixels, 187, LUTYLOCS[4 - y] + 26 + 4 * nn,
            2, (255, 200, 0))
        draw_wire_r(pixels, 191, LUTYLOCS[4 - y] + 26 + 4 * nn,
            1, (255, 200, 0))
        draw_wire_r(pixels, 190, LUTYLOCS[4 - y] + 27 + 4 * nn,
            1, (255, 200, 0))

# LH IO tiles
for y in [1, 2, 3, 4]:
    for nn in range(9):
        drawbox(pixels, 7, LUTYLOCS[4 - y] + 2 + 2 * nn, 4, 2, (255, 0, 0))
        drawbox(pixels, 7, LUTYLOCS[4 - y] + 26 + 2 * nn, 4, 2, (255, 0, 0))

    for nn in range(3):
        draw_wire_t(pixels, 2, LUTYLOCS[4 - y] + 8 + 4 * nn,
            5, (0, 255, 0))
        draw_wire_b(pixels, 3, LUTYLOCS[4 - y] + 9 + 4 * nn,
            4, (0, 255, 0))
        draw_wire_b(pixels, 2, LUTYLOCS[4 - y] + 8 + 4 * nn,
            1, (0, 255, 0))
        draw_wire_r(pixels, 6, LUTYLOCS[4 - y] + 8 + 4 * nn,
            2, (0, 255, 0))
        draw_wire_l(pixels, 2, LUTYLOCS[4 - y] + 8 + 4 * nn,
            1, (0, 255, 0))
        draw_wire_l(pixels, 3, LUTYLOCS[4 - y] + 9 + 4 * nn,
            1, (0, 255, 0))

        drawbox(pixels,
            1, LUTYLOCS[4 - y] + 9 + 4 * nn,
            1, 1,
            (0, 255, 0))

        draw_wire_t(pixels, 3, LUTYLOCS[4 - y] + 10 + 4 * nn,
            4, (255, 200, 0))
        draw_wire_b(pixels, 2, LUTYLOCS[4 - y] + 11 + 4 * nn,
            5, (255, 200, 0))
        draw_wire_t(pixels, 2, LUTYLOCS[4 - y] + 11 + 4 * nn,
            1, (255, 200, 0))
        draw_wire_r(pixels, 6, LUTYLOCS[4 - y] + 10 + 4 * nn,
            2, (255, 200, 0))
        draw_wire_l(pixels, 2, LUTYLOCS[4 - y] + 11 + 4 * nn,
            1, (255, 200, 0))
        draw_wire_l(pixels, 3, LUTYLOCS[4 - y] + 10 + 4 * nn,
            1, (255, 200, 0))

    for nn in range(1):
        draw_wire_t(pixels, 3, LUTYLOCS[4 - y] + 28 + 4 * nn,
            4, (0, 255, 0))
        draw_wire_b(pixels, 2, LUTYLOCS[4 - y] + 29 + 4 * nn,
            5, (0, 255, 0))
        draw_wire_t(pixels, 2, LUTYLOCS[4 - y] + 29 + 4 * nn,
            1, (0, 255, 0))
        draw_wire_r(pixels, 6, LUTYLOCS[4 - y] + 28 + 4 * nn,
            2, (0, 255, 0))
        draw_wire_l(pixels, 2, LUTYLOCS[4 - y] + 29 + 4 * nn,
            1, (0, 255, 0))
        draw_wire_l(pixels, 3, LUTYLOCS[4 - y] + 28 + 4 * nn,
            1, (0, 255, 0))

        drawbox(pixels,
            1, LUTYLOCS[4 - y] + 28 + 4 * nn,
            1, 1,
            (0, 255, 0))

        draw_wire_t(pixels, 2, LUTYLOCS[4 - y] + 26 + 4 * nn,
            5, (255, 200, 0))
        draw_wire_b(pixels, 3, LUTYLOCS[4 - y] + 27 + 4 * nn,
            4, (255, 200, 0))
        draw_wire_b(pixels, 2, LUTYLOCS[4 - y] + 26 + 4 * nn,
            1, (255, 200, 0))
        draw_wire_r(pixels, 6, LUTYLOCS[4 - y] + 26 + 4 * nn,
            2, (255, 200, 0))
        draw_wire_l(pixels, 2, LUTYLOCS[4 - y] + 26 + 4 * nn,
            1, (255, 200, 0))
        draw_wire_l(pixels, 3, LUTYLOCS[4 - y] + 27 + 4 * nn,
            1, (255, 200, 0))

    for nn in [1, 2, 3]:
        draw_wire_t(pixels, 3, LUTYLOCS[4 - y] + 28 + 4 * nn,
            4, (0x82, 0x0F, 0x71))
        draw_wire_b(pixels, 2, LUTYLOCS[4 - y] + 29 + 4 * nn,
            5, (0x82, 0x0F, 0x71))
        draw_wire_t(pixels, 2, LUTYLOCS[4 - y] + 29 + 4 * nn,
            1, (0x82, 0x0F, 0x71))
        draw_wire_r(pixels, 6, LUTYLOCS[4 - y] + 28 + 4 * nn,
            2, (0x82, 0x0F, 0x71))
        draw_wire_l(pixels, 2, LUTYLOCS[4 - y] + 29 + 4 * nn,
            1, (0x82, 0x0F, 0x71))
        draw_wire_l(pixels, 3, LUTYLOCS[4 - y] + 28 + 4 * nn,
            1, (0x82, 0x0F, 0x71))

        draw_wire_t(pixels, 2, LUTYLOCS[4 - y] + 26 + 4 * nn,
            5, (0x82, 0x0F, 0x71))
        draw_wire_b(pixels, 3, LUTYLOCS[4 - y] + 27 + 4 * nn,
            4, (0x82, 0x0F, 0x71))
        draw_wire_b(pixels, 2, LUTYLOCS[4 - y] + 26 + 4 * nn,
            1, (0x82, 0x0F, 0x71))
        draw_wire_r(pixels, 6, LUTYLOCS[4 - y] + 26 + 4 * nn,
            2, (0x82, 0x0F, 0x71))
        draw_wire_l(pixels, 2, LUTYLOCS[4 - y] + 26 + 4 * nn,
            1, (0x82, 0x0F, 0x71))
        draw_wire_l(pixels, 3, LUTYLOCS[4 - y] + 27 + 4 * nn,
            1, (0x82, 0x0F, 0x71))

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

        drawbox(pixels,
            (x - 1) * 28 - 15,
            1 + 2 * nn,
            1, 1,
            (184,228,80))
        drawbox(pixels,
            (x - 1) * 28 - 17,
            2 + 2 * nn,
            1, 1,
            (184,228,80))

        drawbox(pixels,
            (x - 1) * 28 + 8,
            1 + 2 * nn,
            1, 1,
            (184,228,80))
        drawbox(pixels,
            (x - 1) * 28 + 10,
            2 + 2 * nn,
            1, 1,
            (184,228,80))

    for nn in range(2):
        draw_wire_t(pixels, (x - 1) * 28 - 9, 1 + 2*nn,
            4, (0, 255, 0))
        draw_wire_b(pixels, (x - 1) * 28 - 9, 2 + 2*nn,
            3, (0, 255, 0))
        draw_wire_b(pixels, (x - 1) * 28 - 6, 1 + 2*nn,
            1, (0, 255, 0))
        draw_wire_l(pixels, (x - 1) * 28 - 9, 1 + 2*nn,
            2, (0, 255, 0))
        draw_wire_r(pixels, (x - 1) * 28 - 6, 1 + 2*nn,
            1, (0, 255, 0))
        draw_wire_r(pixels, (x - 1) * 28 - 7, 2 + 2*nn,
            1, (0, 255, 0))
        drawbox(pixels,
            (x - 1) * 28 - 5, 2 + 2*nn,
            1, 1, (0, 255, 0))

        drawbox(pixels,
            (x - 1) * 28 - 3, 2 + 2*nn,
            1, 1, (0, 255, 0))
        drawbox(pixels,
            (x - 1) * 28 - 2, 1 + 2*nn,
            1, 1, (0, 255, 0))
        drawbox(pixels,
            (x - 1) * 28, 1 + 2*nn,
            3, 2, (0, 255, 0))

    for nn in range(2):
        draw_wire_t(pixels, (x - 1) * 28 - 9, 5 + 2*nn,
            4, (255, 200, 0))
        draw_wire_b(pixels, (x - 1) * 28 - 9, 6 + 2*nn,
            3, (255, 200, 0))
        draw_wire_b(pixels, (x - 1) * 28 - 6, 5 + 2*nn,
            1, (255, 200, 0))
        draw_wire_l(pixels, (x - 1) * 28 - 9, 5 + 2*nn,
            2, (255, 200, 0))
        draw_wire_r(pixels, (x - 1) * 28 - 6, 5 + 2*nn,
            1, (255, 200, 0))
        draw_wire_r(pixels, (x - 1) * 28 - 7, 6 + 2*nn,
            1, (255, 200, 0))

        drawbox(pixels,
            (x - 1) * 28 - 2, 5 + 2*nn,
            1, 1, (255, 200, 0))
        drawbox(pixels,
            (x - 1) * 28, 5 + 2*nn,
            3, 2, (255, 200, 0))


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

        drawbox(pixels,
            (x - 1) * 28 - 15,
            197 + 2 * nn,
            1, 1,
            (250,99,213))
        drawbox(pixels,
            (x - 1) * 28 - 17,
            196 + 2 * nn,
            1, 1,
            (250,99,213))

        drawbox(pixels,
            (x - 1) * 28 + 8,
            197 + 2 * nn,
            1, 1,
            (250,99,213))
        drawbox(pixels,
            (x - 1) * 28 + 10,
            196 + 2 * nn,
            1, 1,
            (250,99,213))

    for nn in range(2):
        draw_wire_b(pixels, (x - 1) * 28 - 9, 203 + 2*nn,
            4, (0, 255, 0))
        draw_wire_t(pixels, (x - 1) * 28 - 9, 202 + 2*nn,
            3, (0, 255, 0))
        draw_wire_t(pixels, (x - 1) * 28 - 6, 203 + 2*nn,
            1, (0, 255, 0))
        draw_wire_l(pixels, (x - 1) * 28 - 9, 202 + 2*nn,
            2, (0, 255, 0))
        draw_wire_r(pixels, (x - 1) * 28 - 6, 203 + 2*nn,
            1, (0, 255, 0))
        draw_wire_r(pixels, (x - 1) * 28 - 7, 202 + 2*nn,
            1, (0, 255, 0))
        drawbox(pixels,
            (x - 1) * 28 - 5, 202 + 2*nn,
            1, 1, (0, 255, 0))

        drawbox(pixels,
            (x - 1) * 28 - 3, 202 + 2*nn,
            1, 1, (0, 255, 0))
        drawbox(pixels,
            (x - 1) * 28 - 2, 203 + 2*nn,
            1, 1, (0, 255, 0))
        drawbox(pixels,
            (x - 1) * 28, 202 + 2*nn,
            3, 2, (0, 255, 0))

    for nn in range(2):
        draw_wire_b(pixels, (x - 1) * 28 - 9, 199 + 2*nn,
            4, (255, 200, 0))
        draw_wire_t(pixels, (x - 1) * 28 - 9, 198 + 2*nn,
            3, (255, 200, 0))
        draw_wire_t(pixels, (x - 1) * 28 - 6, 199 + 2*nn,
            1, (255, 200, 0))
        draw_wire_l(pixels, (x - 1) * 28 - 9, 198 + 2*nn,
            2, (255, 200, 0))
        draw_wire_r(pixels, (x - 1) * 28 - 6, 199 + 2*nn,
            1, (255, 200, 0))
        draw_wire_r(pixels, (x - 1) * 28 - 7, 198 + 2*nn,
            1, (255, 200, 0))

        drawbox(pixels,
            (x - 1) * 28 - 2, 199 + 2*nn,
            1, 1, (255, 200, 0))
        drawbox(pixels,
            (x - 1) * 28, 198 + 2*nn,
            3, 2, (255, 200, 0))


with open('io-bus-hold.json', 'r') as f:
    bitsbits = json.load(f)
    for _, v in bitsbits.items():
        drawbox(pixels, v[0], v[1], 1, 1, (255, 0, 0))
with open('io-pull-up.json', 'r') as f:
    bitsbits = json.load(f)
    for _, v in bitsbits.items():
        drawbox(pixels, v[0], v[1], 1, 1, (0, 255, 0))
with open('io-fast-slew.json', 'r') as f:
    bitsbits = json.load(f)
    for _, v in bitsbits.items():
        drawbox(pixels, v[0], v[1], 1, 1, (0, 0, 255))
with open('io-open-drain.json', 'r') as f:
    bitsbits = json.load(f)
    for _, v in bitsbits.items():
        drawbox(pixels, v[0], v[1], 1, 1, (255, 255, 0))
with open('io-low-current.json', 'r') as f:
    bitsbits = json.load(f)
    for _, v in bitsbits.items():
        drawbox(pixels, v[0][0], v[0][1], 1, 1, (0, 255, 255))
        drawbox(pixels, v[1][0], v[1][1], 1, 1, (0, 255, 255))

# USERCODE
draw_wire_t(pixels, 1, 202, 10, (255, 0, 255))
draw_wire_l(pixels, 1, 202, 3, (255, 0, 255))
draw_wire_r(pixels, 10, 202, 4, (255, 0, 255))
draw_wire_b(pixels, 1, 204, 8, (255, 0, 255))
draw_wire_l(pixels, 9, 205, 1, (255, 0, 255))
draw_wire_b(pixels, 9, 205, 2, (255, 0, 255))

im.save(outfn)
