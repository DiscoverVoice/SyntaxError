import subprocess
import time
import os
import signal
import argparse
from tqdm.auto import tqdm


def run_command(command, env=None):
    try:
        process = subprocess.Popen(command, env=env)
        return process
    except Exception as e:
        print(f"Failed to run command: {' '.join(command)}, Error: {e}")
        return None


def run_parallel_fuzzing(master_command, slave_commands, sleep_time=600):
    print("Starting master process...")
    master_process = run_command(master_command)

    slave_processes = []
    for i, slave_command in enumerate(slave_commands):
        print(
            f"Starting slave process {i + 1} with power schedule: {slave_command[-3]}"
        )
        slave_process = run_command(slave_command)
        if slave_process:
            slave_processes.append(slave_process)

    time.sleep(sleep_time)

    print("Stopping fuzzing processes...")
    master_process.send_signal(signal.SIGINT)
    master_process.wait()

    for i, slave_process in enumerate(slave_processes):
        slave_process.send_signal(signal.SIGINT)
        slave_process.wait()

    print("Fuzzing terminated successfully.")


def move_slave_data(slave_ids):
    master_dir = "./output_dir/fuzzer01"
    for slave_id in slave_ids:
        slave_dir = f"./output_dir/fuzzer0{slave_id}"

        for sub_dir in ["crashes", "hangs", "queue"]:
            source_dir = os.path.join(slave_dir, sub_dir)
            target_dir = os.path.join(master_dir, sub_dir)

            for file_name in os.listdir(source_dir):
                if "id" in file_name:
                    source_file = os.path.join(source_dir, file_name)
                    target_file = os.path.join(target_dir, file_name)

                    os.rename(source_file, target_file)


def run_minimization(time_limit, memory_limit):
    if not os.path.exists("./output_dir/min_queue"):
        os.mkdir("./output_dir/min_queue")

    cmin_command = [
        "afl-cmin",
        "-i",
        f"./output_dir/fuzzer01/queue/",
        "-o",
        f"./output_dir/min_queue",
        "-T",
        "all",
        "--",
        "./temp",
    ]
    cmin_process = run_command(cmin_command)
    if cmin_process:
        cmin_process.wait()

    for file in tqdm(os.listdir(f"./output_dir/min_queue/")):
        if "id" in file:
            tmin_command = [
                "afl-tmin",
                "-i",
                f"./output_dir/min_queue/{file}",
                "-o",
                f"./output_dir/min_queue/{file}",
                "-t",
                str(time_limit),
                "-m",
                str(memory_limit),
                "-e",
                "--",
                "./temp",
            ]
            tmin_process = run_command(tmin_command)
            if tmin_process:
                tmin_process.wait()


def main(args):
    try:
        dir = args.dir
        target = args.target
        time_limit = args.time_limit
        memory_limit = args.memory_limit
        num_slaves = args.num_slaves
        persistent_mode = args.persistent
        sleep_time = args.sleep_time

        os.chdir(dir)

        compile_command = ["afl-clang-fast++", "-o", "./temp", f"./{target}"]

        print("Starting compilation...")
        compile_process = run_command(compile_command)
        if compile_process:
            compile_process.wait()
        else:
            raise Exception("Compilation failed!")

        if persistent_mode:
            print(
                "Enabling persistent mode. Ensure your target supports persistent loops."
            )

        master_fuzz_command = [
            "afl-fuzz",
            "-M",
            "fuzzer01",
            "-i",
            "./input_dir/",
            "-o",
            "./output_dir",
            "-x",
            "./dict.txt",
            "-P",
            "explore",
            "-p",
            "fast",
            "-t",
            str(time_limit),
            "-m",
            str(memory_limit),
            "--",
            "./temp",
        ]

        power_schedules = ["fast", "coe", "quad", "explore"]

        slave_fuzz_commands = [
            [
                "afl-fuzz",
                f"-S",
                f"fuzzer0{i+2}",
                "-i",
                "./input_dir/",
                "-o",
                "./output_dir",
                "-x",
                "./dict.txt",
                "-P",
                power_schedules[i % len(power_schedules)],
                "-p",
                "fast",
                "-t",
                str(time_limit),
                "-m",
                str(memory_limit),
                "--",
                "./temp",
            ]
            for i in range(num_slaves)
        ]

        print("Starting parallel fuzzing...")
        run_parallel_fuzzing(master_fuzz_command, slave_fuzz_commands, sleep_time)

        move_slave_data(range(2, num_slaves + 2))

        print("Starting corpus minimization...")
        run_minimization(time_limit, memory_limit)

        compile_command = [
            "afl-clang-fast++",
            "-o",
            "./temp",
            f"./{target}",
            "-fprofile-instr-generate",
            "-fcoverage-mapping",
        ]
        compile_process = run_command(compile_command)
        if compile_process:
            compile_process.wait()

        if not os.path.exists("./profraw_queue"):
            os.mkdir("./profraw_queue")

        for testcase in os.listdir("./output_dir/min_queue"):
            if "id" in testcase:
                run_command(
                    [
                        "bash",
                        "-c",
                        f"LLVM_PROFILE_FILE='./profraw_queue/default_%p.profraw' ./temp < ./output_dir/min_queue/{testcase} > /dev/null 2>&1",
                    ]
                ).wait()

        import glob

        profraw_files = glob.glob("./profraw_queue/default_*.profraw")

        print("Running llvm-profdata merge...")
        profdata_merge_command = (
            ["llvm-profdata", "merge", "-sparse"]
            + profraw_files
            + ["-o", "./profraw_queue/temp.profdata"]
        )

        profdata_merge_process = run_command(profdata_merge_command)
        if profdata_merge_process:
            profdata_merge_process.wait()

        print("Running llvm-cov to show coverage...")
        llvm_cov_command = [
            "llvm-cov",
            "show",
            "./temp",
            "-instr-profile=./profraw_queue/temp.profdata",
        ]
        llvm_cov_process = run_command(llvm_cov_command)
        if llvm_cov_process:
            llvm_cov_process.wait()

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        default="./test/",
        help="Directory where run the fuzzer",
    )
    parser.add_argument(
        "-t", "--target", type=str, default="temp.cpp", help="Target file for fuzzing"
    )
    parser.add_argument(
        "-tl",
        "--time_limit",
        type=int,
        default=1000,
        help="Time limit(in milli seconds) for fuzzing",
    )
    parser.add_argument(
        "-ml",
        "--memory_limit",
        type=int,
        default=512,
        help="Memory limit(in seconds) for fuzzing",
    )
    parser.add_argument(
        "-ns",
        "--num_slaves",
        type=int,
        default=1,
        help="Number of slave processes for parallel fuzzing",
    )
    parser.add_argument(
        "-p", "--persistent", action="store_true", help="Enable persistent mode"
    )
    parser.add_argument(
        "-st",
        "--sleep_time",
        type=int,
        default=600,
        help="Time limit(in seconds) for fuzzing",
    )
    args = parser.parse_args()

    main(args)
