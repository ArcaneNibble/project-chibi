from cfmdump2 import LUTYLOCS, DATAA_INPUTS, DATAB_INPUTS, DATAC_INPUTS, DATAD_INPUTS, ROW_IO_INPUTS, COL_IO_INPUTS, LH_IO_TRACK_MUX, BOT_IO_TRACK_MUX, EVEN_CONTROL_MUX_INPUTS, ODD_CONTROL_MUX_INPUTS, my_coords_to_byte_bit, parse_xyi, parse_xysi
import sys
import json

infn = sys.argv[1]
outfn = sys.argv[2]

def parse_xyn(inp):
    xpos = inp.find('X')
    ypos = inp.find('Y')
    npos = inp.find('N')

    assert xpos >= 0
    assert ypos > xpos
    assert npos > ypos

    return (int(inp[xpos + 1:ypos]), int(inp[ypos + 1:npos]), int(inp[npos + 1:]))

def parse_xysi2(inp):
    xpos = inp.find('X')
    ypos = inp.find('Y')
    spos = inp.find('S')
    ipos = inp.find('I')

    assert xpos >= 0
    assert ypos > xpos
    assert spos > ypos
    assert ipos > spos

    return (int(inp[xpos + 1:ypos]), int(inp[ypos + 1:spos]), int(inp[spos + 1:ipos]), int(inp[ipos + 1:]))

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

def setbox(data, x, y, box, fliph=False, flipv=False):
    h = len(box)
    w = len(box[0])

    for boxy, yy in zip(range(h), range(h) if not flipv else reversed(range(h))):
        for boxx, xx in zip(range(w), range(w) if not fliph else reversed(range(w))):
            setbit(data, x + xx, y + yy, box[boxy][boxx])

def setbit(data, x, y, val=False):
    byte_i, bit_i = my_coords_to_byte_bit(x, y)
    if val:
        data[byte_i] |= (1 << bit_i)
    else:
        data[byte_i] &= ~(1 << bit_i)


ioioioio = {}
lablablablab = {}
gclkgclk = {
    'gclk0src': None,
    'gclk1src': None,
    'gclk2src': None,
    'gclk3src': None,
    'gclk0cols': set(),
    'gclk1cols': set(),
    'gclk2cols': set(),
    'gclk3cols': set(),
}

for X in [1, 8]:
    for Y in range(1, 5):
        this_tile_io = []
        for N in range(5 if Y != 2 and X != 1 else 4):
            this_tile_io.append({
                'slew': 'fast',
                'pullup': False,
                'bushold': False,
                'opendrain': False,
                'drivestrength': 'high',
                'invert': True,
                'invertoe': False,
                'schmitttrigger': True,
                'enableinput': False,
                'outputmux': None,
                'idelay': False,
                'oemux': None
            })

        ioioioio[(X, Y)] = {
            'ios': this_tile_io
        }

for X in range(2, 8):
    for Y in [0, 5]:
        this_tile_io = []
        for N in range(4 if X != 4 and not (X == 7 and Y == 0) else 3):
            this_tile_io.append({
                'slew': 'fast',
                'pullup': False,
                'bushold': False,
                'opendrain': False,
                'drivestrength': 'high',
                'invert': True,
                'invertoe': False,
                'schmitttrigger': True,
                'enableinput': False,
                'outputmux': None,
                'idelay': False,
                'oemux': None
            })

        ioioioio[(X, Y)] = {
            'ios': this_tile_io
        }

for X in range(2, 8):
    for Y in range(1, 5):
        lutslutsluts = []
        for N in range(10):
            lutslutsluts.append({
                'bits': 0xFFFF,
                'lutchain': False,
                'regchain': False,
                'qfbk': False,
                'cin': False,
                'syncmode': False,
                'clkline1': True,
                'aclrline1': False,
                'buf0': 'reg',
                'buf1': 'reg',
                'bufL': 'reg',

                'dataa': None,
                'datab': None,
                'datac': None,
                'datad': None,
            })
        lablablablab[(X, Y)] = {
            'luts': lutslutsluts,
            'clk0': None,
            'clk1': None,
        }

# print(ioioioio)



