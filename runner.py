import subprocess

def run_one_flow(container_dir, output=True, back_annotate=False):
    if output:
        streams = None
    else:
        streams = subprocess.DEVNULL

    ret = subprocess.run(["ssh", "altera-quartus-prime-lite-18.lxc", "--",
        "cd {}; quartus_map --read_settings_file=on --write_settings_file=off maxvtest -c maxvtest".format(container_dir)],
        stdout=streams, stderr=streams)
    if ret.returncode != 0:
        raise Exception("quartus_map failed")

    ret = subprocess.run(["ssh", "altera-quartus-prime-lite-18.lxc", "--",
        "cd {}; quartus_fit --read_settings_file=off --write_settings_file=off maxvtest -c maxvtest".format(container_dir)],
        stdout=streams, stderr=streams)
    if ret.returncode != 0:
        raise Exception("quartus_fit failed")

    ret = subprocess.run(["ssh", "altera-quartus-prime-lite-18.lxc", "--",
        "cd {}; quartus_asm --read_settings_file=off --write_settings_file=off maxvtest -c maxvtest".format(container_dir)],
        stdout=streams, stderr=streams)
    if ret.returncode != 0:
        raise Exception("quartus_asm failed")

    if back_annotate:
        ret = subprocess.run(["ssh", "altera-quartus-prime-lite-18.lxc", "--",
            "cd {}; quartus_cdb maxvtest -c maxvtest --back_annotate=routing".format(container_dir)],
            stdout=streams, stderr=streams)
        if ret.returncode != 0:
            raise Exception("back annotate failed")

# run_one_flow('maxvtest2', False)
