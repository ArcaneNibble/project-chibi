from runner import *
import os
import shutil
import queue
import threading

BASE_DIR = '/home/rqou/.local/share/lxc/altera-quartus-prime-lite-18/rootfs/home/rqou'

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
set_location_assignment PIN_9 -to b
set_location_assignment PIN_40 -to o
set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
set_location_assignment LC_X5_Y2_N0 -to my_lcell
set_global_assignment -name NUM_PARALLEL_PROCESSORS 1
"""

B_PATH_USING_LINE_0 = """signal_name = b {   #IOC_X1_Y2_N0
    IO_DATAIN:X1Y2S0I0;
    R4:X1Y2S0I11;
    R4:X5Y2S0I0;
    LOCAL_INTERCONNECT:X5Y2S0I0;
    dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y2_N0
}
"""

B_PATH_USING_LINE_1 = """signal_name = b {   #IOC_X1_Y2_N0
    IO_DATAIN:X1Y2S0I0;
    R4:X2Y2S0I1;
    LOCAL_INTERCONNECT:X5Y2S0I1;
    dest = ( my_lcell, DATAB ), route_port = DATAA; #LC_X5_Y2_N0
}
"""

RCF_TMPL = """section global_data {{
    rcf_written_by = "Quartus Prime 18.0 Build 614";
    device = 5M40ZE64A5;
}}

signal_name = a {{
    zero_or_more, *;
    C4:X{}Y{}S0I{};
    LOCAL_INTERCONNECT:X5Y2S0I{};
    dest = ( intermed, DATAA );
}}

{}

signal_name = my_lcell {{
    LE_BUFFER:X5Y2S0I0;
    R4:X5Y2S0I1;
    LOCAL_INTERCONNECT:X8Y2S0I3;
    IO_DATAOUT:X8Y2S0I0;
    dest = ( o, DATAIN );   #IOC_X8_Y2_N0
}}
"""

NTHREADS = 10

def fuzz_c4_at(workdir, threadi, x, y, i):
    for lablinei in [24]:#range(26):
        with open(workdir + '/maxvtest.qsf', 'w') as f:
            f.write(QSF_TMPL)

        rcfrcf = RCF_TMPL.format(
            x, y, i,
            lablinei,
            B_PATH_USING_LINE_1 if lablinei == 0 else B_PATH_USING_LINE_0)

        # print(rcfrcf)

        with open(workdir + '/maxvtest.rcf', 'w') as f:
            f.write(rcfrcf)

        run_one_flow("c4-to-lab-fuzz/thread{}".format(threadi), False, True, False)

        with open(workdir + '/maxvtest.rcf', 'r') as f:
            rcflinesnew = f.readlines()
        dataa_line_idx = None
        for iii in range(len(rcflinesnew)):
            l = rcflinesnew[iii].strip()
            if l.startswith("dest = ( my_lcell, DATAA )"):
                dataa_line_idx = iii
                break
        liline = rcflinesnew[dataa_line_idx - 1].strip()
        c4line = rcflinesnew[dataa_line_idx - 2].strip()

        if not liline.startswith("LOCAL_INTERCONNECT:") or not c4line.startswith("C4:"):
            print("Something weird happened in C4:X{}Y{}I{} -> LOCAL_INTERCONNECT:X5Y2I{}".format(x, y, i, lablinei))
            shutil.copy(workdir + '/output_files/maxvtest.pof', 'XXX-c4-to-lab-fuzz_X{}Y{}I{}_to_LAB{}.pof'.format(x, y, i, lablinei))
            shutil.copy(workdir + '/maxvtest.rcf', 'XXX-c4-to-lab-fuzz_X{}Y{}I{}_to_LAB{}.rcf'.format(x, y, i, lablinei))
        else:
            liline = liline[19:-1]
            c4line = c4line[3:-1]

            actual_labline = int(liline[liline.find("I") + 1:])
            print(actual_labline)

            expected_c4line = "X{}Y{}S0I{}".format(x, y, i)

            if actual_labline == lablinei:
                print("YAYYAY", c4line)
                if expected_c4line == c4line:
                    print("YAYAYAY2")

                    shutil.copy(workdir + '/output_files/maxvtest.pof', 'c4-to-lab-fuzz_X{}Y{}I{}_to_LAB{}.pof'.format(x, y, i, lablinei))
                    shutil.copy(workdir + '/maxvtest.rcf', 'c4-to-lab-fuzz_X{}Y{}I{}_to_LAB{}.rcf'.format(x, y, i, lablinei))

def main():
    os.mkdir(BASE_DIR + '/c4-to-lab-fuzz')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    for x in [4]:#, 5]:
        for y in [1]:#, 1, 2, 3, 4, 5]:
            for i in [26]:#range(1):
                workqueue.put((x, y, i))
                num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/c4-to-lab-fuzz/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/c4-to-lab-seed', MYDIR)

        while True:
            try:
                x, y, i = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on X{}Y{}I{}".format(x, y, i))
            fuzz_c4_at(MYDIR, threadi, x, y, i)
            donequeue.put((x, y, i))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        x, y, i = donequeue.get()
        print("Finished X{}Y{}I{}".format(x, y, i))
        num_items -= 1

if __name__=='__main__':
    main()
