import binascii
import sys
import struct

infn = sys.argv[1]

with open(infn, 'rb') as inf:
    indata = inf.read()

header = indata[:12]
payload = indata[12:]

print("Header", header)

while len(payload) > 0:
    pktid, pktlen = struct.unpack("<HI", payload[:6])
    # print(pktid, pktlen)
    pktpayload = payload[6:6 + pktlen]
    payload = payload[6 + pktlen:]

    print("Packet {:04X} len {}".format(pktid, pktlen))

    if pktid == 1:
        print(" Creator: \'{}\'".format(pktpayload))
    elif pktid == 2:
        print(" Device name: \'{}\'".format(pktpayload))
    elif pktid == 3:
        print(" Comment: \'{}\'".format(pktpayload))
    elif pktid == 5:
        print(" Security: \'{}\'".format(pktpayload))
    elif pktid == 8:
        print(" Terminator/CRC: \'{}\'".format(binascii.hexlify(pktpayload).decode('ascii')))
    elif pktid == 17:
        bitlen = struct.unpack("<I", pktpayload[6:10])[0]
        pkt_header = pktpayload[:12]
        actual_bits = pktpayload[12:]
        print(" Config, {} bits, header \'{}\'".format(bitlen, pkt_header))

        outfn = sys.argv[2]
        with open(outfn, 'wb') as outf:
            outf.write(actual_bits)

    elif pktid == 24:
        bitlen = struct.unpack("<I", pktpayload[6:10])[0]
        pkt_header = pktpayload[:12]
        actual_bits = pktpayload[12:]
        print(" User flash(?), {} bits, header \'{}\'".format(bitlen, pkt_header))

        outfn = sys.argv[3]
        with open(outfn, 'wb') as outf:
            outf.write(actual_bits)
