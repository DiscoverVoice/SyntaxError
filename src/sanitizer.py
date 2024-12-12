import re
import subprocess
import os


def compile_and_run(cpp_code, cpp_file_path, input_data, output_file_path, compile_cmd):
    result = {"Compilation Error": "", "Observed Output": "", "Runtime Errors": ""}

    with open(cpp_file_path, "w") as cpp_file:
        cpp_file.write(cpp_code)

    compile_process = subprocess.run(
        compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if compile_process.returncode != 0:
        result["Compilation Error"] = compile_process.stderr
        os.remove(cpp_file_path)
        return

    os.environ["ASAN_OPTIONS"] = "halt_on_error=0:abort_on_error=0"
    os.environ["MSAN_OPTIONS"] = "halt_on_error=0:abort_on_error=0"

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

    return result


def merge_results(result1, result2):
    merged_result = {
        "Compilation Error": "",
        "Observed Output": "",
        "Runtime Errors": "",
    }

    merged_result["Compilation Error"] = (
        result1["Compilation Error"] + "\n" + result2["Compilation Error"]
    ).strip()
    merged_result["Observed Output"] = (
        result1["Observed Output"] or result2["Observed Output"]
    )
    merged_result["Runtime Errors"] = (
        result1["Runtime Errors"] + "\n" + result2["Runtime Errors"]
    ).strip()

    return merged_result

def split_texts(text):
    chunks = text.split('\n\n')
    return chunks

if __name__ == "__main__":
    cpp_file_path = "./program.cpp"
    output_file_path = "./program"
    cpp_code = """
    #include <iostream>
    #include <vector>
    #include <memory>
    using namespace std;

    int main() {
        int* ptr = new int[10];
        cout << ptr[5] << endl; // 초기화되지 않은 메모리 읽기

        delete[] ptr;
        cout << ptr[0] << endl; // 해제된 메모리 접근 (Use-after-free)
        int k = 5/0;
        return 0;
    }
    """
    input_test_case = ""
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


    from pprint import pprint
    result2["Runtime Errors"] = split_texts(result2["Runtime Errors"])
    pprint(result2["Runtime Errors"])
    # merged_result = merge_results(result1, result2)
    # print(merged_result["Runtime Errors"])
