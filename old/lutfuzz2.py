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
set_location_assignment PIN_22 -to o
set_location_assignment LC_X{}_Y{}_N{} -to my_lcell
set_global_assignment -name NUM_PARALLEL_PROCESSORS 1
"""

NTHREADS = 20

def fuzz_lut_at(workdir, threadi, x, y, n):
    with open(workdir + '/maxvtest.qpf', 'w') as f:
        f.write(QPF_TMPL)

    with open(workdir + '/maxvtest.qsf', 'w') as f:
        f.write(QSF_TMPL.format(x, y, n))

    while True:
        try:
            run_one_flow("lutfuzz2/thread{}".format(threadi), False, True, False)
            break
        except Exception:
            pass

    shutil.copy(workdir + '/output_files/maxvtest.pof', 'lutfuzz2/lutfuzz_X{}_Y{}_N{}.pof'.format(x, y, n))
    shutil.copy(workdir + '/maxvtest.rcf', 'lutfuzz2/lutfuzz_X{}_Y{}_N{}.rcf'.format(x, y, n))

def main():
    os.mkdir(BASE_DIR + '/lutfuzz2')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    for x in [2, 3, 4, 5, 6, 7]:
        for y in [1, 2, 3, 4]:
            for n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                workqueue.put((x, y, n))
                num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/lutfuzz2/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/lutfuzz2-seed', MYDIR)

        while True:
            try:
                x, y, n = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on X{}_Y{}_N{}".format(x, y, n))
            fuzz_lut_at(MYDIR, threadi, x, y, n)
            donequeue.put((x, y, n))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        x, y, n = donequeue.get()
        print("Finished X{}_Y{}_N{}".format(x, y, n))
        num_items -= 1

if __name__=='__main__':
    main()