def get_mux_box(muxname):
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

        return (boxX, boxY)

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

        return (boxX, boxY)

    elif muxname.startswith("R:"):
        X, Y, I = parse_xyi(muxname)
        # print(X, Y, I)

        if X == 1:
            return None
        
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

        return (boxX, boxY)

    elif muxname.startswith("U:"):
        X, Y, I = parse_xyi(muxname)
        # print(X, Y, I)

        if Y == 0:
            return None
        
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

        return (boxX, boxY)

    elif muxname.startswith("D:"):
        X, Y, I = parse_xyi(muxname)
        # print(X, Y, I)

        if Y == 5:
            return None
        
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

        return (boxX, boxY)

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

            return (boxX, boxY)

        elif X == 8:
            # Right IO
            assert I in range(18)

            boxX = 183
            if I in range(9):
                boxY = LUTYLOCS[4 - Y] + 2 * I + 2
            else:
                boxY = LUTYLOCS[4 - Y] + 2 * (17 - I) + 26

            return (boxX, boxY)

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

                return (boxX, boxY)
            elif Y == 5:
                # Top IO
                assert I in range(10)

                if I < 5:
                    boxX = (X - 1) * 28 + 3
                    boxY = 1 + 2 * I
                else:
                    boxX = (X - 1) * 28 - 13
                    boxY = 1 + 2 * (I - 5)

                return (boxX, boxY)
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

                return (boxX, boxY)
    else:
        print("ERROR: Do not understand {}".format(muxname))
        raise Exception()


