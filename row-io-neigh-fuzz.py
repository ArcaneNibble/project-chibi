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

set_location_assignment PIN_2 -to a
set_location_assignment PIN_3 -to b
set_location_assignment IOC_X{}_Y{}_N2 -to o

set_location_assignment LC_X{}_Y{}_N{} -to my_lcell

set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
"""

RCF_TMPL = """signal_name = my_lcell {
    LE_BUFFER:*;
    LOCAL_INTERCONNECT:*;
    IO_DATAOUT:*;
    dest = ( o, DATAIN );
}
"""

NTHREADS = 20

def fuzz_lut_at(workdir, threadi, srcx, srcy, srcn):
    if srcx == 2:
        dstx = 1
    else:
        dstx = 8

    with open(workdir + '/maxvtest.qsf', 'w') as f:
        f.write(QSF_TMPL.format(dstx, srcy, srcx, srcy, srcn))

    with open(workdir + '/maxvtest.rcf', 'w') as f:
        f.write(RCF_TMPL)

    while True:
        try:
            run_one_flow("row-io-neigh/thread{}".format(threadi), False, True, False)
            break
        except Exception:
            pass

    shutil.copy(workdir + '/output_files/maxvtest.pof', 'row-io-neigh/neighfuzz_X{}_Y{}_N{}.pof'.format(srcx, srcy, srcn))
    shutil.copy(workdir + '/maxvtest.rcf', 'row-io-neigh/neighfuzz_X{}_Y{}_N{}.rcf'.format(srcx, srcy, srcn))

def main():
    os.mkdir(BASE_DIR + '/row-io-neigh')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    for srcx in [2, 7]:
        for srcy in [1, 2, 3, 4]:
            for srcn in range(10):
                workqueue.put((srcx, srcy, srcn))
                num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/row-io-neigh/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/row-io-neigh-seed', MYDIR)

        while True:
            try:
                srcx, srcy, srcn = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on X{}_Y{}_N{}".format(srcx, srcy, srcn))
            fuzz_lut_at(MYDIR, threadi, srcx, srcy, srcn)
            donequeue.put((srcx, srcy, srcn))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        srcx, srcy, srcn = donequeue.get()
        print("Finished X{}_Y{}_N{}".format(srcx, srcy, srcn))
        num_items -= 1

if __name__=='__main__':
    main()
