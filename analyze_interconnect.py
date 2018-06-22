import json
import sys

with open(sys.argv[1], 'r') as f:
    x = json.load(f)
with open('my_wire_to_quartus_wire.json', 'r') as f:
    wirenamemap = json.load(f)

print("----- There are {} muxes in the database".format(len(x)))
print("----- There are {} routing pairs in the database".format(sum((len(v) for k, v in x.items()))))

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

    return (int(inp[xpos + 1:ypos]), int(inp[ypos + 1:ipos]), int(inp[ipos + 1:]))

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
        return 0
    if C:
        if A: return 1
        if B: return 2
        if E: return 3
        if F: return 4
    if D:
        if A: return 5
        if B: return 6
        if E: return 7
        if F: return 8
    if H:
        if A: return 9
        if B: return 10
        if E: return 11
        if F: return 12

def flipv(muxbits):
    return muxbits[::-1]

def fliph(muxbits):
    return [x[::-1] for x in muxbits]

# # print(x)
# uniq_r_muxes = []
# for _ in range(8):
#     uniq_r_muxes.append(set())

# for X in range(2, 8):
#     for Y in range(1, 5):
#         for N in range(8):
#             mux = "R:X{}Y{}I{}".format(X, Y, N)
#             muxvals = x[mux]
#             # print(muxvals)
#             for muxsrc, muxbits in muxvals.items():
#                 uniq_r_muxes[N].add(bits2str(muxbits))

# # print(uniq_r_muxes)
# for N in range(8):
#     print("~~~~~ R{} ~~~~~".format(N))
#     for xx in sorted(list(uniq_r_muxes[N])):
#         print(xx)

# # print(x)
# uniq_l_muxes = []
# for _ in range(8):
#     uniq_l_muxes.append(set())

# # print(x)
# uniq_l2_muxes = []
# for _ in range(8):
#     uniq_l2_muxes.append(set())

# for X in [8]:
#     for Y in range(1, 5):
#         for N in range(8):
#             mux = "L2:X{}Y{}I{}".format(X, Y, N)
#             muxvals = x[mux]
#             # print(muxvals)
#             for muxsrc, muxbits in muxvals.items():
#                 uniq_l2_muxes[N].add(bits2str(muxbits))

# # print(uniq_l2_muxes)
# for N in range(8):
#     print("~~~~~ L2:{} ~~~~~".format(N))
#     for xx in sorted(list(uniq_l2_muxes[N])):
#         print(xx)

# # print(x)
# uniq_l_muxes = []
# for _ in range(8):
#     uniq_l_muxes.append(set())

# for X in range(3, 9):
#     for Y in range(1, 5):
#         for N in range(8):
#             mux = "L:X{}Y{}I{}".format(X, Y, N)
#             muxvals = x[mux]
#             # print(muxvals)
#             for muxsrc, muxbits in muxvals.items():
#                 uniq_l_muxes[N].add(bits2str(muxbits))

# # print(uniq_l_muxes)
# for N in range(8):
#     print("~~~~~ L{} ~~~~~".format(N))
#     for xx in sorted(list(uniq_l_muxes[N])):
#         print(xx)

# uniq_u_muxes = []
# for _ in range(7):
#     uniq_u_muxes.append(set())

# for X in [8]:#range(2, 8):
#     for Y in range(1, 5):
#         for N in range(7):
#             mux = "U:X{}Y{}I{}".format(X, Y, N)
#             muxvals = x[mux]
#             # print(muxvals)
#             for muxsrc, muxbits in muxvals.items():
#                 uniq_u_muxes[N].add(bits2str(muxbits))

# # print(uniq_r_muxes)
# for N in range(7):
#     print("~~~~~ U{} ~~~~~".format(N))
#     for xx in sorted(list(uniq_u_muxes[N])):
#         print(xx)

# uniq_d_muxes = []
# for _ in range(7):
#     uniq_d_muxes.append(set())

# for X in [8]:#range(2, 8):
#     for Y in range(1, 5):
#         for N in range(7):
#             mux = "D:X{}Y{}I{}".format(X, Y, N)
#             muxvals = x[mux]
#             # print(muxvals)
#             for muxsrc, muxbits in muxvals.items():
#                 uniq_d_muxes[N].add(bits2str(muxbits))

# # print(uniq_r_muxes)
# for N in range(7):
#     print("~~~~~ D{} ~~~~~".format(N))
#     for xx in sorted(list(uniq_d_muxes[N])):
#         print(xx)

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
    for src, muxbits in srcs.items():
        if dst.startswith("R:"):
            _, _, I = parse_xyi(dst)
            if I >= 4:
                muxbits = flipv(muxbits)
        elif dst.startswith("L:") or dst.startswith("L2"):
            _, _, I = parse_xyi(dst)
            muxbits = fliph(muxbits)
            if I >= 4:
                muxbits = flipv(muxbits)
        elif dst.startswith("U:"):
            X, _, I = parse_xyi(dst)
            if X == 8:
                muxbits = fliph(muxbits)

            if I == 0 and X != 8:
                muxbits = fliph(muxbits)
            if I >= 4:
                muxbits = flipv(muxbits)
        elif dst.startswith("D:"):
            X, _, I = parse_xyi(dst)
            if X == 8:
                muxbits = fliph(muxbits)

            if I == 6 and X != 8:
                muxbits = fliph(muxbits)
            if I >= 3:
                muxbits = flipv(muxbits)
        else:
            continue

        muxidx = decodemux(muxbits)

        if srcs_decoded[muxidx] is not None:
            print(dst, src, srcs_decoded[muxidx])
        assert srcs_decoded[muxidx] is None
        srcs_decoded[muxidx] = src

    print("~~~~~ {} ~~~~~".format(dst))
    print(LABELS[0])
    for i in range(len(srcs_decoded)):
        print(LABELS[i + 1], end='')
        src = srcs_decoded[i]
        if src is None:
            print("???")
        else:
            print(src, end='')
            if src in wirenamemap:
                print(" ({})".format(wirenamemap[src]))
            else:
                print()

        # if dst.startswith("LOCAL_INTERCONNECT:"):
        #     continue

        # print(dst, src)

        # if dst.startswith("L:"):
        #     _, _, I = parse_xyi(dst)
        #     muxbits = fliph(muxbits)
        #     if I >= 4:
        #         muxbits = flipv(muxbits)
        # if dst.startswith("R:"):
        #     _, _, I = parse_xyi(dst)
        #     if I >= 4:
        #         muxbits = flipv(muxbits)
        # if dst.startswith("D:"):
        #     X, _, I = parse_xyi(dst)
        #     if I >= 3:
        #         muxbits = flipv(muxbits)
        #     if I == 6:
        #         muxbits = fliph(muxbits)
        #     if X == 8:
        #         muxbits = fliph(muxbits)
        # if dst.startswith("U:"):
        #     X, _, I = parse_xyi(dst)
        #     if I >= 4:
        #         muxbits = flipv(muxbits)
        #     if I == 0:
        #         muxbits = fliph(muxbits)
        #     if X == 8:
        #         muxbits = fliph(muxbits)
        # if dst.startswith("L2:"):
        #     _, _, I = parse_xyi(dst)
        #     if I >= 4:
        #         muxbits = flipv(muxbits)

        # decodemux(muxbits)
