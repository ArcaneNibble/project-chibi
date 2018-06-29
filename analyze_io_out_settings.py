from cfmdump2 import getbit
import json

fastslew_bits = {}
bushold_bits = {}
pullup_bits = {}

def analyze_io_at(X, Y, N):
    with open('output-modes/IOC_X{}_Y{}_N{}_baseline.pof.cfm'.format(X, Y, N), 'rb') as f:
        baseline = f.read()
    with open('output-modes/IOC_X{}_Y{}_N{}_fastslew.pof.cfm'.format(X, Y, N), 'rb') as f:
        fastslew = f.read()
    with open('output-modes/IOC_X{}_Y{}_N{}_bushold.pof.cfm'.format(X, Y, N), 'rb') as f:
        bushold = f.read()
    with open('output-modes/IOC_X{}_Y{}_N{}_pullup.pof.cfm'.format(X, Y, N), 'rb') as f:
        pullup = f.read()

    fastslewbit = None
    for y in range(232, 256):
        for x in range(208):
            bitbaseline = getbit(baseline, x, y)
            bitfastslew = getbit(fastslew, x, y)

            if bitbaseline != bitfastslew:
                assert fastslewbit is None
                fastslewbit = (x, y)
                print("IOC_X{}_Y{}_N{} fast slew ({}, {})".format(X, Y, N, x,  y))
    assert fastslewbit is not None
    fastslew_bits["IOC_X{}_Y{}_N{}".format(X, Y, N)] = fastslewbit

    busholdbit = None
    for y in range(232, 256):
        for x in range(208):
            bitbaseline = getbit(fastslew, x, y)
            bitbushold = getbit(bushold, x, y)

            if bitbaseline != bitbushold:
                assert busholdbit is None
                busholdbit = (x, y)
                print("IOC_X{}_Y{}_N{} bus hold ({}, {})".format(X, Y, N, x,  y))
    assert busholdbit is not None
    bushold_bits["IOC_X{}_Y{}_N{}".format(X, Y, N)] = busholdbit

    pullupbit = None
    for y in range(232, 256):
        for x in range(208):
            bitbaseline = getbit(fastslew, x, y)
            bitpullup = getbit(pullup, x, y)

            if bitbaseline != bitpullup:
                assert pullupbit is None
                pullupbit = (x, y)
                print("IOC_X{}_Y{}_N{} pull up ({}, {})".format(X, Y, N, x,  y))
    assert pullupbit is not None
    pullup_bits["IOC_X{}_Y{}_N{}".format(X, Y, N)] = pullupbit

for X in [1, 8]:
    for Y in [1, 2, 3, 4]:
        for N in range(4 if X == 1 or Y == 2 else 5):
            analyze_io_at(X, Y, N)

for X in [2, 3, 4, 5, 6, 7]:
    for Y in [0, 5]:
        for N in range(3 if X == 4 or (X == 2 and Y == 5) or (X == 7 and Y == 0) else 4):
            analyze_io_at(X, Y, N)

# print(fastslew_bits)

with open('io-fast-slew.json', 'w') as f:
    json.dump(fastslew_bits, f)
with open('io-bus-hold.json', 'w') as f:
    json.dump(bushold_bits, f)
with open('io-pull-up.json', 'w') as f:
    json.dump(pullup_bits, f)

