import subprocess
import os
import argparse
from typing import *


def compile(
    source_files, output_binary, compiler="afl-clang-lto++", sanitizers=["ASAN"]
):
    env = os.environ.copy()
    if sanitizers:
        for sanitizer in sanitizers:
            env[f"AFL_USE_{sanitizer}"] = "1"

    command = [compiler, "-o", output_binary] + source_files

    try:
        print("Compiling target with command:", " ".join(command))
        subprocess.run(command, check=True, env=env)
        print(f"Compilation successful. Output binary: {output_binary}")
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Compile target with AFL++ using afl-clang-lto++."
    )
    parser.add_argument("source_files", nargs="+", help="Source files to compile")
    parser.add_argument("-o", "--output", required=True, help="Output binary file")
    parser.add_argument(
        "--sanitizers",
        nargs="*",
        choices=["ASAN", "MSAN", "UBSAN", "CFISAN", "TSAN", "LSAN"],
        help="Sanitizers to apply (e.g., ASAN, MSAN)",
    )

    args = parser.parse_args()
    compile(args.source_files, args.output, sanitizers=args.sanitizer)


if __name__ == "__main__":
    main()
