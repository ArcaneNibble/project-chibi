const SCALE_PX = 4;
const WIDTH = 487;
const HEIGHT = 512;

let ATTRIBS = new Array(WIDTH * HEIGHT);
let DID_ATTRIBS = false;

const LUTYLOCS = [11, 57, 103, 149, 195, 242, 288, 334, 380, 426];

function my_coords_to_byte_bit(x, y) {
    if (x < 313) {
        if (y < 366) {
            // upper left (short cols, long rows)
            let intermed_biti = x * 366 + y;

            intermed_biti += 61;

            let bytegroup_i = (intermed_biti / 61) | 0;
            let bytegroup_biti = intermed_biti % 61;

            bytegroup_biti += 3

            return [bytegroup_i * 8 + ((bytegroup_biti / 8) | 0), bytegroup_biti % 8]
        } else if (y >= 494 && y < 512) {
            // "stripe" bits
            let bytegroup_i = ((y - 494) / 3) | 0;
            let bytegroup_biti = (y - 494) % 3;

            bytegroup_i += 1;

            return [bytegroup_i * 8 + x * 48, bytegroup_biti]
        }
    } else if (x < 487) {
        if ((x != 486 && y < 488) || (x == 486 && y < 122)) {
            // right hand side (long cols, all rows incl short)
            let intermed_biti = (x - 313) * 488 + y;

            intermed_biti += 61 + (313 * 366);
            intermed_biti %= 199104;

            let bytegroup_i = (intermed_biti / 61) | 0;
            let bytegroup_biti = intermed_biti % 61;

            bytegroup_biti += 3

            return [bytegroup_i * 8 + ((bytegroup_biti / 8) | 0), bytegroup_biti % 8]
        } else if (x != 486 && y < 512) {
            // "stripe" bits, but there are more
            let bytegroup_i = ((y - 488) / 3) | 0;
            let bytegroup_biti = (y - 488) % 3;

            bytegroup_i += (0x3ab8 / 8);

            return [bytegroup_i * 8 + (x - 313) * 64, bytegroup_biti]
        } else if (x == 486 && y >= 506 && y < 512) {
            // last column of "stripe" bits
            let bytegroup_i = ((y - 506) / 3) | 0;
            let bytegroup_biti = (y - 506) % 3;

            bytegroup_i += (0x65f8 / 8);
            bytegroup_i %= (0x6600 / 8);

            return [bytegroup_i * 8, bytegroup_biti]
        }
    }
}

function draw_block_px(ctx, x, y, bit) {
    if (bit == -1) {
        ctx.fillStyle = "#808080";
        ctx.fillRect(x * SCALE_PX + 0,
                     y * SCALE_PX + 0,
                     SCALE_PX / 2, SCALE_PX / 2);
        ctx.fillRect(x * SCALE_PX + SCALE_PX / 2,
                     y * SCALE_PX + SCALE_PX / 2,
                     SCALE_PX / 2, SCALE_PX / 2);
        ctx.fillStyle = "#C0C0C0";
        ctx.fillRect(x * SCALE_PX + SCALE_PX / 2,
                     y * SCALE_PX + 0,
                     SCALE_PX / 2, SCALE_PX / 2);
        ctx.fillRect(x * SCALE_PX + 0,
                     y * SCALE_PX + SCALE_PX / 2,
                     SCALE_PX / 2, SCALE_PX / 2);
    } else if (bit == 0) {
        ctx.fillStyle = "#000000";
        ctx.fillRect(x * SCALE_PX, y * SCALE_PX, SCALE_PX, SCALE_PX);
    } else {
        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(x * SCALE_PX, y * SCALE_PX, SCALE_PX, SCALE_PX);
    }
}

function outline_box(ctx, x, y, w, h) {
    ctx.strokeRect(x * SCALE_PX + 0.5, y * SCALE_PX + 0.5, w * SCALE_PX - 1, h * SCALE_PX - 1);
}

function setattrib(x, y, w, h, str) {
    for (let dx = 0; dx < w; dx++) {
        for (let dy = 0; dy < h; dy++) {
            if (ATTRIBS[(y + dy) * WIDTH + (x + dx)]) {
                alert("BUG BUG BUG");
            }
            ATTRIBS[(y + dy) * WIDTH + (x + dx)] = str;
        }
    }
}

function u32str(x) {
    let s = x.toString(16);
    while (s.length < 8)
        s = "0" + s;
    return s;
}

