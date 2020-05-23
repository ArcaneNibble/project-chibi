#!/usr/bin/env python3

import json
import sys

dev = sys.argv[1]
if len(sys.argv) >= 3 and sys.argv[2] == "skipdummy":
    skipdummy = True
else:
    skipdummy = False

with open('routing-bits-{}.json'.format(dev), 'r') as f:
    x = json.load(f)
with open('wire-name-map-{}.json'.format(dev), 'r') as f:
    wirenamemap = json.load(f)

print("----- There are {} muxes in the database".format(len(x)))
print("----- There are {} routing pairs in the database".format(
    sum((len(v) for k, v in x.items()))))
print("----- There are {} *real* routing pairs in the database".format(
    sum((len([x for x in v
        if not x.startswith("R4:") and not x.startswith("C4:")])
        for k, v in x.items()))))


def bits2str(bits):
    ret = ""
    for row in bits:
        rowstr = ""
        for bit in row:
            rowstr += "1" if bit else "0"
        ret += rowstr + '\n'
    return ret


def parse_xyi(inp):
    xpos = inp.find('X')
    ypos = inp.find('Y')
    ipos = inp.find('I')

    assert xpos >= 0
    assert ypos > xpos
    assert ipos > ypos

    return (int(inp[xpos + 1:ypos]),
            int(inp[ypos + 1:ipos]),
            int(inp[ipos + 1:]))


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

    return (int(inp[xpos + 1:ypos]),
            int(inp[ypos + 1:spos]),
            int(inp[ipos + 1:]))


def anybits(bits):
    for y in bits:
        for x in y:
            if not x:
                return True
    return False


def decodemux(bits):
    A = not bits[0][0]
    B = not bits[0][1]
    C = not bits[0][2]
    D = not bits[0][3]
    E = not bits[1][0]
    F = not bits[1][1]
    G = not bits[1][2]
    H = not bits[1][3]

    assert G + C + D + H == 1
    assert A + B + E + F == 1 or (A + B + E + F == 0 and G)
    if G:
        assert A + B + C + D + E + F + H == 0

    if G:
        return 0
    if C:
        if A:
            return 1
        if B:
            return 2
        if E:
            return 3
        if F:
            return 4
    if D:
        if A:
            return 5
        if B:
            return 6
        if E:
            return 7
        if F:
            return 8
    if H:
        if A:
            return 9
        if B:
            return 10
        if E:
            return 11
        if F:
            return 12


def flipv(muxbits):
    return muxbits[::-1]


def fliph(muxbits):
    return [x[::-1] for x in muxbits]


def is_left_io(x, y):
    if dev == "240":
        return x == 1
    else:
        return x == 0


def is_right_io(x, y):
    if dev == "240":
        return x == 8
    elif dev == "570":
        return x == 13
    elif dev == "1270":
        return x == 17
    elif dev == "2210":
        return x == 21
    else:
        assert False


def is_top_io(x, y):
    if dev == "240":
        return y == 5
    elif dev == "570":
        return y == 8
    elif dev == "1270":
        return y == 11
    elif dev == "2210":
        return y == 14
    else:
        assert False


def is_bot_io(x, y):
    if dev == "240":
        return y == 0
    elif dev == "570":
        if x < 9:
            return y == 3
        else:
            return y == 0
    elif dev == "1270":
        if x < 11:
            return y == 3
        else:
            return y == 0
    elif dev == "2210":
        if x < 13:
            return y == 3
        else:
            return y == 0
    else:
        assert False


def is_ufm_corner(x, y):
    if dev == "240":
        return False
    elif dev == "570":
        return x == 9 and (y == 2 or y == 3)
    elif dev == "1270":
        return x == 11 and (y == 2 or y == 3)
    elif dev == "2210":
        return x == 13 and (y == 2 or y == 3)
    else:
        assert False


LABELS = [
    "|G|C|D|H|A|B|E|F|",
    "|0| | | | | | | |       ",
    "| |0| | |0| | | |       ",
    "| |0| | | |0| | |       ",
    "| |0| | | | |0| |       ",
    "| |0| | | | | |0|       ",
    "| | |0| |0| | | |       ",
    "| | |0| | |0| | |       ",
    "| | |0| | | |0| |       ",
    "| | |0| | | | |0|       ",
    "| | | |0|0| | | |       ",
    "| | | |0| |0| | |       ",
    "| | | |0| | |0| |       ",
    "| | | |0| | | |0|       ",
]

for dst, srcs in x.items():
    srcs_decoded = [None] * 13
    is_tb_io = False
    for src, muxbits in srcs.items():
        if dst.startswith("R:"):
            _, _, I = parse_xyi(dst)
            if I >= 4:
                muxbits = flipv(muxbits)
        elif (dst.startswith("L:") or dst.startswith(
              "L2:") or dst.startswith("R2:")):
            _, _, I = parse_xyi(dst)
            muxbits = fliph(muxbits)
            if I >= 4:
                muxbits = flipv(muxbits)
        elif dst.startswith("U:"):
            X, Y, I = parse_xyi(dst)
            if is_right_io(X, Y):
                muxbits = fliph(muxbits)

            if I == 0 and not is_right_io(X, Y):
                muxbits = fliph(muxbits)
            if I >= 4:
                muxbits = flipv(muxbits)
        elif dst.startswith("D:"):
            X, Y, I = parse_xyi(dst)
            if is_right_io(X, Y):
                muxbits = fliph(muxbits)

            if I == 6 and not is_right_io(X, Y):
                muxbits = fliph(muxbits)
            if I >= 3:
                muxbits = flipv(muxbits)
        elif dst.startswith("LOCAL_INTERCONNECT:"):
            X, Y, I = parse_xysi(dst[19:])
            if is_left_io(X, Y):
                muxbits = fliph(muxbits)
                if I > 8:
                    muxbits = flipv(muxbits)
            elif is_right_io(X, Y):
                if I > 8:
                    muxbits = flipv(muxbits)
            else:
                is_tb_io = is_top_io(X, Y) or is_bot_io(X, Y)
                if is_tb_io:
                    if is_bot_io(X, Y):
                        muxbits = flipv(muxbits)
                    if I < 5:
                        muxbits = fliph(muxbits)
                elif is_ufm_corner(X, Y):
                    muxbits = fliph(muxbits)
                    if I >= 5:
                        muxbits = flipv(muxbits)
                else:
                    if I in range(0, 5) or I in range(13, 18):
                        muxbits = fliph(muxbits)
                    if I >= 13:
                        muxbits = flipv(muxbits)
        else:
            print(dst)
            assert False

        # print(dst)
        muxidx = decodemux(muxbits)

        if srcs_decoded[muxidx] is not None:
            print(dst, src, srcs_decoded[muxidx])
        assert srcs_decoded[muxidx] is None
        srcs_decoded[muxidx] = src

    print("~~~~~ {} ~~~~~".format(dst))
    print(LABELS[0])
    if is_tb_io:
        assert srcs_decoded[0] is None
    for i in range(len(srcs_decoded)):
        if is_tb_io and i == 0:
            continue
        print(LABELS[i + 1], end='')
        src = srcs_decoded[i]
        if src is None:
            print("???")
        elif src.startswith("R4:") or src.startswith("C4:"):
            if skipdummy:
                print("???")
            else:
                print("*DUMMY* ({})".format(src))
        else:
            print(src, end='')
            if src in wirenamemap:
                print(" ({})".format(wirenamemap[src]))
            else:
                print()
