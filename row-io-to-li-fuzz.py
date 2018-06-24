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

set_location_assignment IOC_X{}_Y{}_N{} -to a
set_location_assignment PIN_{} -to b
set_location_assignment PIN_{} -to o

set_location_assignment LC_X{}_Y{}_N0 -to my_lcell

set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
"""

RCF_TMPL = """signal_name = a {{
    IO_DATAIN:*;
    LOCAL_INTERCONNECT:X{}Y{}S0I{};
    dest = ( my_lcell, DATAA );
}}
"""

NTHREADS = 20

def fuzz_lut_at(workdir, threadi, srcx, srcy, srcn, dsti):
    if srcx == 1:
        pinb = 98
        pino = 99
        dstx = 2
    else:
        pinb = 75
        pino = 76
        dstx = 7

    with open(workdir + '/maxvtest.qsf', 'w') as f:
        f.write(QSF_TMPL.format(srcx, srcy, srcn, pinb, pino, dstx, srcy))

    with open(workdir + '/maxvtest.rcf', 'w') as f:
        f.write(RCF_TMPL.format(dstx, srcy, dsti))

    while True:
        try:
            run_one_flow("row-io-to-li/thread{}".format(threadi), False, True, False)
            break
        except Exception:
            pass

    shutil.copy(workdir + '/output_files/maxvtest.pof', 'row-io-to-li/neighfuzz_X{}_Y{}_N{}_to_LAB{}.pof'.format(srcx, srcy, srcn, dsti))
    shutil.copy(workdir + '/maxvtest.rcf', 'row-io-to-li/neighfuzz_X{}_Y{}_N{}_to_LAB{}.rcf'.format(srcx, srcy, srcn, dsti))

def main():
    os.mkdir(BASE_DIR + '/row-io-to-li')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    for srcx in [1, 8]:
        for srcy in [1, 2, 3, 4]:
            if srcx == 1 or srcy == 2:
                N = 4
            else:
                N = 5

            if srcx == 1:
                all_dsti = [5, 6, 7, 8, 9, 10, 11, 12, 18, 19, 20, 21, 22, 23, 24, 25]
            else:
                all_dsti = [0, 1, 2, 3, 4, 13, 14, 15, 16, 17]

            for srcn in range(N):
                for dsti in all_dsti:
                    workqueue.put((srcx, srcy, srcn, dsti))
                    num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/row-io-to-li/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/row-io-neigh-seed', MYDIR)

        while True:
            try:
                srcx, srcy, srcn, dsti = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on X{}_Y{}_N{} -> LAB{}".format(srcx, srcy, srcn, dsti))
            fuzz_lut_at(MYDIR, threadi, srcx, srcy, srcn, dsti)
            donequeue.put((srcx, srcy, srcn, dsti))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        srcx, srcy, srcn, dsti = donequeue.get()
        print("Finished X{}_Y{}_N{} -> LAB{}".format(srcx, srcy, srcn, dsti))
        num_items -= 1

if __name__=='__main__':
    main()
