from runner import *
import os
import shutil
import queue
import threading

BASE_DIR = '/home/rqou/.local/share/lxc/altera-quartus-prime-lite-18/rootfs/home/rqou'

VLOG_TMPL = """module maxvtest(input a, input b, input c, input d, output o);

maxv_lcell my_lcell (
    .dataa(a),
    .datab(b),
    .datac(c),
    .datad(d),
    .combout(o));
defparam my_lcell.operation_mode = "normal";
defparam my_lcell.synch_mode = "off";
defparam my_lcell.register_cascade_mode = "off";
defparam my_lcell.sum_lutc_input = "datac";
defparam my_lcell.lut_mask = "{:04X}";
defparam my_lcell.output_mode = "comb_only";

endmodule
"""

QPF_TMPL = """QUARTUS_VERSION = "18.0"
DATE = "03:45:37  May 30, 2018"

PROJECT_REVISION = "maxvtest"
"""

QSF_TMPL = """set_global_assignment -name FAMILY "MAX V"
set_global_assignment -name DEVICE 5M40ZE64A5
set_global_assignment -name TOP_LEVEL_ENTITY maxvtest
set_global_assignment -name ORIGINAL_QUARTUS_VERSION 18.0.0
set_global_assignment -name PROJECT_CREATION_TIME_DATE "03:45:37  MAY 30, 2018"
set_global_assignment -name LAST_QUARTUS_VERSION "18.0.0 Lite Edition"
set_global_assignment -name PROJECT_OUTPUT_DIRECTORY output_files
set_global_assignment -name MIN_CORE_JUNCTION_TEMP "-40"
set_global_assignment -name MAX_CORE_JUNCTION_TEMP 125
set_global_assignment -name ERROR_CHECK_FREQUENCY_DIVISOR "-1"
set_global_assignment -name EDA_SIMULATION_TOOL "ModelSim-Altera (Verilog)"
set_global_assignment -name EDA_TIME_SCALE "1 ps" -section_id eda_simulation
set_global_assignment -name EDA_OUTPUT_DATA_FORMAT "VERILOG HDL" -section_id eda_simulation
set_global_assignment -name VERILOG_FILE top.v
set_location_assignment PIN_21 -to a
set_location_assignment PIN_20 -to b
set_location_assignment PIN_19 -to c
set_location_assignment PIN_18 -to d
set_location_assignment PIN_22 -to o
set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
set_location_assignment LC_X{}_Y{}_N{} -to my_lcell
set_global_assignment -name NUM_PARALLEL_PROCESSORS 1
"""

RCF_TMPL = """section global_data {
    rcf_written_by = "Quartus Prime 18.0 Build 614";
    device = 5M40ZE64A5;
}

signal_name = a {
    zero_or_more, *;
    dest = ( my_lcell, DATAA ), route_port = DATAA;
}
signal_name = b {
    zero_or_more, *;
    dest = ( my_lcell, DATAB ), route_port = DATAB;
}
signal_name = c {
    zero_or_more, *;
    dest = ( my_lcell, DATAC ), route_port = DATAC;
}
signal_name = d {
    zero_or_more, *;
    dest = ( my_lcell, DATAD ), route_port = DATAD;
}
"""

NTHREADS = 20

def fuzz_lut_at(x, y, n):
    this_lut_dir = 'lutfuzz/X{}_Y{}_N{}'.format(x, y, n)
    os.mkdir(BASE_DIR + '/' + this_lut_dir)

    with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.qpf', 'w') as f:
        f.write(QPF_TMPL)

    with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.qsf', 'w') as f:
        f.write(QSF_TMPL.format(x, y, n))

    with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.rcf', 'w') as f:
        f.write(RCF_TMPL)

    for lut_contents_i in [0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020, 0x0040, 0x0080,
                           0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x2000, 0x4000, 0x8000]:

        with open(BASE_DIR + '/' + this_lut_dir + '/top.v', 'w') as f:
            f.write(VLOG_TMPL.format(lut_contents_i))

        run_one_flow(this_lut_dir, False, True)

        shutil.copy(BASE_DIR + '/' + this_lut_dir + '/output_files/maxvtest.pof', 'lutfuzz_X{}_Y{}_N{}_bits{:04X}.pof'.format(x, y, n, lut_contents_i))

def main():
    os.mkdir(BASE_DIR + '/lutfuzz')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    for x in [2, 3, 4, 5, 6, 7]:
        for y in [1, 2, 3, 4]:
            for n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                workqueue.put((x, y, n))
                num_items += 1

    def threadfn():
        while True:
            try:
                x, y, n = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on X{}_Y{}_N{}".format(x, y, n))
            fuzz_lut_at(x, y, n)
            donequeue.put((x, y, n))

    for _ in range(NTHREADS):
        t = threading.Thread(target=threadfn)
        t.start()

    while num_items:
        x, y, n = donequeue.get()
        print("Finished X{}_Y{}_N{}".format(x, y, n))
        num_items -= 1

if __name__=='__main__':
    main()
