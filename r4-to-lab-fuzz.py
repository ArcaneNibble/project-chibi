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
set_location_assignment PIN_27 -to b
set_location_assignment PIN_53 -to o
set_global_assignment -name ROUTING_BACK_ANNOTATION_FILE maxvtest.rcf
set_location_assignment LC_X5_Y{}_N0 -to my_lcell
set_global_assignment -name NUM_PARALLEL_PROCESSORS 1
"""

B_PATH_USING_LINE_0_Y1 = """signal_name = b {   #IOC_X5_Y0_N0
    IO_DATAIN:X5Y0S0I0;
    C4:X5Y1S0I6;
    LOCAL_INTERCONNECT:X5Y1S0I0;
    dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y1_N0
}"""

B_PATH_USING_LINE_1_Y1 = """signal_name = b {   #IOC_X5_Y0_N0
    IO_DATAIN:X5Y0S0I0;
    C4:X5Y1S0I11;
    LOCAL_INTERCONNECT:X5Y1S0I1;
    dest = ( my_lcell, DATAB ), route_port = DATAA; #LC_X5_Y1_N0
}"""

B_PATH_USING_LINE_0_Y2 = """signal_name = b {   #IOC_X5_Y0_N0
    IO_DATAIN:X5Y0S0I0;
    C4:X5Y1S0I6;
    C4:X5Y2S0I1;
    LOCAL_INTERCONNECT:X5Y2S0I0;
    dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y2_N0
}"""

B_PATH_USING_LINE_1_Y2 = """signal_name = b {   #IOC_X5_Y0_N0
    IO_DATAIN:X5Y0S0I0;
    C4:X5Y1S0I6;
    C4:X5Y2S0I1;
    LOCAL_INTERCONNECT:X5Y2S0I1;
    dest = ( my_lcell, DATAB ), route_port = DATAA; #LC_X5_Y2_N0
}"""

B_PATH_USING_LINE_0_Y3 = """signal_name = b {   #IOC_X5_Y0_N0
    IO_DATAIN:X5Y0S0I0;
    C4:X5Y1S0I3;
    LOCAL_INTERCONNECT:X5Y3S0I0;
    dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y3_N0
}"""

B_PATH_USING_LINE_1_Y3 = """signal_name = b {   #IOC_X5_Y0_N0
    IO_DATAIN:X5Y0S0I0;
    C4:X5Y1S0I11;
    C4:X5Y3S0I2;
    LOCAL_INTERCONNECT:X5Y3S0I1;
    dest = ( my_lcell, DATAB ), route_port = DATAD; #LC_X5_Y3_N0
}"""

B_PATH_USING_LINE_0_Y4 = """signal_name = b {   #IOC_X5_Y0_N0
    IO_DATAIN:X5Y0S0I0;
    C4:X5Y1S0I3;
    C4:X5Y2S0I0;
    LOCAL_INTERCONNECT:X5Y4S0I0;
    dest = ( my_lcell, DATAB ), route_port = DATAC; #LC_X5_Y4_N0
}"""

B_PATH_USING_LINE_1_Y4 = """signal_name = b {   #IOC_X5_Y0_N0
    IO_DATAIN:X5Y0S0I0;
    C4:X5Y1S0I11;
    C4:X5Y4S0I2;
    LOCAL_INTERCONNECT:X5Y4S0I1;
    dest = ( my_lcell, DATAB ), route_port = DATAD; #LC_X5_Y4_N0
}"""

OUT_PATH_Y1 = """signal_name = my_lcell {    #LC_X5_Y1_N0
    LE_BUFFER:X5Y1S0I0;
    C4:X4Y2S0I0;
    LOCAL_INTERCONNECT:X5Y5S0I9;
    IO_DATAOUT:X5Y5S2I0;
    dest = ( o, DATAIN );   #IOC_X5_Y5_N2
}"""

OUT_PATH_Y2 = """signal_name = my_lcell {    #LC_X5_Y2_N0
    LE_BUFFER:X5Y2S0I0;
    C4:X4Y3S0I0;
    LOCAL_INTERCONNECT:X5Y5S0I6;
    IO_DATAOUT:X5Y5S2I0;
    dest = ( o, DATAIN );   #IOC_X5_Y5_N2
}"""

OUT_PATH_Y3 = """signal_name = my_lcell {    #LC_X5_Y3_N0
    LE_BUFFER:X5Y3S0I0;
    C4:X4Y4S0I0;
    LOCAL_INTERCONNECT:X5Y5S0I7;
    IO_DATAOUT:X5Y5S2I0;
    dest = ( o, DATAIN );   #IOC_X5_Y5_N2
}"""

OUT_PATH_Y4 = """signal_name = my_lcell {    #LC_X5_Y4_N0
    LE_BUFFER:X5Y4S0I0;
    C4:X4Y5S0I0;
    LOCAL_INTERCONNECT:X5Y5S0I5;
    IO_DATAOUT:X5Y5S2I0;
    dest = ( o, DATAIN );   #IOC_X5_Y5_N2
}"""

RCF_TMPL = """section global_data {{
    rcf_written_by = "Quartus Prime 18.0 Build 614";
    device = 5M40ZE64A5;
}}

signal_name = a {{
    zero_or_more, *;
    R4:X{}Y{}S0I{};
    LOCAL_INTERCONNECT:X5Y{}S0I{};
    dest = ( my_lcell, DATAA );
}}

