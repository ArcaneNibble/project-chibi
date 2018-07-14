from cfmdump2 import LUTYLOCS, DATAA_INPUTS, DATAB_INPUTS, DATAC_INPUTS, DATAD_INPUTS, ROW_IO_INPUTS, COL_IO_INPUTS, LH_IO_TRACK_MUX, BOT_IO_TRACK_MUX, EVEN_CONTROL_MUX_INPUTS, ODD_CONTROL_MUX_INPUTS, my_coords_to_byte_bit, parse_xyi, parse_xysi
import sys
import json

infn = sys.argv[1]
outfn = sys.argv[2]

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
with open('io-open-drain.json', 'r') as f:
    opendrainbits = json.load(f)

outoutout = bytearray(b'\xff' * 0x1a00)

def setbit(data, x, y, val=False):
    byte_i, bit_i = my_coords_to_byte_bit(x, y)
    if val:
        data[byte_i] |= (1 << bit_i)
    else:
        data[byte_i] &= ~(1 << bit_i)


ioioioio = {}
lablablablab = {}

for X in [1, 8]:
    for Y in range(1, 5):
        for N in range(5 if Y != 2 and X != 1 else 4):
            ioioioio[(X, Y, N)] = {
                'slew': 'fast',
                'pullup': False,
                'bushold': False,
                'opendrain': False,
                'drivestrength': 'high',
                'invert': True,
                'invertoe': False,
                'schmitttrigger': False,
                'enableinput': False,
                'outputmux': None,
                'idelay': False,
                'oemux': None
            }

for X in range(2, 8):
    for Y in [0, 5]:
        for N in range(4 if X != 4 and not (X == 7 and Y == 0) else 3):
            ioioioio[(X, Y, N)] = {
                'slew': 'fast',
                'pullup': False,
                'bushold': False,
                'opendrain': False,
                'drivestrength': 'high',
                'invert': True,
                'invertoe': False,
                'schmitttrigger': False,
                'enableinput': False,
                'outputmux': None,
                'idelay': False,
                'oemux': None
            }

# print(ioioioio)

# Stripes in pad ring
for x in range(208):
    for y in [232, 236, 238, 242, 244, 248, 250, 254]:
        setbit(outoutout, x, y)

# Dunno what this bit does
setbit(outoutout, 1, 9)

# IOs
for ((X, Y, N), attribs) in ioioioio.items():
    # print(X, Y, N, attribs)
    # Secret pad
    if X != 2 and Y != 5 and N != 3:
        name = "IOC_X{}_Y{}_N{}".format(X, Y, N)
        if attribs['bushold']:
            busholdloc = busholdbits[name]
            setbit(outoutout, busholdloc[0], busholdloc[1])
        if attribs['pullup']:
            pulluploc = pullupbits[name]
            setbit(outoutout, pulluploc[0], pulluploc[1])
        if attribs['slew'] == 'slow':
            slewrateloc = slewratebits[name]
            setbit(outoutout, slewrateloc[0], slewrateloc[1])
        if attribs['opendrain']:
            opendrainloc = opendrainbits[name]
            setbit(outoutout, opendrainloc[0], opendrainloc[1])
        if attribs['drivestrength'] == 'low':
            lowcurrentloc = lowcurrentbits[name]
            setbit(outoutout, lowcurrentloc[0][0], lowcurrentloc[0][1])
            setbit(outoutout, lowcurrentloc[1][0], lowcurrentloc[1][1])

    if Y == 0 or Y == 5:
        tileX = (X - 1) * 28 - 17

        setbit(outoutout, tileX + [27, 18, 11, 9][N], 0 if Y == 5 else 206, attribs['schmitttrigger'])
        setbit(outoutout, tileX + [26, 17, 10, 8][N], 0 if Y == 5 else 206, attribs['enableinput'])

        outpY = (1 if N == 0 or N == 2 else 3) if Y == 5 else (204 if N == 0 or N == 2 else 202)

        setbit(outoutout, tileX + (11 if N >= 2 else 15), outpY + (1 if Y == 5 else 0), not attribs['invert'])
        setbit(outoutout, tileX + (11 if N >= 2 else 15), outpY + (5 if Y == 5 else -4), not attribs['invertoe'])

    if X == 1 or X == 8:
        tileY = LUTYLOCS[4 - Y]

        setbit(outoutout, 0 if X == 1 else 193, tileY + [1, 8, 14, 21, 28][N], attribs['schmitttrigger'])
        setbit(outoutout, 0 if X == 1 else 193, tileY + [0, 7, 13, 20, 27][N], attribs['enableinput'])

        localY = tileY + 8 + N * 4
        if N >= 3:
            localY += 8

        setbit(outoutout, 2 if X == 1 else 191, localY + (1 if N < 3 else 0), not attribs['invert'])
        setbit(outoutout, 2 if X == 1 else 191, localY + (2 if N < 3 else -1), not attribs['invertoe'])

with open(outfn, 'wb') as f:
    f.write(outoutout)
