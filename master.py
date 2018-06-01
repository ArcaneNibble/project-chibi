import cfmdiff

def main():
    bits = []
    for _ in range(112):
        bits.append([None] * 64)

    # Dummy bits?
    for y in range(112):
        bits[y][0] = (b"?0", b"DUMMY0", b"Appears to be constantly 0")
        bits[y][33] = (b"?0", b"DUMMY0", b"Appears to be constantly 0")

    tabletabletable = b'<table id="thetable">'

    tabletabletable += b'<tr><th>Byte</th><th colspan="8">+0</th><th colspan="8">+1</th><th colspan="8">+2</th><th colspan="8">+3</th><th colspan="8">+4</th><th colspan="8">+5</th><th colspan="8">+6</th><th colspan="8">+7</th></tr>'

    tabletabletable += b'<tr><th>Bit</th>'
    for _ in range(8):
        tabletabletable += b'<th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th>'
    tabletabletable += b'</tr>'

    for y in range(112):
        tabletabletable += b'<tr>'

        byterange = "<th>0x{:03X}-0x{:03X}</th>".format(y * 8, y * 8 + 7).encode('ascii')
        tabletabletable += byterange

        for x in range(64):
            bit = bits[y][x]
            if bit is None:
                tabletabletable += b'<td>?</td>'
            else:
                shortdesc, bitclass, longdesc = bit

                tooltip = b'<div class="tooltip">' + shortdesc + \
                    b'<span class="tooltiptext">' + longdesc + b'</span></div>'

                tabletabletable += b'<td class="' + bitclass + b'">' + tooltip + b'</td>'
        tabletabletable += b'</tr>'
    tabletabletable += b'</table>'

    # print(bits)
    with open("tmpl.html", "rb") as f:
        TMPL = f.read()

    outoutout = TMPL.replace(b'_____CONTENTHERE_____', tabletabletable)
    with open("outoutout.html", "wb") as f:
        f.write(outoutout)

if __name__=='__main__':
    main()
