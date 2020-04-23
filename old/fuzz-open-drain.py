from runner import *
import os
import shutil
import queue
import threading
import json

BASE_DIR = '/home/rqou/.local/share/lxc/altera-quartus-prime-lite-18/rootfs/home/rqou'

QSF_TMP = """set_global_assignment -name FAMILY "MAX V"
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
set_location_assignment IOC_X{}_Y{}_N{} -to o
"""

NTHREADS = 20

def fuzz_io_at(workdir, threadi, X, Y, N):
    if X == 1 and Y == 4 and N == 0:
        srcX = 1
        srcY = 4
        srcN = 1
    else:
        srcX = 1
        srcY = 4
        srcN = 0

    with open(workdir + '/maxvtest.qsf', 'w') as f:
        f.write(QSF_TMP.format(srcX, srcY, srcN, X, Y, N))

    while True:
        try:
            run_one_flow("fuzz-od/thread{}".format(threadi), False, True, False)
            break
        except Exception:
            pass

    shutil.copy(workdir + '/output_files/maxvtest.pof', 'fuzz-od/IOC_X{}_Y{}_N{}.pof'.format(X, Y, N))
    shutil.copy(workdir + '/maxvtest.rcf', 'fuzz-od/IOC_X{}_Y{}_N{}.rcf'.format(X, Y, N))


def main():
    os.mkdir(BASE_DIR + '/fuzz-od')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0

    for X in [1, 8]:
        for Y in [1, 2, 3, 4]:
            for N in range(4 if X == 1 or Y == 2 else 5):
                workqueue.put((X, Y, N))
                num_items += 1

    for X in [2, 3, 4, 5, 6, 7]:
        for Y in [0, 5]:
            for N in range(3 if X == 4 or (X == 2 and Y == 5) or (X == 7 and Y == 0) else 4):
                workqueue.put((X, Y, N))
                num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/fuzz-od/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/fuzz-od-seed', MYDIR)

        while True:
            try:
                X, Y, N = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on IOC_X{}_Y{}_N{}".format(X, Y, N))
            fuzz_io_at(MYDIR, threadi, X, Y, N)
            donequeue.put((X, Y, N))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        X, Y, N = donequeue.get()
        print("Finished IOC_X{}_Y{}_N{}".format(X, Y, N))
        num_items -= 1

if __name__=='__main__':
    main()
