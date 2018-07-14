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

outoutout = bytearray(b'\xff' * 0x1a00)

def setbit(data, x, y, val=False):
    byte_i, bit_i = my_coords_to_byte_bit(x, y)
    if val:
        data[byte_i] |= (1 << bit_i)
    else:
        data[byte_i] &= ~(1 << bit_i)

# Stripes in pad ring
for x in range(208):
    for y in [232, 236, 238, 242, 244, 248, 250, 254]:
        setbit(outoutout, x, y)

# Dunno what this bit does
setbit(outoutout, 1, 9)

with open(outfn, 'wb') as f:
    f.write(outoutout)
