from cfmdump2 import getbit
import json

with open('io-bus-hold.json', 'r') as f:
    busholdbits = json.load(f)
with open('io-pull-up.json', 'r') as f:
    pullupbits = json.load(f)
with open('io-fast-slew.json', 'r') as f:
    slewratebits = json.load(f)
with open('io-low-current.json', 'r') as f:
    lowcurrentbits = json.load(f)

allotherbits = set()

for _, v in busholdbits.items():
    allotherbits.add(tuple(v))
for _, v in pullupbits.items():
    allotherbits.add(tuple(v))
for _, v in slewratebits.items():
    allotherbits.add(tuple(v))
for _, v in lowcurrentbits.items():
    allotherbits.add(tuple(v[0]))
    allotherbits.add(tuple(v[1]))

opendrain_bits = {}

def analyze_io_at(X, Y, N):
    with open('fuzz-od/IOC_X{}_Y{}_N{}.pof.cfm'.format(X, Y, N), 'rb') as f:
        baseline = f.read()

    opendrainbit = None
    for y in [234, 237, 240, 243, 246, 249, 252, 255]:
        for x in range(208):
            if (x, y) in allotherbits:
                continue

            if not getbit(baseline, x, y):
                assert opendrainbit is None
                opendrainbit = (x, y)
                print("IOC_X{}_Y{}_N{} open drain ({}, {})".format(X, Y, N, x,  y))
    assert opendrainbit is not None
    opendrain_bits["IOC_X{}_Y{}_N{}".format(X, Y, N)] = opendrainbit

for X in [1, 8]:
    for Y in [1, 2, 3, 4]:
        for N in range(4 if X == 1 or Y == 2 else 5):
            analyze_io_at(X, Y, N)

for X in [2, 3, 4, 5, 6, 7]:
    for Y in [0, 5]:
        for N in range(3 if X == 4 or (X == 2 and Y == 5) or (X == 7 and Y == 0) else 4):
            analyze_io_at(X, Y, N)

# print(opendrain_bits)

with open('io-open-drain.json', 'w') as f:
    json.dump(opendrain_bits, f)
