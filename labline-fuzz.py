from runner import *
import os
import shutil
import queue
import threading

BASE_DIR = '/home/rqou/.local/share/lxc/altera-quartus-prime-lite-18/rootfs/home/rqou'

VLOG_TMPL = """module maxvtest(input a, input b, output o);

wire intermed;

maxv_lcell my_lcell (
    .dataa(a),
    .datab(b),
    .combout(o));
defparam my_lcell.operation_mode = "normal";
defparam my_lcell.synch_mode = "off";
defparam my_lcell.register_cascade_mode = "off";
defparam my_lcell.sum_lutc_input = "datac";
defparam my_lcell.lut_mask = "8888";
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
set_location_assignment PIN_22 -to o
set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
set_location_assignment LC_X{}_Y{}_N{} -to my_lcell
set_global_assignment -name NUM_PARALLEL_PROCESSORS 1
"""

RCF_TMPL = """section global_data {{
    rcf_written_by = "Quartus Prime 18.0 Build 614";
    device = 5M40ZE64A5;
}}

signal_name = a {{
    zero_or_more, *;
    LOCAL_INTERCONNECT:X{}Y{}S0I{};
    dest = ( my_lcell, DATAA ), route_port = DATA{};
}}

signal_name = b {{
    zero_or_more, *;
    dest = ( my_lcell, DATAB ), route_port = DATA{};
}}
"""

NTHREADS = 10

def fuzz_local_at(x, y, inp, track):
    this_lut_dir = 'labtrackfuzz/X{}_Y{}_DATA{}_from_labline{}'.format(x, y, inp, track)
    os.mkdir(BASE_DIR + '/' + this_lut_dir)

    with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.qpf', 'w') as f:
        f.write(QPF_TMPL)

    with open(BASE_DIR + '/' + this_lut_dir + '/top.v', 'w') as f:
        f.write(VLOG_TMPL)

        if inp == 'B':
            b_input_pin = 'A'
        else:
            b_input_pin = 'B'

    with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.rcf', 'w') as f:
        f.write(RCF_TMPL.format(x, y, track, inp, b_input_pin))

    for n in range(2):
        with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.rcf', 'r') as f:
            rcflines = f.readlines()
        with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.rcf', 'w') as f:
            is_in_my_lcell = False
            for line in rcflines:
                if not is_in_my_lcell:
                    if line.startswith("signal_name = my_lcell"):
                        is_in_my_lcell = True
                    else:
                        f.write(line)
                else:
                    if line.strip() == "}":
                        is_in_my_lcell = False
        # with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.rcf', 'r') as f:
        #     print(f.read())

        with open(BASE_DIR + '/' + this_lut_dir + '/maxvtest.qsf', 'w') as f:
            f.write(QSF_TMPL.format(x, y, n))

        run_one_flow(this_lut_dir, True, True, n == 0)

        shutil.copy(BASE_DIR + '/' + this_lut_dir + '/output_files/maxvtest.pof', 'labtrackfuzz_X{}_Y{}_N{}_DATA{}_from_labline{}.pof'.format(x, y, n, inp, track))
        shutil.copy(BASE_DIR + '/' + this_lut_dir + '/maxvtest.rcf', 'labtrackfuzz_X{}_Y{}_N{}_DATA{}_from_labline{}.rcf'.format(x, y, n, inp, track))
        shutil.copy(BASE_DIR + '/' + this_lut_dir + '/maxvtest.qsf', 'labtrackfuzz_X{}_Y{}_N{}_DATA{}_from_labline{}.qsf'.format(x, y, n, inp, track))

def main():
    os.mkdir(BASE_DIR + '/labtrackfuzz')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    X = 5
    for y in [1]:#, 2, 3, 4]:
        for inp in ['A']:#, 'B', 'C', 'D']:
            if inp == 'A':
                tracks = [ 0,  1,  3,  6,  8,  9, 11, 14, 15, 18, 19, 22, 25]
            elif inp == 'B':
                tracks = [ 2,  4,  5,  7, 10, 12, 13, 16, 17, 20, 21, 23, 24]
            elif inp == 'C':
                tracks = [ 0,  2,  3,  7,  8,  9, 11, 14, 17, 18, 21, 22, 25]
            elif inp == 'D':
                tracks = [ 1,  4,  5,  6, 10, 12, 13, 15, 16, 19, 20, 23, 24]

            for trackidx in range(1):
                track = tracks[trackidx]
                workqueue.put((X, y, inp, track))
                num_items += 1

    def threadfn():
        while True:
            try:
                x, y, inp, track = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on X{}_Y{} DATA{} from track {}".format(x, y, inp, track))
            fuzz_local_at(x, y, inp, track)
            donequeue.put((x, y, inp, track))

    for _ in range(NTHREADS):
        t = threading.Thread(target=threadfn)
        t.start()

    while num_items:
        x, y, inp, track = donequeue.get()
        print("Finished X{}_Y{} DATA{} from track {}".format(x, y, inp, track))
        num_items -= 1

if __name__=='__main__':
    main()
