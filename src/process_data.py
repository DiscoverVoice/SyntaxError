import json

input_file = "../data/qa.json"
qa_output_file = "../data/qa_data.jsonl"
debug_output_file = "../data/debug_data.jsonl"


def process_data(input_path, qa_output_path, debug_output_path):
    with open(input_path, "r") as f:
        data = json.load(f)

    qa_data = []
    debug_data = []

    for problem_id, problem_data in data.items():
        formatted_spec = problem_data.get("formatted_specification", "N/A")
        sub_func_code = problem_data.get("sub_func_code", "N/A")
        test_case_input = problem_data.get("test_case_input", "N/A")
        test_case_output = problem_data.get("test_case_output", "N/A")
        debug = problem_data.get("debug", "N/A")
        qa = problem_data.get("QA", "N/A")

        qa_prompt = (
            f"You are responsible for providing feedback on the code, specifications, and debugging results.\n\n"
            f"### Specification:\n{formatted_spec}\n\n"
            f"### Sub-function Code:\n{sub_func_code}\n\n"
            f"### Debugging Result:\n{debug}\n\n"
            "### Feedback:\n"
            "Q1. Summary of Implementation Errors:\n"
            "Q2. Summary of Consistency Between Specification and Code:\n"
            "Q3. Suggestions for Improvements or Alternative Implementations:\n"
            "Q4. Summary of Debugging Results:\n"
        )
        qa_data.append(
            {
                "instruction": "Provide detailed feedback on the code and debugging results.",
                "input": qa_prompt,
                "output": qa,
            }
        )

        debug_prompt = (
            f"Provide debugging analysis for the given test case. "
            f"Focus on step-by-step evaluation, validation, and suggestions for improvement.\n"
            f"### C++ Code:\n{sub_func_code}\n\n"
            f"### Test Case:\n- Input:\n{test_case_input}\n\n"
            f"- Expected Output:\n{test_case_output}\n\n"
            "### Step-by-Step Debugging:\n"
            "1. **Code Execution Analysis:**\n"
            "2. **Validation:**\n"
            "3. **Improvement Suggestions:**\n"
        )
        debug_data.append(
            {
                "instruction": "Analyze the provided C++ code and test case for debugging purposes.",
                "input": debug_prompt,
                "output": debug,
            }
        )

    def save_as_jsonl(data_list, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            for item in data_list:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    save_as_jsonl(qa_data, qa_output_path)
    save_as_jsonl(debug_data, debug_output_path)


process_data(input_file, qa_output_file, debug_output_file)
