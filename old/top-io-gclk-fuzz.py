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

set_location_assignment PIN_{} -to a
set_location_assignment IOC_X{}_Y{}_N0 -to o

set_instance_assignment -name GLOBAL_SIGNAL "GLOBAL CLOCK" -to a

set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
"""

RCF_TMPL = """signal_name = a {{
    zero_or_more, *;
    LOCAL_INTERCONNECT:X{}Y{}S0I{};
    IO_DATAOUT:*;
    dest = ( o, DATAIN );
}}
"""

NTHREADS = 20

def fuzz_lut_at(workdir, threadi, srcclk, dstx, dsty, dsti):
    if srcclk == 0:
        srcpin = 12
    elif srcclk == 1:
        srcpin = 14
    elif srcclk == 2:
        srcpin = 62
    else:
        srcpin = 64

    with open(workdir + '/maxvtest.qsf', 'w') as f:
        f.write(QSF_TMPL.format(srcpin, dstx, dsty))

    with open(workdir + '/maxvtest.rcf', 'w') as f:
        f.write(RCF_TMPL.format(dstx, dsty, dsti))

    while True:
        try:
            run_one_flow("top-io-gclk-fuzz/thread{}".format(threadi), False, True, False)
            break
        except Exception:
            pass

    shutil.copy(workdir + '/output_files/maxvtest.pof', 'top-io-gclk-fuzz/gclk{}_to_X{}Y{}I{}.pof'.format(srcclk, dstx, dsty, dsti))
    shutil.copy(workdir + '/maxvtest.rcf', 'top-io-gclk-fuzz/gclk{}_to_X{}Y{}I{}.rcf'.format(srcclk, dstx, dsty, dsti))

def main():
    os.mkdir(BASE_DIR + '/top-io-gclk-fuzz')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    # for srcx in [1, 8]:
    #     for srcy in [1, 2, 3, 4]:
    #         if srcx == 1 or srcy == 2:
    #             N = 4
    #         else:
    #             N = 5

    #         if srcx == 1:
    #             all_dsti = [5, 6, 7, 8, 9, 10, 11, 12, 18, 19, 20, 21, 22, 23, 24, 25]
    #         else:
    #             all_dsti = [0, 1, 2, 3, 4, 13, 14, 15, 16, 17]

    #         for srcn in range(N):
    #             for dsti in all_dsti:
    #                 workqueue.put((srcclk, dstx, dsty, dsti))
    #                 num_items += 1
    for dstx in [2, 3, 4, 5, 6, 7]:
        for dsty in [0, 5]:
            for dsti in [3, 4, 8, 9]:
                for srcclk in [0, 1, 2, 3]:
                    workqueue.put((srcclk, dstx, dsty, dsti))
                    num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/top-io-gclk-fuzz/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/top-io-gclk-fuzz-seed', MYDIR)

        while True:
            try:
                srcclk, dstx, dsty, dsti = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on GCLK{} -> X{}Y{}I{}".format(srcclk, dstx, dsty, dsti))
            fuzz_lut_at(MYDIR, threadi, srcclk, dstx, dsty, dsti)
            donequeue.put((srcclk, dstx, dsty, dsti))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        srcclk, dstx, dsty, dsti = donequeue.get()
        print("Finished GCLK{} -> X{}Y{}I{}".format(srcclk, dstx, dsty, dsti))
        num_items -= 1

if __name__=='__main__':
    main()