function clear_canvas(ctx) {
    for (let x = 0; x < WIDTH; x++) {
        for (let y = 0; y < HEIGHT; y++) {
            draw_block_px(ctx, x, y, -1);
        }
    }
}

function draw_bitstream(ctx, bitstream) {
    for (let x = 0; x < WIDTH; x++) {
        for (let y = 0; y < HEIGHT; y++) {
            let bit_pos = my_coords_to_byte_bit(x, y);
            if (bit_pos) {
                let [bitstream_byte, bitstream_bit] = bit_pos;

                let bit = bitstream[bitstream_byte] & (1 << bitstream_bit);

                draw_block_px(ctx, x, y, bit);
            }
        }
    }
}

const LUT_COLOR = "#0000FF";
const LUT_INPUT_COLOR = "#00FF00";
const LOCAL_INTERCONNECT_COLOR = "#FF0000";
const LEFT_COLOR = "#8462D5";
const RIGHT_COLOR = "#65A10E";
const UP_COLOR = "#FA63D5";
const DOWN_COLOR = "#B8E450";

function draw_all_labels(ctx) {
    for (let x = 2; x < 18; x++) {
        let NUMROWS;
        if (x < 13) {
            NUMROWS = 7;
        } else {
            NUMROWS = 10;
        }
        for (let y = 1; y < NUMROWS + 1; y++) {
            for (let n = 0; n < 10; n++) {
                let boxY = LUTYLOCS[NUMROWS - y] + n * 4;
                if (n >= 5) boxY += 6;

                let realN = n;
                if (n >= 5) realN = 9 - (n - 5)

                // LUTs
                ctx.strokeStyle = LUT_COLOR;
                outline_box(ctx, (x - 1) * 28, boxY, 4, 4);
                if (!DID_ATTRIBS)
                    setattrib((x - 1) * 28, boxY, 4, 4, "LUT X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + "N" + realN);

                // LUT inputs
                ctx.strokeStyle = LUT_INPUT_COLOR;
                outline_box(ctx, (x - 1) * 28 - 9, boxY, 9, 4);
                if (!DID_ATTRIBS)
                    setattrib((x - 1) * 28 - 9, boxY, 9, 4, "LUT X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + "N" + realN + " inputs");
            }

            // LAB lines [5-12], [18-25] (on the "left" of the LUTs)
            ctx.strokeStyle = LOCAL_INTERCONNECT_COLOR;
            for (let nn = 0; nn < 8; nn++) {
                outline_box(ctx,
                    (x - 1) * 28 - 13,
                    LUTYLOCS[NUMROWS - y] + nn * 2,
                    4, 2);
                if (!DID_ATTRIBS)
                    setattrib(
                        (x - 1) * 28 - 13,
                        LUTYLOCS[NUMROWS - y] + nn * 2,
                        4, 2,
                        "LAB X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " LOCAL_INTERCONNECT " + (nn + 5));
                outline_box(ctx,
                    (x - 1) * 28 - 13,
                    LUTYLOCS[NUMROWS - y] + 30 + nn * 2,
                    4, 2);
                if (!DID_ATTRIBS)
                    setattrib(
                        (x - 1) * 28 - 13,
                        LUTYLOCS[NUMROWS - y] + 30 + nn * 2,
                        4, 2,
                        "LAB X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " LOCAL_INTERCONNECT " + (25 - nn));
            }

            // LAB lines [0-4], [13-17] (on the "right" of the LUTs)
            for (let nn = 0; nn < 5; nn++) {
                outline_box(ctx,
                    (x - 1) * 28 + 7,
                    LUTYLOCS[NUMROWS - y] + nn * 4 + 2,
                    4, 2);
                if (!DID_ATTRIBS)
                    setattrib(
                        (x - 1) * 28 + 7,
                        LUTYLOCS[NUMROWS - y] + nn * 4 + 2,
                        4, 2,
                        "LAB X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " LOCAL_INTERCONNECT " + nn);
                outline_box(ctx,
                    (x - 1) * 28 + 7,
                    LUTYLOCS[NUMROWS - y] + nn * 4 + 26,
                    4, 2);
                if (!DID_ATTRIBS)
                    setattrib(
                        (x - 1) * 28 + 7,
                        LUTYLOCS[NUMROWS - y] + nn * 4 + 26,
                        4, 2,
                        "LAB X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " LOCAL_INTERCONNECT " + (17 - nn));
            }
        }
    }

    ctx.strokeStyle = LEFT_COLOR;
    for (let x = 3; x < 19; x++) {
        let NUMROWS;
        if (x < 14) {
            NUMROWS = 7;
        } else {
            NUMROWS = 10;
        }
        for (let y = 1; y < NUMROWS + 1; y++) {
            // R4 going left
            for (let nn = 0; nn < 4; nn++) {
                outline_box(ctx,
                    (x - 1) * 28 - 21,
                    LUTYLOCS[NUMROWS - y] + nn * 4 + 4,
                    4, 2);
                if (!DID_ATTRIBS)
                    setattrib(
                        (x - 1) * 28 - 21,
                        LUTYLOCS[NUMROWS - y] + nn * 4 + 4,
                        4, 2,
                        "Left line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number " + nn)
                outline_box(ctx,
                    (x - 1) * 28 - 21,
                    LUTYLOCS[NUMROWS - y] + nn * 4 + 28,
                    4, 2);
                if (!DID_ATTRIBS)
                    setattrib(
                        (x - 1) * 28 - 21,
                        LUTYLOCS[NUMROWS - y] + nn * 4 + 28,
                        4, 2,
                        "Left line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number " + (nn + 4))
            }
        }
    }

    ctx.strokeStyle = RIGHT_COLOR;
    for (let x = 2; x < 18; x++) {
        let NUMROWS;
        if (x < 14) {
            NUMROWS = 7;
        } else {
            NUMROWS = 10;
        }
        for (let y = 1; y < NUMROWS + 1; y++) {
            // R4 going right
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 0,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 6,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 14,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 18,
                4, 2);

            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 26,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 30,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 38,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 44,
                4, 2);

            if (!DID_ATTRIBS) {
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 0,
                    4, 2,
                    "Right line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 0");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 6,
                    4, 2,
                    "Right line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 1");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 14,
                    4, 2,
                    "Right line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 2");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 18,
                    4, 2,
                    "Right line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 3");

                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 26,
                    4, 2,
                    "Right line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 4");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 30,
                    4, 2,
                    "Right line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 5");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 38,
                    4, 2,
                    "Right line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 6");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 44,
                    4, 2,
                    "Right line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 7");
            }
        }
    }

    // ctx.strokeStyle = LEFT_COLOR;
    // // Extra set of R4 (R1?) going left in the last column
    // for (let y = 1; y < 5; y++) {
    //     outline_box(ctx,
    //         (8 - 1) * 28 - 17,
    //         LUTYLOCS[4 - y] + 0,
    //         4, 2);
    //     outline_box(ctx,
    //         (8 - 1) * 28 - 17,
    //         LUTYLOCS[4 - y] + 6,
    //         4, 2);
    //     outline_box(ctx,
    //         (8 - 1) * 28 - 17,
    //         LUTYLOCS[4 - y] + 14,
    //         4, 2);
    //     outline_box(ctx,
    //         (8 - 1) * 28 - 17,
    //         LUTYLOCS[4 - y] + 18,
    //         4, 2);

    //     outline_box(ctx,
    //         (8 - 1) * 28 - 17,
    //         LUTYLOCS[4 - y] + 26,
    //         4, 2);
    //     outline_box(ctx,
    //         (8 - 1) * 28 - 17,
    //         LUTYLOCS[4 - y] + 30,
    //         4, 2);
    //     outline_box(ctx,
    //         (8 - 1) * 28 - 17,
    //         LUTYLOCS[4 - y] + 38,
    //         4, 2);
    //     outline_box(ctx,
    //         (8 - 1) * 28 - 17,
    //         LUTYLOCS[4 - y] + 44,
    //         4, 2);

    //     if (!DID_ATTRIBS) {
    //         setattrib(
    //             (8 - 1) * 28 - 17,
    //             LUTYLOCS[4 - y] + 0,
    //             4, 2,
    //             "Left 2 line from X8Y" + y + " number 0");
    //         setattrib(
    //             (8 - 1) * 28 - 17,
    //             LUTYLOCS[4 - y] + 6,
    //             4, 2,
    //             "Left 2 line from X8Y" + y + " number 1");
    //         setattrib(
    //             (8 - 1) * 28 - 17,
    //             LUTYLOCS[4 - y] + 14,
    //             4, 2,
    //             "Left 2 line from X8Y" + y + " number 2");
    //         setattrib(
    //             (8 - 1) * 28 - 17,
    //             LUTYLOCS[4 - y] + 18,
    //             4, 2,
    //             "Left 2 line from X8Y" + y + " number 3");

    //         setattrib(
    //             (8 - 1) * 28 - 17,
    //             LUTYLOCS[4 - y] + 26,
    //             4, 2,
    //             "Left 2 line from X8Y" + y + " number 4");
    //         setattrib(
    //             (8 - 1) * 28 - 17,
    //             LUTYLOCS[4 - y] + 30,
    //             4, 2,
    //             "Left 2 line from X8Y" + y + " number 5");
    //         setattrib(
    //             (8 - 1) * 28 - 17,
    //             LUTYLOCS[4 - y] + 38,
    //             4, 2,
    //             "Left 2 line from X8Y" + y + " number 6");
    //         setattrib(
    //             (8 - 1) * 28 - 17,
    //             LUTYLOCS[4 - y] + 44,
    //             4, 2,
    //             "Left 2 line from X8Y" + y + " number 7");
    //     }
    // }

    // ctx.strokeStyle = RIGHT_COLOR;
    // // Extra set of R4 going right in the first column
    // for (let y = 1; y < 5; y++) {
    //     outline_box(ctx,
    //         3,
    //         LUTYLOCS[4 - y] + 1,
    //         2, 1);
    //     outline_box(ctx,
    //         5,
    //         LUTYLOCS[4 - y] + 1,
    //         2, 1);

    //     outline_box(ctx,
    //         3,
    //         LUTYLOCS[4 - y] + 3,
    //         2, 1);
    //     outline_box(ctx,
    //         5,
    //         LUTYLOCS[4 - y] + 3,
    //         2, 1);

    //     outline_box(ctx,
    //         3,
    //         LUTYLOCS[4 - y] + 42,
    //         2, 1);
    //     outline_box(ctx,
    //         5,
    //         LUTYLOCS[4 - y] + 42,
    //         2, 1);

    //     outline_box(ctx,
    //         3,
    //         LUTYLOCS[4 - y] + 44,
    //         2, 1);
    //     outline_box(ctx,
    //         5,
    //         LUTYLOCS[4 - y] + 44,
    //         2, 1);

    //     if (!DID_ATTRIBS) {
    //         setattrib(
    //             3,
    //             LUTYLOCS[4 - y] + 1,
    //             2, 1,
    //             "Right line from X1Y" + y + " number 0");
    //         setattrib(
    //             5,
    //             LUTYLOCS[4 - y] + 1,
    //             2, 1,
    //             "Right line from X1Y" + y + " number 1");

    //         setattrib(
    //             3,
    //             LUTYLOCS[4 - y] + 3,
    //             2, 1,
    //             "Right line from X1Y" + y + " number 2");
    //         setattrib(
    //             5,
    //             LUTYLOCS[4 - y] + 3,
    //             2, 1,
    //             "Right line from X1Y" + y + " number 3");

    //         setattrib(
    //             3,
    //             LUTYLOCS[4 - y] + 42,
    //             2, 1,
    //             "Right line from X1Y" + y + " number 4");
    //         setattrib(
    //             5,
    //             LUTYLOCS[4 - y] + 42,
    //             2, 1,
    //             "Right line from X1Y" + y + " number 5");

    //         setattrib(
    //             3,
    //             LUTYLOCS[4 - y] + 44,
    //             2, 1,
    //             "Right line from X1Y" + y + " number 6");
    //         setattrib(
    //             5,
    //             LUTYLOCS[4 - y] + 44,
    //             2, 1,
    //             "Right line from X1Y" + y + " number 7");
    //     }
    // }

    for (let x = 2; x < 19; x++) {
        let NUMROWS;
        if (x < 13) {
            NUMROWS = 7;
        } else {
            NUMROWS = 10;
        }
        for (let y = 1; y < NUMROWS + 1; y++) {
            // C4 up
            ctx.strokeStyle = UP_COLOR;
            outline_box(ctx,
                (x - 1) * 28 - 21,
                LUTYLOCS[NUMROWS - y] + 0,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 4,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 10,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 16,
                4, 2);

            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 32,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 36,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 42,
                4, 2);
            if (!DID_ATTRIBS) {
                setattrib(
                    (x - 1) * 28 - 21,
                    LUTYLOCS[NUMROWS - y] + 0,
                    4, 2,
                    "Up line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 0");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 4,
                    4, 2,
                    "Up line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 1");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 10,
                    4, 2,
                    "Up line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 2");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 16,
                    4, 2,
                    "Up line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 3");

                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 32,
                    4, 2,
                    "Up line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 4");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 36,
                    4, 2,
                    "Up line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 5");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 42,
                    4, 2,
                    "Up line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 6");
            }

            // C4 down
            ctx.strokeStyle = DOWN_COLOR;
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 2,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 8,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 12,
                4, 2);

            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 28,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 34,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 17,
                LUTYLOCS[NUMROWS - y] + 40,
                4, 2);
            outline_box(ctx,
                (x - 1) * 28 - 21,
                LUTYLOCS[NUMROWS - y] + 44,
                4, 2);
            if (!DID_ATTRIBS) {
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 2,
                    4, 2,
                    "Down line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 0");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 8,
                    4, 2,
                    "Down line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 1");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 12,
                    4, 2,
                    "Down line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 2");

                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 28,
                    4, 2,
                    "Down line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 3");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 34,
                    4, 2,
                    "Down line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 4");
                setattrib(
                    (x - 1) * 28 - 17,
                    LUTYLOCS[NUMROWS - y] + 40,
                    4, 2,
                    "Down line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 5");
                setattrib(
                    (x - 1) * 28 - 21,
                    LUTYLOCS[NUMROWS - y] + 44,
                    4, 2,
                    "Down line from X" + (x - 1) + "Y" + (y + (x < 11 ? 3 : 0)) + " number 6");
            }
        }
    }

    DID_ATTRIBS = true;
}

