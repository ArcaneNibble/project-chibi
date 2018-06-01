from PIL import Image
import sys
import math

W = 64

infn = sys.argv[1]
outfn = sys.argv[2]
with open(infn, 'rb') as f:
    indata = f.read()

BITS = len(indata) * 8
H = math.ceil(BITS / W)

# print(W, H, BITS)

im = Image.new("1", (W, H))
pixels = im.load()

# pixels[0,0] = 1
for y in range(H):
    for x in range(W):
        bit = y * W + x
        # print(bit)

        byte_i = bit // 8
        bit_i = 7 - (bit % 8)

        if indata[byte_i] & (1 << bit_i):
            pixels[x, y] = 1

im.save(outfn)
