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


def run_minimization(time_limit, memory_limit):
    if not os.path.exists("./output_dir/min_hangs"):
        os.mkdir("./output_dir/min_hangs")

    for file in tqdm(os.listdir(f"./output_dir/fuzzer01/hangs/")):
        if "id" in file:
            tmin_command = [
                "afl-tmin",
                "-i",
                f"./output_dir/fuzzer01/hangs/{file}",
                "-o",
                f"./output_dir/min_hangs/{file}",
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

        os.chdir(dir)

        compile_command = ["afl-clang-fast++", "-o", "./temp", f"./{target}"]

        print("Starting compilation...")
        compile_process = run_command(compile_command)
        if compile_process:
            compile_process.wait()
        else:
            raise Exception("Compilation failed!")

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

        if not os.path.exists("./profraw_hangs"):
            os.mkdir("./profraw_hangs")

        for testcase in os.listdir("./output_dir/min_hangs"):
            if "id" in testcase:
                run_command(
                    [
                        "bash",
                        "-c",
                        f"LLVM_PROFILE_FILE='./profraw_hangs/default_%p.profraw' ./temp < ./output_dir/min_hangs/{testcase} > /dev/null 2>&1",
                    ]
                ).wait()

        import glob

        profraw_files = glob.glob("./profraw_hangs/default_*.profraw")

        print("Running llvm-profdata merge...")
        profdata_merge_command = (
            ["llvm-profdata", "merge", "-sparse"]
            + profraw_files
            + ["-o", "./profraw_hangs/temp.profdata"]
        )

        profdata_merge_process = run_command(profdata_merge_command)
        if profdata_merge_process:
            profdata_merge_process.wait()

        print("Running llvm-cov to show coverage...")
        llvm_cov_command = [
            "llvm-cov",
            "show",
            "./temp",
            "-instr-profile=./profraw_hangs/temp.profdata",
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
    args = parser.parse_args()

    main(args)
