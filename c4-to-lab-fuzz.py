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
set_location_assignment PIN_{} -to b
set_location_assignment PIN_{} -to o
set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
set_location_assignment LC_X5_Y{}_N0 -to my_lcell
set_global_assignment -name NUM_PARALLEL_PROCESSORS 1
"""

# (bpin, opin, bpath0, bpath1, outpath)
OTHER_BITS = [
    # 1
    (11, 37, """signal_name = b {   #IOC_X1_Y1_N1
        IO_DATAIN:X1Y1S1I0;
        R4:X2Y1S0I3;
        R4:X2Y1S0I9;
        R4:X1Y1S0I44;
        R4:X3Y1S0I0;
        LOCAL_INTERCONNECT:X5Y1S0I0;
        dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y1_N0
    }""", """signal_name = b {  #IOC_X1_Y1_N1
        IO_DATAIN:X1Y1S1I0;
        R4:X2Y1S0I3;
        R4:X5Y1S0I1;
        LOCAL_INTERCONNECT:X5Y1S0I1;
        dest = ( my_lcell, DATAB ), route_port = DATAA; #LC_X5_Y1_N0
    }""", """signal_name = my_lcell {    #LC_X5_Y1_N0
        LE_BUFFER:X5Y1S0I1;
        R4:X6Y1S0I1;
        LOCAL_INTERCONNECT:X8Y1S0I3;
        IO_DATAOUT:X8Y1S1I0;
        dest = ( o, DATAIN );   #IOC_X8_Y1_N1
    }"""),

    # 2
    (9, 40, """signal_name = b {   #IOC_X1_Y2_N0
        IO_DATAIN:X1Y2S0I0;
        R4:X1Y2S0I11;
        R4:X5Y2S0I0;
        LOCAL_INTERCONNECT:X5Y2S0I0;
        dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y2_N0
    }""", """signal_name = b {   #IOC_X1_Y2_N0
        IO_DATAIN:X1Y2S0I0;
        R4:X2Y2S0I1;
        LOCAL_INTERCONNECT:X5Y2S0I1;
        dest = ( my_lcell, DATAB ), route_port = DATAA; #LC_X5_Y2_N0
    }""", """signal_name = my_lcell {
        LE_BUFFER:X5Y2S0I0;
        R4:X5Y2S0I1;
        LOCAL_INTERCONNECT:X8Y2S0I3;
        IO_DATAOUT:X8Y2S0I0;
        dest = ( o, DATAIN );   #IOC_X8_Y2_N0
    }"""),

    # 3
    (3, 44, """signal_name = b {    #IOC_X1_Y3_N0
        IO_DATAIN:X1Y3S0I0;
        R4:X2Y3S0I0;
        R4:X5Y3S0I0;
        LOCAL_INTERCONNECT:X5Y3S0I0;
        dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y3_N0
    }""", """signal_name = b {  #IOC_X1_Y3_N0
        IO_DATAIN:X1Y3S0I0;
        R4:X1Y3S0I15;
        R4:X5Y3S0I1;
        LOCAL_INTERCONNECT:X5Y3S0I1;
        dest = ( my_lcell, DATAB ), route_port = DATAA; #LC_X5_Y3_N0
    }""", """signal_name = my_lcell {    #LC_X5_Y3_N0
        LE_BUFFER:X5Y3S0I0;
        C4:X4Y0S0I14;
        R4:X5Y3S0I4;
        R4:X7Y3S0I5;
        LOCAL_INTERCONNECT:X8Y3S0I13;
        IO_DATAOUT:X8Y3S0I0;
        dest = ( o, DATAIN );   #IOC_X8_Y3_N0
    }"""),

    # 4
    (64, 48, """signal_name = b {   #IOC_X1_Y4_N1
        IO_DATAIN:X1Y4S1I0;
        R4:X2Y4S0I3;
        R4:X2Y4S0I9;
        R4:X1Y4S0I44;
        R4:X3Y4S0I0;
        LOCAL_INTERCONNECT:X5Y4S0I0;
        dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y4_N0
    }""", """signal_name = b {  #IOC_X1_Y4_N1
        IO_DATAIN:X1Y4S1I0;
        R4:X2Y4S0I3;
        R4:X5Y4S0I1;
        LOCAL_INTERCONNECT:X5Y4S0I1;
        dest = ( my_lcell, DATAB ), route_port = DATAD; #LC_X5_Y4_N0
    }""", """signal_name = my_lcell {    #LC_X5_Y4_N0
        LE_BUFFER:X5Y4S0I1;
        R4:X6Y4S0I1;
        LOCAL_INTERCONNECT:X8Y4S0I3;
        IO_DATAOUT:X8Y4S1I0;
        dest = ( o, DATAIN );   #IOC_X8_Y4_N1
    }"""),
]

RCF_TMPL = """section global_data {{
    rcf_written_by = "Quartus Prime 18.0 Build 614";
    device = 5M40ZE64A5;
}}

