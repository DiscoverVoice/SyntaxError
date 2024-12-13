import re
import subprocess
import os


def compile_and_run(cpp_code, cpp_file_path, input_data, output_file_path, compile_cmd):
    result = {"Compilation Error": "", "Observed Output": "", "Runtime Errors": []}

    with open(cpp_file_path, "w") as cpp_file:
        cpp_file.write(cpp_code)

    compile_process = subprocess.run(
        compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if compile_process.returncode != 0:
        result["Compilation Error"] = compile_process.stderr.strip()
        os.remove(cpp_file_path)
        return result

    os.environ["ASAN_OPTIONS"] = "halt_on_error=0"
    os.environ["MSAN_OPTIONS"] = "halt_on_error=0"

    run_cmd = [output_file_path]

    run_process = subprocess.run(
        run_cmd,
        input=input_data,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    result["Observed Output"] = run_process.stdout.strip()
    if run_process.stderr:
        result["Runtime Errors"] = run_process.stderr.strip()
        match = re.search(r"SUMMARY:.*?(\n|$)", result["Runtime Errors"], re.DOTALL)
        if match:
            result["Runtime Errors"] = match.group().strip()
        chunks = result["Runtime Errors"].strip().split("\n\n")

        results = []
        for chunk in chunks:
            lines = chunk.split("\n")
            collected = []
            for line in lines:
                collected.append(line)
                if "in main" in line:
                    break
            results.append("\n".join(collected))
        result["Runtime Errors"] = results
    return result


def extract_code_blocks(cpp_code, log_entries):
    lines = cpp_code.splitlines()
    annotated_code = lines[:]

    for entry in log_entries:
        summary_pattern = r"SUMMARY: \w+Sanitizer: (.+?) /"
        match_summary = re.search(summary_pattern, entry)
        error_match = re.search(summary_pattern, entry).group(1)
        error_match = match_summary.group(1) if match_summary else "Unknown Error"

        code_pattern = r":(\d+):\d+"
        match_code = re.search(code_pattern, entry)
        if match_code:
            line_number = int(match_code.group(1))

            if 0 < line_number <= len(annotated_code):
                annotated_code[line_number - 1] += f"  // <---- Error:{error_match}"

    return "\n".join(annotated_code)


def merge_results(result1, result2):
    merged_result = {
        "Compilation Error": [],
        "Observed Output": "",
        "Runtime Errors": [],
    }
    merged_result["Compilation Error"] = (
        result1["Compilation Error"] or result2["Compilation Error"]
    )

    merged_result["Observed Output"] = (
        result1["Observed Output"] or result2["Observed Output"]
    )
    merged_result["Runtime Errors"] = (
        result1["Runtime Errors"] + result2["Runtime Errors"]
    )
    return merged_result


def sanitize(
    cpp_code,
    cpp_file_path="./program.cpp",
    output_file_path="./program",
    input_test_case="",
):
    compile_cmd1 = [
        "clang++",
        cpp_file_path,
        "-o",
        output_file_path,
        "-fsanitize=address,leak,undefined",
        "-flto",
        "-fvisibility=hidden",
        "-g",
        "-std=c++17",
    ]
    compile_cmd2 = [
        "clang++",
        cpp_file_path,
        "-o",
        output_file_path,
        "-fsanitize=memory",
        "-fsanitize-memory-track-origins=2",
        "-fno-omit-frame-pointer",
        "-g",
        "-std=c++17",
    ]
    result1 = compile_and_run(
        cpp_code, cpp_file_path, input_test_case, output_file_path, compile_cmd1
    )
    result2 = compile_and_run(
        cpp_code, cpp_file_path, input_test_case, output_file_path, compile_cmd2
    )

    merged_result = merge_results(result1, result2)
    if merged_result["Runtime Errors"]:
        merged_result["Runtime Errors"] = extract_code_blocks(
            cpp_code, merged_result["Runtime Errors"]
        )
    else:
        merged_result["Runtime Errors"] = ""
    return merged_result