{}

{}
"""

NTHREADS = 40

def fuzz_r4_at(workdir, threadi, chanx, chany, chani, tiley):
    for lablinei in [0]:#range(26):
        with open(workdir + '/maxvtest.qsf', 'w') as f:
            f.write(QSF_TMPL.format(tiley))

        if tiley == 1:
            if lablinei == 0:
                bpath = B_PATH_USING_LINE_1_Y1
            else:
                bpath = B_PATH_USING_LINE_0_Y1
        elif tiley == 2:
            if lablinei == 0:
                bpath = B_PATH_USING_LINE_1_Y2
            else:
                bpath = B_PATH_USING_LINE_0_Y2
        elif tiley == 3:
            if lablinei == 0:
                bpath = B_PATH_USING_LINE_1_Y3
            else:
                bpath = B_PATH_USING_LINE_0_Y3
        elif tiley == 4:
            if lablinei == 0:
                bpath = B_PATH_USING_LINE_1_Y4
            else:
                bpath = B_PATH_USING_LINE_0_Y4
        else:
            asdfasdfasdf

        if tiley == 1:
            outpath = OUT_PATH_Y1
        elif tiley == 2:
            outpath = OUT_PATH_Y2
        elif tiley == 3:
            outpath = OUT_PATH_Y3
        elif tiley == 4:
            outpath = OUT_PATH_Y4
        else:
            asdfasdfasdf

        rcfrcf = RCF_TMPL.format(
            chanx, chany, chani,
            tiley, lablinei,
            bpath, outpath)

        # print(rcfrcf)

        with open(workdir + '/maxvtest.rcf', 'w') as f:
            f.write(rcfrcf)

        run_one_flow("r4-to-lab-fuzz/thread{}".format(threadi), False, True, False)

        with open(workdir + '/maxvtest.rcf', 'r') as f:
            rcflinesnew = f.readlines()
        dataa_line_idx = None
        for iii in range(len(rcflinesnew)):
            l = rcflinesnew[iii].strip()
            if l.startswith("dest = ( my_lcell, DATAA )"):
                dataa_line_idx = iii
                break
        liline = rcflinesnew[dataa_line_idx - 1].strip()
        r4line = rcflinesnew[dataa_line_idx - 2].strip()

        if not liline.startswith("LOCAL_INTERCONNECT:") or not r4line.startswith("R4:"):
            print("Something weird happened in R4:X{}Y{}I{} -> LOCAL_INTERCONNECT:X5Y{}I{}".format(chanx, chany, chani, tiley, lablinei))
            shutil.copy(workdir + '/output_files/maxvtest.pof', 'XXX-r4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.pof'.format(chanx, chany, chani, tiley, lablinei))
            shutil.copy(workdir + '/maxvtest.rcf', 'XXX-r4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.rcf'.format(chanx, chany, chani, tiley, lablinei))
        else:
            liline = liline[19:-1]
            r4line = r4line[3:-1]

            print(liline, r4line)

            actual_labline = int(liline[liline.find("I") + 1:])

            expected_r4line = "X{}Y{}S0I{}".format(chanx, chany, chani)

            if actual_labline == lablinei:
                if expected_c4line == c4line:
                    print("Got R4:X{}Y{}I{} -> LOCAL_INTERCONNECT:X5Y{}I{}".format(chanx, chany, chani, tiley, lablinei))
                    shutil.copy(workdir + '/output_files/maxvtest.pof', 'r4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.pof'.format(chanx, chany, chani, tiley, lablinei))
                    shutil.copy(workdir + '/maxvtest.rcf', 'r4-to-lab-fuzz_X{}Y{}I{}_to_X5Y{}_LAB{}.rcf'.format(chanx, chany, chani, tiley, lablinei))

def main():
    os.mkdir(BASE_DIR + '/r4-to-lab-fuzz')

    workqueue = queue.Queue()
    donequeue = queue.Queue()

    num_items = 0

    for tiley in [1, 2, 3, 4]:
        for chany in [tiley - 1, tiley]:
            for chanx in [0]:#, 1, 2, 3, 4, 5, 6, 7, 8]:
                for chani in [0]:#range(64):
                    workqueue.put((tiley, chanx, chany, chani))
                    num_items += 1

    def threadfn(threadi):
        MYDIR = BASE_DIR + '/r4-to-lab-fuzz/thread{}'.format(threadi)
        shutil.copytree(BASE_DIR + '/r4-to-lab-seed', MYDIR)

        while True:
            try:
                tiley, chanx, chany, chani = workqueue.get(timeout=0)
            except queue.Empty:
                return

            print("Working on R4:X{}Y{}I{} -> LAB X5Y{}".format(chanx, chany, chani, tiley))
            fuzz_r4_at(MYDIR, threadi, chanx, chany, chani, tiley)
            donequeue.put((chanx, chany, chani, tiley))

    for threadi in range(NTHREADS):
        t = threading.Thread(target=threadfn, args=(threadi,))
        t.start()

    while num_items:
        chanx, chany, chani, tiley = donequeue.get()
        print("Finished R4:X{}Y{}I{} -> LAB X5Y{}".format(chanx, chany, chani, tiley))
        num_items -= 1

if __name__=='__main__':
    main()
