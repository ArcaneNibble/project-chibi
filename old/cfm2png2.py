from PIL import Image
import sys
import math
import cfmdump

infn = sys.argv[1]
outfn = sys.argv[2]
with open(infn, 'rb') as f:
    indata = f.read()

im = Image.new("RGB", (28 * 7 * 8, 232 * 8))
pixels = im.load()

for tilecol in range(7):
    tiledata = indata[0xC0 + tilecol * 0x380:0xC0 + (tilecol + 1) * 0x380]

    for imy in range(232):
        for imx in range(28):
            if cfmdump.bit_at_my_coords(tiledata, imx, imy):
                for xx in range(8):
                    for yy in range(8):
                        pixels[(28 * tilecol + imx) * 8 + xx, imy * 8 + yy] = (255, 255, 255)

    # Tile border
    for yy in range(232 * 8):
        pixels[28 * tilecol * 8, yy] = (255, 0, 255)

    # LAB-wide stuff
    for laby in range(4):
        starty = [179, 133, 86, 40][laby]

        # LUT
        for yy in range(20 * 8):
            pixels[(28 * tilecol + 22) * 8, starty * 8 + yy] = (0, 0, 255)
        for yy in range(20 * 8):
            pixels[(28 * tilecol + 22) * 8, (starty + 26) * 8 + yy] = (0, 0, 255)
        for yy in range(20 * 8):
            pixels[(28 * tilecol + 26) * 8 - 1, starty * 8 + yy] = (0, 0, 255)
        for yy in range(20 * 8):
            pixels[(28 * tilecol + 26) * 8 - 1, (starty + 26) * 8 + yy] = (0, 0, 255)
        for xx in range(22 * 8, 26 * 8):
            pixels[(28 * tilecol * 8) + xx, starty * 8] = (0, 0, 255)
            pixels[(28 * tilecol * 8) + xx, (starty + 20) * 8 - 1] = (0, 0, 255)
            pixels[(28 * tilecol * 8) + xx, (starty + 26) * 8] = (0, 0, 255)
            pixels[(28 * tilecol * 8) + xx, (starty + 46) * 8 - 1] = (0, 0, 255)

        # LUT inputs
        for yy in range(20 * 8):
            pixels[(28 * tilecol + 13) * 8, starty * 8 + yy] = (0, 255, 0)
        for yy in range(20 * 8):
            pixels[(28 * tilecol + 13) * 8, (starty + 26) * 8 + yy] = (0, 255, 0)
        for yy in range(20 * 8):
            pixels[(28 * tilecol + 22) * 8 - 1, starty * 8 + yy] = (0, 255, 0)
        for yy in range(20 * 8):
            pixels[(28 * tilecol + 22) * 8 - 1, (starty + 26) * 8 + yy] = (0, 255, 0)
        for xx in range(13 * 8, 22 * 8):
            pixels[(28 * tilecol * 8) + xx, starty * 8] = (0, 255, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 20) * 8 - 1] = (0, 255, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 26) * 8] = (0, 255, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 46) * 8 - 1] = (0, 255, 0)

        # LAB inputs
        for yy in range(16 * 8):
            pixels[(28 * tilecol + 9) * 8, starty * 8 + yy] = (255, 0, 0)
        for yy in range(16 * 8):
            pixels[(28 * tilecol + 9) * 8, (starty + 30) * 8 + yy] = (255, 0, 0)
        for yy in range(16 * 8):
            pixels[(28 * tilecol + 13) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(16 * 8):
            pixels[(28 * tilecol + 13) * 8 - 1, (starty + 30) * 8 + yy] = (255, 0, 0)
        for xx in range(9 * 8, 13 * 8):
            pixels[(28 * tilecol * 8) + xx, starty * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 16) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 30) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 46) * 8 - 1] = (255, 0, 0)

        for xx in range(1 * 8, 5 * 8):
            pixels[(28 * tilecol * 8) + xx, (starty + 2) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 4) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 6) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 8) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 10) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 12) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 14) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 16) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 18) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 20) * 8 - 1] = (255, 0, 0)

            pixels[(28 * tilecol * 8) + xx, (starty + 26) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 28) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 30) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 32) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 34) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 36) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 38) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 40) * 8 - 1] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 42) * 8] = (255, 0, 0)
            pixels[(28 * tilecol * 8) + xx, (starty + 44) * 8 - 1] = (255, 0, 0)

        for yy in range(2 * 8, 4 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(6 * 8, 8 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(10 * 8, 12 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(14 * 8, 16 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(18 * 8, 20 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)

        for yy in range(26 * 8, 28 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(30 * 8, 32 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(34 * 8, 36 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(38 * 8, 40 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)
        for yy in range(42 * 8, 44 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (255, 0, 0)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (255, 0, 0)

        # R4 going left?!?!
        for xx in range(1 * 8, 5 * 8):
            pixels[(28 * tilecol * 8) + xx, (starty + 4) * 8] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 6) * 8 - 1] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 8) * 8] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 10) * 8 - 1] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 12) * 8] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 14) * 8 - 1] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 16) * 8] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 18) * 8 - 1] = (132,98,213)

            pixels[(28 * tilecol * 8) + xx, (starty + 28) * 8] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 30) * 8 - 1] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 32) * 8] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 34) * 8 - 1] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 36) * 8] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 38) * 8 - 1] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 40) * 8] = (132,98,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 42) * 8 - 1] = (132,98,213)

        for yy in range(4 * 8, 6 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (132,98,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (132,98,213)
        for yy in range(8 * 8, 10 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (132,98,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (132,98,213)
        for yy in range(12 * 8, 14 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (132,98,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (132,98,213)
        for yy in range(16 * 8, 18 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (132,98,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (132,98,213)

        for yy in range(28 * 8, 30 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (132,98,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (132,98,213)
        for yy in range(32 * 8, 34 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (132,98,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (132,98,213)
        for yy in range(36 * 8, 38 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (132,98,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (132,98,213)
        for yy in range(40 * 8, 42 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (132,98,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (132,98,213)

        # R4 going right?!?!
        for xx in range(5 * 8, 9 * 8):
            pixels[(28 * tilecol * 8) + xx, (starty + 0) * 8] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 2) * 8 - 1] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 6) * 8] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 8) * 8 - 1] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 14) * 8] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 16) * 8 - 1] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 18) * 8] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 20) * 8 - 1] = (101,161,14)

            pixels[(28 * tilecol * 8) + xx, (starty + 26) * 8] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 28) * 8 - 1] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 30) * 8] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 32) * 8 - 1] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 38) * 8] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 40) * 8 - 1] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 44) * 8] = (101,161,14)
            pixels[(28 * tilecol * 8) + xx, (starty + 46) * 8 - 1] = (101,161,14)

        for yy in range(0 * 8, 2 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (101,161,14)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (101,161,14)
        for yy in range(6 * 8, 8 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (101,161,14)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (101,161,14)
        for yy in range(14 * 8, 16 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (101,161,14)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (101,161,14)
        for yy in range(18 * 8, 20 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (101,161,14)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (101,161,14)

        for yy in range(26 * 8, 28 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (101,161,14)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (101,161,14)
        for yy in range(30 * 8, 32 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (101,161,14)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (101,161,14)
        for yy in range(38 * 8, 40 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (101,161,14)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (101,161,14)
        for yy in range(44 * 8, 46 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (101,161,14)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (101,161,14)

        # C4 going up?!?!
        for xx in range(1 * 8, 5 * 8):
            pixels[(28 * tilecol * 8) + xx, (starty + 0) * 8] = (250,99,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 2) * 8 - 1] = (250,99,213)
        for xx in range(5 * 8, 9 * 8):
            pixels[(28 * tilecol * 8) + xx, (starty + 4) * 8] = (250,99,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 6) * 8 - 1] = (250,99,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 10) * 8] = (250,99,213)
            pixels[(28 * tilecol * 8) + xx, (starty + 12) * 8 - 1] = (250,99,213)

        for yy in range(0 * 8, 2 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (250,99,213)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (250,99,213)
        for yy in range(4 * 8, 6 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (250,99,213)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (250,99,213)
        for yy in range(10 * 8, 12 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (250,99,213)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (250,99,213)

        # C4 going down?!?!
        for xx in range(1 * 8, 5 * 8):
            pixels[(28 * tilecol * 8) + xx, (starty + 44) * 8] = (184,228,80)
            pixels[(28 * tilecol * 8) + xx, (starty + 46) * 8 - 1] = (184,228,80)
        for xx in range(5 * 8, 9 * 8):
            pixels[(28 * tilecol * 8) + xx, (starty + 2) * 8] = (184,228,80)
            pixels[(28 * tilecol * 8) + xx, (starty + 4) * 8 - 1] = (184,228,80)
            pixels[(28 * tilecol * 8) + xx, (starty + 8) * 8] = (184,228,80)
            pixels[(28 * tilecol * 8) + xx, (starty + 10) * 8 - 1] = (184,228,80)
            pixels[(28 * tilecol * 8) + xx, (starty + 12) * 8] = (184,228,80)
            pixels[(28 * tilecol * 8) + xx, (starty + 14) * 8 - 1] = (184,228,80)
            pixels[(28 * tilecol * 8) + xx, (starty + 40) * 8] = (184,228,80)
            pixels[(28 * tilecol * 8) + xx, (starty + 42) * 8 - 1] = (184,228,80)

        for yy in range(2 * 8, 4 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (184,228,80)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (184,228,80)
        for yy in range(8 * 8, 10 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (184,228,80)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (184,228,80)
        for yy in range(12 * 8, 14 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (184,228,80)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (184,228,80)
        for yy in range(40 * 8, 42 * 8):
            pixels[(28 * tilecol + 5) * 8, starty * 8 + yy] = (184,228,80)
            pixels[(28 * tilecol + 9) * 8 - 1, starty * 8 + yy] = (184,228,80)
        for yy in range(44 * 8, 46 * 8):
            pixels[(28 * tilecol + 1) * 8, starty * 8 + yy] = (184,228,80)
            pixels[(28 * tilecol + 5) * 8 - 1, starty * 8 + yy] = (184,228,80)

im.save(outfn)
