from runner import *
import os
import shutil
import queue
import threading

BASE_DIR = '/home/rqou/.local/share/lxc/altera-quartus-prime-lite-18/rootfs/home/rqou'

QSF_TMPL = """set_global_assignment -name FAMILY "MAX V"
set_global_assignment -name DEVICE 5M240ZT100C4
set_global_assignment -name TOP_LEVEL_ENTITY maxvtest
set_global_assignment -name ORIGINAL_QUARTUS_VERSION 18.0.0
set_global_assignment -name PROJECT_CREATION_TIME_DATE "03:45:37  MAY 30, 2018"
set_global_assignment -name LAST_QUARTUS_VERSION "18.0.0 Lite Edition"
set_global_assignment -name PROJECT_OUTPUT_DIRECTORY output_files
set_global_assignment -name ERROR_CHECK_FREQUENCY_DIVISOR "-1"
set_global_assignment -name EDA_SIMULATION_TOOL "ModelSim-Altera (Verilog)"
set_global_assignment -name EDA_TIME_SCALE "1 ps" -section_id eda_simulation
set_global_assignment -name EDA_OUTPUT_DATA_FORMAT "VERILOG HDL" -section_id eda_simulation
set_global_assignment -name VERILOG_FILE top.v
set_global_assignment -name NUM_PARALLEL_PROCESSORS 1
set_global_assignment -name INCREMENTAL_COMPILATION OFF
set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf

set_location_assignment PIN_2 -to a
set_location_assignment PIN_3 -to b
set_location_assignment PIN_4 -to c
set_location_assignment PIN_5 -to o

set_location_assignment LC_X{}_Y{}_N{} -to intermed
set_location_assignment LC_X{}_Y{}_N{} -to my_lcell2
"""

RCF_TMPL = """signal_name = intermed {{
    LE_BUFFER:*;
    LOCAL_INTERCONNECT:X{}Y{}S0I{};
    dest = ( my_lcell2, DATAA );
}}
"""

NTHREADS = 20

def fuzz_lut_at(workdir, threadi, srcx, srcy, srcn, dstI):
    if srcn == 0:
        otherlutN = 1
    else:
        otherlutN = 0

    with open(workdir + '/maxvtest.qsf', 'w') as f:
        f.write(QSF_TMPL.format(srcx, srcy, srcn, srcx, srcy, otherlutN))

    with open(workdir + '/maxvtest.rcf', 'w') as f:
        f.write(RCF_TMPL.format(srcx, srcy, dstI))

    while True:
        try:
            run_one_flow("lab-self-connection/thread{}".format(threadi), False, True, False)
            break
        except Exception:
            pass

    shutil.copy(workdir + '/output_files/maxvtest.pof', 'lab-self-connection/labself_X{}_Y{}_N{}_to_LAB{}.pof'.format(srcx, srcy, srcn, dstI))
    shutil.copy(workdir + '/maxvtest.rcf', 'lab-self-connection/labself_X{}_Y{}_N{}_to_LAB{}.rcf'.format(srcx, srcy, srcn, dstI))

def main():
    os.mkdir(BASE_DIR + '/lab-self-connection')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    for srcx in [2, 3, 4, 5, 6, 7]:
        for srcy in [1, 2, 3, 4]:
            for srcn in range(10):
                for dstI in range(26):
                    workqueue.put((srcx, srcy, srcn, dstI))
                    num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/lab-self-connection/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/lab-self-connection-seed', MYDIR)

        while True:
            try:
                srcx, srcy, srcn, dstI = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on X{}_Y{}_N{} -> LAB{}".format(srcx, srcy, srcn, dstI))
            fuzz_lut_at(MYDIR, threadi, srcx, srcy, srcn, dstI)
            donequeue.put((srcx, srcy, srcn, dstI))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        srcx, srcy, srcn, dstI = donequeue.get()
        print("Finished X{}_Y{}_N{} -> LAB{}".format(srcx, srcy, srcn, dstI))
        num_items -= 1

if __name__=='__main__':
    main()