################################## HERE WE ACTUALLY READ THE INPUT
with open(infn, 'r') as f:
    while True:
        l = f.readline()
        if not l:
            break
        l = l.strip()

        if not l:
            continue

        if ' = ' in l:
            srcthing, value = l.split(' = ')

            if srcthing.startswith("LUTBITS:"):
                x, y, n = parse_xyn(srcthing[8:])
                # print(x, y, n)
                bits = int(value, 2)
                # print(bits)
                lablablablab[(x, y)]['luts'][n]['bits'] = bits
            elif srcthing.startswith("IO_TILE:"):
                _, loc, param = srcthing.split(':')
                x, y, i = parse_xyi(loc)

                if param == "INVERTOUT":
                    ioioioio[(x, y)]['ios'][i]['invert'] = value.lower() == 'true'
                elif param == "INVERTOE":
                    ioioioio[(x, y)]['ios'][i]['invertoe'] = value.lower() == 'true'
                elif param == "ENABLEIBUF":
                    ioioioio[(x, y)]['ios'][i]['enableinput'] = value.lower() == 'true'
                elif param == "SCHMITTTRIGGER":
                    ioioioio[(x, y)]['ios'][i]['schmitttrigger'] = value.lower() == 'true'
                else:
                    print("SKIPPED {} = {}".format(srcthing, value))
            elif srcthing.startswith("GCLK_COL:"):
                colidx = srcthing[10]
                gclkidx = srcthing[12]
                gclkgclk['gclk{}cols'.format(gclkidx)].add(int(colidx))
            elif srcthing.startswith('GCLK_SOURCE:'):
                gclkidx = srcthing[13]
                gclkgclk['gclk{}src'.format(gclkidx)] = value.lower()
            else:
                print(srcthing, value)
        else:
            srcthing, dstthing = l.split(' -> ')

            if srcthing == "COMBOUT":
                x, y, n = parse_xysi(dstthing[10:])
                if n % 2 == 0:
                    lablablablab[(x, y)]['luts'][n // 2]['buf0'] = 'comb'
                else:
                    lablablablab[(x, y)]['luts'][n // 2]['buf1'] = 'comb'
            elif srcthing == "REGOUT":
                x, y, n = parse_xysi(dstthing[10:])
                if n % 2 == 0:
                    lablablablab[(x, y)]['luts'][n // 2]['buf0'] = 'reg'
                else:
                    lablablablab[(x, y)]['luts'][n // 2]['buf1'] = 'reg'
            elif dstthing.startswith("LUT"):
                luti = int(dstthing[3])
                lutinp = dstthing[5:].lower()

                x, y, llI = parse_xysi(srcthing[19:])

                lablablablab[(x, y)]['luts'][luti][lutinp] = llI
            elif dstthing.startswith("IO_DATAOUT"):
                _, _, outputI, _ = parse_xysi2(dstthing[11:])
                x, y, llI = parse_xysi(srcthing[19:])

                ioioioio[(x, y)]['ios'][outputI]['outputmux'] = llI
            elif dstthing.startswith("TILECLK"):
                x, y, clki = parse_xyi(dstthing[8:])
                assert srcthing[0:4] == "GCLK" # TODO
                lablablablab[(x, y)]['clk0' if clki == 0 else 'clk1'] = srcthing.lower()
            elif srcthing.startswith("TILECLK"):
                x, y, n = parse_xyi(dstthing[4:])
                if srcthing[7] == '0':
                    lablablablab[(x, y)]['luts'][n]['clkline1'] = False
                else:
                    lablablablab[(x, y)]['luts'][n]['clkline1'] = True
            else:
                dstmuxbox = get_mux_box(dstthing)
                if dstmuxbox is None:
                    assert srcthing.startswith("IO_DATAIN")

                    _, _, ioI, _ = parse_xysi2(srcthing[10:])

                    ioI = "N" + str(ioI)
                    x, y, trackI = parse_xyi(dstthing[2:])

                    if x == 1:
                        choices = LH_IO_TRACK_MUX[trackI]

                        bitL = choices[0] == ioI
                        bitR = choices[1] == ioI

                        assert bitL or bitR

                        if trackI < 2:
                            trackY = LUTYLOCS[4 - y] + 1
                        elif trackI < 4:
                            trackY = LUTYLOCS[4 - y] + 3
                        elif trackI < 6:
                            trackY = LUTYLOCS[4 - y] + 42
                        elif trackI < 8:
                            trackY = LUTYLOCS[4 - y] + 44

                        trackX = 3 if trackI % 2 == 0 else 5

                        if bitL:
                            setbit(data, trackX + 0, trackY)
                        if bitR:
                            setbit(data, trackX + 1, trackY)
                    elif y == 0:
                        # bottom
                        print(x, y, trackI, ioI)

                        choices = BOT_IO_TRACK_MUX[trackI % 5]

                        bitL = choices[0] == ioI
                        bitR = choices[1] == ioI

                        assert bitL or bitR

                        tileX = (x - 1) * 28 - 17
                        trackX = tileX + (0 if trackI < 5 else 24)
                        trackY = 196 + 2 * (trackI % 5)

                        if bitL:
                            if trackI < 5:
                                setbit(outoutout, trackX + 0, trackY + 0)
                            else:
                                setbit(outoutout, trackX + 3, trackY + 0)
                        if bitR:
                            if trackI < 5:
                                setbit(outoutout, trackX + 2, trackY + 1)
                            else:
                                setbit(outoutout, trackX + 1, trackY + 1)
                    elif y == 5:
                        # top
                        choices = BOT_IO_TRACK_MUX[4 - (trackI % 5)]

                        bitL = choices[0] == ioI
                        bitR = choices[1] == ioI

                        assert bitL or bitR

                        tileX = (x - 1) * 28 - 17
                        trackX = tileX + (0 if trackI < 5 else 24)
                        trackY = 1 + 2 * (trackI % 5)

                        if bitL:
                            if trackI < 5:
                                setbit(outoutout, trackX + 0, trackY + 1)
                            else:
                                setbit(outoutout, trackX + 3, trackY + 1)
                        if bitR:
                            if trackI < 5:
                                setbit(outoutout, trackX + 2, trackY + 0)
                            else:
                                setbit(outoutout, trackX + 1, trackY + 0)
                    else:
                        assert False
                else:
                    # print(dstmuxbox)
                    muxbits = interconnect_map[dstthing][srcthing]
                    # print(muxbits)
                    setbox(outoutout, dstmuxbox[0], dstmuxbox[1], muxbits)


# Stripes in pad ring
for x in range(208):
    for y in [232, 236, 238, 242, 244, 248, 250, 254]:
        setbit(outoutout, x, y)

# Dunno what this bit does
setbit(outoutout, 1, 9)

# Clocks for now
for X in range(2, 9):
    setbit(outoutout, (X - 1) * 28 - 16, 103, X in gclkgclk['gclk0cols'])
    setbit(outoutout, (X - 1) * 28 - 15, 103, X in gclkgclk['gclk1cols'])
    setbit(outoutout, (X - 1) * 28 - 13, 103, X in gclkgclk['gclk2cols'])
    setbit(outoutout, (X - 1) * 28 - 12, 103, X in gclkgclk['gclk3cols'])
setbit(outoutout, 5, 103, 1 in gclkgclk['gclk0cols'])
setbit(outoutout, 6, 103, 1 in gclkgclk['gclk1cols'])
setbit(outoutout, 7, 103, 1 in gclkgclk['gclk2cols'])
setbit(outoutout, 8, 103, 1 in gclkgclk['gclk3cols'])

setbit(outoutout, 18, 103, gclkgclk['gclk0src'] != None)
setbit(outoutout, 14, 103, gclkgclk['gclk1src'] != None)
setbit(outoutout, 4, 103, gclkgclk['gclk2src'] != None)
setbit(outoutout, 10, 103, gclkgclk['gclk3src'] != None)

# Extra things hack for now
setbit(outoutout, 2, LUTYLOCS[3 - 0] + 31)
setbit(outoutout, 2, LUTYLOCS[3 - 0] + 32)
setbit(outoutout, 2, LUTYLOCS[3 - 0] + 35)
setbit(outoutout, 2, LUTYLOCS[3 - 0] + 36)
setbit(outoutout, 2, LUTYLOCS[3 - 0] + 39)
setbit(outoutout, 2, LUTYLOCS[3 - 0] + 40)

setbit(outoutout, 2, LUTYLOCS[2 - 0] + 31)
setbit(outoutout, 2, LUTYLOCS[2 - 0] + 32)
setbit(outoutout, 2, LUTYLOCS[2 - 0] + 35)
setbit(outoutout, 2, LUTYLOCS[2 - 0] + 36)

setbit(outoutout, 2, LUTYLOCS[1 - 0] + 31)
setbit(outoutout, 2, LUTYLOCS[1 - 0] + 32)
setbit(outoutout, 2, LUTYLOCS[1 - 0] + 35)
setbit(outoutout, 2, LUTYLOCS[1 - 0] + 36)

setbit(outoutout, 2, LUTYLOCS[0 - 0] + 39)

# IOs
for ((X, Y), tileattribs) in ioioioio.items():
    for N in range(len(tileattribs['ios'])):
        attribs = tileattribs['ios'][N]
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

            setbit(outoutout, tileX + [27, 18, 11, 9][N], 0 if Y == 5 else 206, not attribs['schmitttrigger'])
            setbit(outoutout, tileX + [26, 17, 10, 8][N], 0 if Y == 5 else 206, attribs['enableinput'])

            outpY = (1 if N == 0 or N == 2 else 3) if Y == 5 else (204 if N == 0 or N == 2 else 202)

            setbit(outoutout, tileX + (11 if N >= 2 else 15), outpY + (1 if Y == 5 else 0), not attribs['invert'])
            setbit(outoutout, tileX + (11 if N >= 2 else 15), outpY + (5 if Y == 5 else -4), not attribs['invertoe'])

            if attribs['outputmux'] is None:
                output_to_find = "VDD ???"
            else:
                output_to_find = str(attribs['outputmux'])
            outputmuxbits = None
            for i in range(len(COL_IO_INPUTS)):
                if COL_IO_INPUTS[i][0] == output_to_find:
                    outputmuxbits = COL_IO_INPUTS[i][1:]
            # print(outputmuxbits)
            for bitX, bitY in outputmuxbits:
                if N >= 2:
                    setbit(outoutout, tileX + 8 + (3 - bitX), outpY + (bitY if Y == 5 else 1 - bitY))
                else:
                    if bitX != 0:
                        bitX += 1
                    setbit(outoutout, tileX + 15 + bitX, outpY + (bitY if Y == 5 else 1 - bitY))

            if attribs['oemux'] is None:
                output_to_find = "VDD ???"
            else:
                output_to_find = str(attribs['oemux'])
            outputmuxbits = None
            for i in range(len(COL_IO_INPUTS)):
                if COL_IO_INPUTS[i][0] == output_to_find:
                    outputmuxbits = COL_IO_INPUTS[i][1:]
            # print(outputmuxbits)
            for bitX, bitY in outputmuxbits:
                if N >= 2:
                    setbit(outoutout, tileX + 8 + (3 - bitX), outpY + (bitY + 4 if Y == 5 else 1 - bitY - 4))
                else:
                    if bitX != 0:
                        bitX += 1
                    setbit(outoutout, tileX + 15 + bitX, outpY + (bitY + 4 if Y == 5 else 1 - bitY - 4))

        if X == 1 or X == 8:
            tileY = LUTYLOCS[4 - Y]

            setbit(outoutout, 0 if X == 1 else 193, tileY + [1, 8, 14, 21, 28][N], not attribs['schmitttrigger'])
            setbit(outoutout, 0 if X == 1 else 193, tileY + [0, 7, 13, 20, 27][N], attribs['enableinput'])

            localY = tileY + 8 + N * 4
            if N >= 3:
                localY += 8

            setbit(outoutout, 2 if X == 1 else 191, localY + (1 if N < 3 else 0), not attribs['invert'])
            setbit(outoutout, 2 if X == 1 else 191, localY + (2 if N < 3 else -1), not attribs['invertoe'])

            if attribs['outputmux'] is not None:
                output_to_find = str(attribs['outputmux'])
                outputmuxbits = None
                for i in range(len(ROW_IO_INPUTS)):
                    if ROW_IO_INPUTS[i][0] == output_to_find:
                        outputmuxbits = ROW_IO_INPUTS[i][1:]
                # print(outputmuxbits)
                for bitX, bitY in outputmuxbits:
                    setbit(outoutout, (187 + bitX if X == 8 else 2 + (4 - bitX)), localY + (bitY if N < 3 else 1 - bitY))

            if attribs['oemux'] is not None:
                output_to_find = str(attribs['oemux'])
                outputmuxbits = None
                for i in range(len(ROW_IO_INPUTS)):
                    if ROW_IO_INPUTS[i][0] == output_to_find:
                        outputmuxbits = ROW_IO_INPUTS[i][1:]
                # print(outputmuxbits)
                for bitX, bitY in outputmuxbits:
                    setbit(outoutout, (187 + bitX if X == 8 else 2 + (4 - bitX)), localY + ((1 - bitY) + 2 if N < 3 else bitY - 2))

def lut_twiddle(lutbits):
    lutbox = []
    for _ in range(4):
        lutbox.append([False] * 4)

    lutbox[3][1] = bool(lutbits & (1 << 0))
    lutbox[3][0] = bool(lutbits & (1 << 1))
    lutbox[2][1] = bool(lutbits & (1 << 2))
    lutbox[2][0] = bool(lutbits & (1 << 3))

    lutbox[2][3] = bool(lutbits & (1 << 4))
    lutbox[2][2] = bool(lutbits & (1 << 5))
    lutbox[3][3] = bool(lutbits & (1 << 6))
    lutbox[3][2] = bool(lutbits & (1 << 7))

    lutbox[1][1] = bool(lutbits & (1 << 8))
    lutbox[1][0] = bool(lutbits & (1 << 9))
    lutbox[0][1] = bool(lutbits & (1 << 10))
    lutbox[0][0] = bool(lutbits & (1 << 11))

    lutbox[1][3] = bool(lutbits & (1 << 12))
    lutbox[1][2] = bool(lutbits & (1 << 13))
    lutbox[0][3] = bool(lutbits & (1 << 14))
    lutbox[0][2] = bool(lutbits & (1 << 15))

    return lutbox

# LABs
for ((X, Y), attribs) in lablablablab.items():
    lutX = (X - 1) * 28
    labY = LUTYLOCS[4 - Y]

    # Mystery bit
    setbit(outoutout, lutX + 5, labY + 23)

    # TODO: Just set these up for now
    setbit(outoutout, lutX + 4, labY + 20)
    setbit(outoutout, lutX + 5, labY + 20)
    setbit(outoutout, lutX + 5, labY + 21)
    setbit(outoutout, lutX + 1, labY + 24)
    setbit(outoutout, lutX + 0, labY + 25)
    setbit(outoutout, lutX + 5, labY + 25)
    setbit(outoutout, lutX + 6, labY + 25)

    for N in range(10):
        if N < 5:
            lutY = LUTYLOCS[4 - Y] + N * 4
        else:
            lutY = LUTYLOCS[4 - Y] + 46 - (N - 5) * 4 - 4

        lutattrib = attribs['luts'][N]
        lutbox = lut_twiddle(lutattrib['bits'])
        # print(lutbox)
        setbox(outoutout, lutX, lutY, lutbox, flipv=N >= 5)

        setbit(outoutout, lutX + 4, lutY + (0 if N < 5 else 3), not lutattrib['qfbk'])
        setbit(outoutout, lutX + 5, lutY + (0 if N < 5 else 3), not lutattrib['cin'])
        setbit(outoutout, lutX + 6, lutY + (0 if N < 5 else 3), not lutattrib['syncmode'])

        setbit(outoutout, lutX + 4, lutY + (1 if N < 5 else 2), lutattrib['buf1'] == 'reg')
        setbit(outoutout, lutX + 5, lutY + (1 if N < 5 else 2), lutattrib['buf0'] == 'reg')

        setbit(outoutout, lutX + 4, lutY + (2 if N < 5 else 1), not lutattrib['clkline1'])
        setbit(outoutout, lutX + 5, lutY + (2 if N < 5 else 1), lutattrib['regchain'])

        setbit(outoutout, lutX + 4, lutY + (3 if N < 5 else 0), lutattrib['lutchain'])
        setbit(outoutout, lutX + 5, lutY + (3 if N < 5 else 0), not lutattrib['aclrline1'])
        setbit(outoutout, lutX + 6, lutY + (3 if N < 5 else 0), lutattrib['bufL'] == 'reg')

        if lutattrib['dataa'] is not None:
            if isinstance(lutattrib['dataa'], int):
                val_to_find = "LAB" + str(lutattrib['dataa'])
            else:
                val_to_find = lutattrib['dataa']
            outputmuxbits = None
            for i in range(len(DATAA_INPUTS)):
                if DATAA_INPUTS[i][0] == val_to_find:
                    outputmuxbits = DATAA_INPUTS[i][1:]
            for bitX, bitY in outputmuxbits:
                setbit(outoutout, lutX - 9 + bitX, lutY + (bitY if N < 5 else 3 - bitY))

        if lutattrib['datab'] is not None:
            if isinstance(lutattrib['datab'], int):
                val_to_find = "LAB" + str(lutattrib['datab'])
            else:
                val_to_find = lutattrib['datab']
            outputmuxbits = None
            for i in range(len(DATAB_INPUTS)):
                if DATAB_INPUTS[i][0] == val_to_find:
                    outputmuxbits = DATAB_INPUTS[i][1:]
            for bitX, bitY in outputmuxbits:
                setbit(outoutout, lutX - 9 + bitX, lutY + (bitY if N < 5 else 3 - bitY))

        if lutattrib['datac'] is not None:
            if isinstance(lutattrib['datac'], int):
                val_to_find = "LAB" + str(lutattrib['datac'])
            else:
                val_to_find = lutattrib['datac']
            outputmuxbits = None
            for i in range(len(DATAC_INPUTS)):
                if DATAC_INPUTS[i][0] == val_to_find:
                    outputmuxbits = DATAC_INPUTS[i][1:]
            for bitX, bitY in outputmuxbits:
                setbit(outoutout, lutX - 9 + bitX, lutY + (bitY if N < 5 else 3 - bitY))

        if lutattrib['datad'] is not None:
            if isinstance(lutattrib['datad'], int):
                val_to_find = "LAB" + str(lutattrib['datad'])
            else:
                val_to_find = lutattrib['datad']
            outputmuxbits = None
            for i in range(len(DATAD_INPUTS)):
                if DATAD_INPUTS[i][0] == val_to_find:
                    outputmuxbits = DATAD_INPUTS[i][1:]
            for bitX, bitY in outputmuxbits:
                setbit(outoutout, lutX - 9 + bitX, lutY + (bitY if N < 5 else 3 - bitY))

with open(outfn, 'wb') as f:
    f.write(outoutout)
