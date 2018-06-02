from runner import *
import os
import shutil
import queue
import threading

BASE_DIR = '/home/rqou/.local/share/lxc/altera-quartus-prime-lite-18/rootfs/home/rqou'

VLOG_TMPL = """module maxvtest(input a, input b, input c, output o);

wire intermed;

maxv_lcell my_lcell1 (
    .dataa(a),
    .datab(b),
    .combout(intermed));
defparam my_lcell1.operation_mode = "normal";
defparam my_lcell1.synch_mode = "off";
defparam my_lcell1.register_cascade_mode = "off";
defparam my_lcell1.sum_lutc_input = "datac";
defparam my_lcell1.lut_mask = "8888";
defparam my_lcell1.output_mode = "comb_only";

maxv_lcell my_lcell2 (
    .dataa(intermed),
    .datab(c),
    .combout(o));
defparam my_lcell2.operation_mode = "normal";
defparam my_lcell2.synch_mode = "off";
defparam my_lcell2.register_cascade_mode = "off";
defparam my_lcell2.sum_lutc_input = "datac";
defparam my_lcell2.lut_mask = "8888";
defparam my_lcell2.output_mode = "comb_only";

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
set_location_assignment PIN_22 -to o
set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
set_location_assignment LC_X{}_Y{}_N{} -to intermed
set_location_assignment LC_X{}_Y{}_N{} -to my_lcell2
set_global_assignment -name NUM_PARALLEL_PROCESSORS 1
"""

RCF_TMPL = """section global_data {{
    rcf_written_by = "Quartus Prime 18.0 Build 614";
    device = 5M40ZE64A5;
}}

signal_name = a {{
    zero_or_more, *;
    dest = ( intermed, DATAA ), route_port = DATAA;
}}

signal_name = b {{
    zero_or_more, *;
    dest = ( intermed, DATAB ), route_port = DATAB;
}}

signal_name = intermed {{
    LOCAL_LINE:*;
    dest = ( my_lcell2, DATAA ), route_port = DATA{};
}}

signal_name = c {{
    zero_or_more, *;
    dest = ( my_lcell2, DATAB ), route_port = DATA{};
}}
"""

NTHREADS = 10

def fuzz_local_at(x, y, n):
    for inp, fromn in [('A', 3), ('A', 4), ('A', 5), ('A', 6), ('A', 8),
                       ('B', 0), ('B', 1), ('B', 2), ('B', 7), ('B', 9),
                       ('C', 0), ('C', 4), ('C', 5), ('C', 6), ('C', 7),
                       ('D', 1), ('D', 2), ('D', 3), ('D', 8), ('D', 9),]:
        if n == fromn:
            continue

        this_lut_dir = 'localfeedbackfuzz/X{}_Y{}_N{}_DATA{}_from_N{}'.format(x, y, n, inp, fromn)
        os.mkdir(BASE_DIR + '/' + this_lut_dir)

        with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.qpf', 'w') as f:
            f.write(QPF_TMPL)

        with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.qsf', 'w') as f:
            f.write(QSF_TMPL.format(x, y, fromn, x, y, n))

        if inp == 'B':
            c_input_pin = 'A'
        else:
            c_input_pin = 'B'

        with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.rcf', 'w') as f:
            f.write(RCF_TMPL.format(inp, c_input_pin))

        with open(BASE_DIR + '/' + this_lut_dir + '/top.v', 'w') as f:
            f.write(VLOG_TMPL)

        run_one_flow(this_lut_dir, False, True)

        shutil.copy(BASE_DIR + '/' + this_lut_dir + '/output_files/maxvtest.pof', 'localfeedbackfuzz_X{}_Y{}_N{}_DATA{}_from_N{}.pof'.format(x, y, n, inp, fromn))
        shutil.copy(BASE_DIR + '/' + this_lut_dir + '/maxvtest.rcf', 'localfeedbackfuzz_X{}_Y{}_N{}_DATA{}_from_N{}.rcf'.format(x, y, n, inp, fromn))

def main():
    os.mkdir(BASE_DIR + '/localfeedbackfuzz')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    X = 5
    for y in [1, 2, 3, 4]:
        for n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            workqueue.put((X, y, n))
            num_items += 1

    def threadfn():
        while True:
            try:
                x, y, n = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on X{}_Y{}_N{}".format(x, y, n))
            fuzz_local_at(x, y, n)
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
