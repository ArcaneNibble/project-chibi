import sys

fn1 = sys.argv[1]
fn2 = sys.argv[2]

with open(fn1, 'rb') as f:
    f1 = f.read()

with open(fn2, 'rb') as f:
    f2 = f.read()

assert len(f1) == len(f2)

for byte_i in range(len(f1)):
    byte1 = f1[byte_i]
    byte2 = f2[byte_i]

    if byte1 != byte2:
        for bit_i in range(8):
            bit1 = byte1 & (1 << bit_i)
            bit2 = byte2 & (1 << bit_i)

            if bit1 != bit2:
                if bit1:
                    print("Bit became UNSET at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0))
                else:
                    print("Bit became  SET  at 0x{:04X} bit {} ({:03X})".format(byte_i, bit_i, byte_i - 0xC0))
