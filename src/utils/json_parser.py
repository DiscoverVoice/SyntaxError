import json
import argparse
import os


def convert_to_descriptions(directory_path="./"):
    json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]
    descriptions = {}

    for filename in json_files:
        problem_number = filename.split(".")[0]
        file_path = os.path.join(directory_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            test_cases = []
            test_case_count = 1

            while True:
                input_key = f"test case input {test_case_count}"
                output_key = f"test case output {test_case_count}"

                if input_key not in data or output_key not in data:
                    break

                test_cases.append(
                    f"""Test Case Input {test_case_count}
```
{data[input_key]}
```
Test Case Output {test_case_count}
```
{data[output_key]}
```"""
                )

                test_case_count += 1

            problem_description = f"""Time Limit: {data['time limit']}
Memory Limit: {data['memory limit']}

Problem
{data['problem']}

Input
{data['input']}

Output
{data['output']}

{'\n'.join(test_cases)}"""

            descriptions[problem_number] = problem_description

    return descriptions


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        nargs="?",
        default="./",
        help="Directory path containing the JSON problem files (default: current directory)",
    )

    args = parser.parse_args()
    descriptions = convert_to_descriptions(args.directory)

    for problem_number, description in sorted(descriptions.items()):

        print(description)