signal_name = a {{
    zero_or_more, *;
    C4:X{}Y{}S0I{};
    LOCAL_INTERCONNECT:X5Y{}S0I{};
    dest = ( my_lcell, DATAA );
}}

{}

{}
"""

NTHREADS = 40

def fuzz_c4_at(workdir, threadi, chanx, chany, chani, tiley):
    for lablinei in range(26):

        (bpin, opin, bpath0, bpath1, outpath) = OTHER_BITS[tiley - 1]

        if lablinei == 0:
            bpath = bpath1
        else:
            bpath = bpath0

        with open(workdir + '/maxvtest.qsf', 'w') as f:
            f.write(QSF_TMPL.format(bpin, opin, tiley))

        rcfrcf = RCF_TMPL.format(
            chanx, chany, chani,
            tiley, lablinei,
            bpath, outpath)

        # print(rcfrcf)

        with open(workdir + '/maxvtest.rcf', 'w') as f:
            f.write(rcfrcf)

        while True:
            try:
                run_one_flow("c4-to-lab-fuzz/thread{}".format(threadi), False, True, False)
                break
            except Exception:
                pass

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
            print("Something weird happened in C4:X{}Y{}I{} -> LOCAL_INTERCONNECT:X5Y{}I{}".format(chanx, chany, chani, tiley, lablinei))
            shutil.copy(workdir + '/output_files/maxvtest.pof', 'XXX-c4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.pof'.format(chanx, chany, chani, tiley, lablinei))
            shutil.copy(workdir + '/maxvtest.rcf', 'XXX-c4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.rcf'.format(chanx, chany, chani, tiley, lablinei))
        else:
            liline = liline[19:-1]
            c4line = c4line[3:-1]

            actual_labline = int(liline[liline.find("I") + 1:])

            expected_c4line = "X{}Y{}S0I{}".format(chanx, chany, chani)

            if actual_labline == lablinei:
                if expected_c4line == c4line:
                    print("Got C4:X{}Y{}S0I{} -> LOCAL_INTERCONNECT:X5Y{}S0I{}".format(chanx, chany, chani, tiley, lablinei))
                    shutil.copy(workdir + '/output_files/maxvtest.pof', 'c4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.pof'.format(chanx, chany, chani, tiley, lablinei))
                    shutil.copy(workdir + '/maxvtest.rcf', 'c4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.rcf'.format(chanx, chany, chani, tiley, lablinei))

def main():
    os.mkdir(BASE_DIR + '/c4-to-lab-fuzz')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0
    for tiley in [1, 2, 3, 4]:
        for chanx in [4, 5]:
            for chany in [0, 1, 2, 3, 4, 5]:
                for chani in range(64):
                    workqueue.put((tiley, chanx, chany, chani))
                    num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/c4-to-lab-fuzz/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/c4-to-lab-seed', MYDIR)

        while True:
            try:
                tiley, chanx, chany, chani = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on C4:X{}Y{}I{} -> LAB X5Y{}".format(chanx, chany, chani, tiley))
            fuzz_c4_at(MYDIR, threadi, chanx, chany, chani, tiley)
            donequeue.put((chanx, chany, chani, tiley))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        chanx, chany, chani, tiley = donequeue.get()
        print("Finished C4:X{}Y{}I{} -> LAB X5Y{}".format(chanx, chany, chani, tiley))
        num_items -= 1

if __name__=='__main__':
    main()