window.onload = () => {
    // console.log('hi');
    let statuselem = document.getElementById('status');

    let canvaselem = document.getElementById('canvas');
    let ctx = canvaselem.getContext('2d');
    ctx.lineWidth = 1;

    clear_canvas(ctx);
    draw_all_labels(ctx);

    let file_contents = null;

    let lastX = -1;
    let lastY = -1;
    let captured_data = null;

    document.getElementById('clearbutton').onclick = () => {
        clear_canvas(ctx);
        draw_all_labels(ctx);

        captured_data = null;
    };

    document.getElementById('fileopen').onchange = e => {
        let file = e.target.files[0];
        if (!file) return;
        let reader = new FileReader();
        reader.onload = e => {
            file_contents = new Uint8Array(e.target.result);
            // console.log(file_contents);
            draw_bitstream(ctx, file_contents);
            draw_all_labels(ctx);

            captured_data = null;
        };
        reader.readAsArrayBuffer(file);
    };

    canvaselem.onmousemove = e => {
        // console.log(e.offsetX, e.offsetY);
        let x = (e.offsetX / SCALE_PX) | 0;
        let y = (e.offsetY / SCALE_PX) | 0;

        if (lastX != x || lastY != y) {
            // console.log(x, y);

            if (captured_data != null) {
                ctx.putImageData(captured_data, lastX * SCALE_PX, lastY * SCALE_PX);
            }
            captured_data = ctx.getImageData(x * SCALE_PX, y * SCALE_PX, SCALE_PX, SCALE_PX);

            // Draw selection box
            ctx.strokeStyle = "#FF00FF";
            outline_box(ctx, x, y, 1, 1);

            // Update text
            let status = "(" + x + ", " + y + ")<br>";

            // XXX check me
            let alteraLoc = "UNKNOWN/INVALID?";
            if (x <= 473 && y <= 482) {
                let alteraX = 473 - x;
                alteraLoc = (alteraX + y * 475).toString();
                alteraLoc += " (" + alteraX + ", " + y + ")";
            }

            status += "Altera bit number " + alteraLoc + "<br>";

            let bit_pos = my_coords_to_byte_bit(x, y);
            if (bit_pos) {
                let [bitstream_byte, bitstream_bit] = bit_pos;
                status += "Byte 0x" + u32str(bitstream_byte) + " bit " + bitstream_bit + "<br>";
            } else {
                status += "INVALID BYTE<br>";
            }

            if (ATTRIBS[y * WIDTH + x]) {
                status = status + ATTRIBS[y * WIDTH + x];
            } else {
                status = status + "UNKNOWN FUNCTION";
            }

            statuselem.innerHTML = status;

            lastX = x;
            lastY = y;
        }
    };
};
