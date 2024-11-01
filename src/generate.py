from utils.model import LLM
from typing import Dict
import re

def get_code(text, type_):
        match = re.search(rf"```{type_}\s+(.*?)```", text, re.DOTALL)
        return match.group(1).strip() if match else ""

def generate_spec(problem: Dict):
    llm = LLM("microsoft/Phi-3-small-8k-instruct")

    test_cases = []
    for key, value in problem.items():
        if key.startswith("test case"):
            case_num = key.split(" ")[-1]
            example = {
                "input": value,
                "output": problem.get(f"test case output {case_num}", "Not specified"),
            }
            test_cases.append(example)

    problem_desc = (
        f"Problem Statement: {problem['problem']}\n"
        f"Input: {problem['input']}\n"
        f"Output: {problem['output']}\n"
    )

    for i, case in enumerate(test_cases, start=1):
        problem_desc += (
            f"\nTest Case Input {i}:\n```\n{case['input']}\n```\n"
            f"Test Case Output {i}:\n```\n{case['output']}\n```\n"
        )
    format = (
        "1. Inputs: \n"
        "   - Input variables: \n"
        "   - Constraints of input variables: \n"
        "   - Input format: \n"
        "2. Outputs: \n"
        "   - Output variables: \n"
        "   - Constraints of output variables: \n"
        "   - Output format: \n"
        "3. Definition of problem: \n"
    )
    system_prompt = "Change the below specification to fill the formal specification.\n"
    example = (
        "<|endoftext|><|system|>\n"
        f"{system_prompt}"
        "<|end|>"
        "<|endoftext|><|user|>\n"
        "Problem Statement: Write a program that takes a year as input and outputs 1 if it is a leap year, or 0 if it is not.\nA leap year is defined as a year that is a multiple of 4 but not a multiple of 100, or a multiple of 400.\nFor example, the year 2012 is a leap year because it is a multiple of 4 and not a multiple of 100. The year 1900 is not a leap year because it is a multiple of 100 but not a multiple of 400. However, the year 2000 is a leap year because it is a multiple of 400.\n"
        "Input: The first line contains a year. The year is a natural number greater than or equal to 1 and less than or equal to 4000.\n"
        "Output: Output 1 if the year is a leap year, otherwise output 0.\n"
        "Test Case Input 1:\n```2000```\n"
        "Test Case Output 1:\n```1```\n"
        "Test Case Input 2:\n```1999```\n"
        "Test Case Output 2:\n```0```\n"
        f"{format}"
        "<|end|>\n"
        "<|assistant|>\n"
        "1. Inputs: \n"
        "   - Input variables: \n"
        "      - year: A natural number representing the year to be checked.\n"
        "   - Constraints of input variables: \n"
        "      - 1 ≤ year ≤ 4000\n"
        "   - Input format: \n"
        "      - A single line containing one integer representing the year.\n"
        "2. Outputs: \n"
        "   - Output variables: \n"
        "      - regions_non_colorblind: Number of distinct regions visible to a non-colorblind person.\n"
        "      - regions_colorblind: Number of distinct regions visible to a red-green colorblind person.\n"
        "   - Constraints of output variables: \n"
        "      - is_leap must be either 1 (leap year) or 0 (not a leap year).\n"
        "   - Output format: \n"
        "      - A single line containing the result as an integer (1 or 0).\n"
        "3. Definition of problem: \n"
        "   - A given year year is considered a leap year (is_leap = 1) if it satisfies the following conditions: \n"
        "      - It is divisible by 4 but not divisible by 100, or\n"
        "      - It is divisible by 400.\n"
        "   - If the year does not meet these conditions, it is not a leap year (is_leap = 0).\n"
        "<|end|>\n"
    )
    prompt = (
        f"{example}\n"
        "<|endoftext|><|user|>\n"
        f"{system_prompt}"
        f"{problem_desc}"
        f"{format}"
        "<|end|>\n"
        "<|assistant|>\n"
    )
    output = llm.generate_text(prompt)
    return output


def generate_seed_generator(formatted_spec):
    llm = LLM("Qwen/Qwen2.5-Coder-7B-Instruct")

    prompt = f"""
    You are a code assistant specializing in making input generetor. Please create a Python code that generates random input examples based on specified variables and constraints.
    Function Requirements:
    {formatted_spec}
    """
    output = llm.generate_text(prompt)

    return get_code(output, "python")


def generate_code(standardized_spec, feedback=None):
    llm = LLM("gpt-4o")
    if feedback is None:
        system_prompt = """When prompting for user input, do not display any text. Simply wait for the input without showing any message, such as "Enter your age" or similar prompts."""

        prompt = f"""
        "<|endoftext|><|system|>\n"
        f"{system_prompt}"
        "<|end|>"
        Helpful tips for solving problems:
        - Approach the solution step-by-step.
        - Look at the big picture of the problem.
        - If solving the whole problem is challenging, break it down into smaller parts.
        - Consider various test cases: common scenarios, very small inputs, very large inputs, and edge cases.
        - Review the constraints and limitations carefully.
        - Implement C++ code.
        Specification:{standardized_spec}
        C++ Code:
        """
    else:
        prompt = f"""
        {feedback}
        C++ Code:
        {standardized_spec}
        """

    output = llm.generate_text(prompt)
    return get_code(output, "cpp")

def generate_sub_function(code):
    llm = LLM("Qwen/Qwen2.5-7B-Instruct", temperature=0.7, top_p=0.95, max_tokens=2048)
    
    prompt1 = (
        f"Code: {code}\n"
        "Convert the given C++ code into a hierarchical tree-style structure:\n"
        "  - Separate each major step or logical block into its own sub-function.\n"
        "  - The main function should orchestrate these sub-functions, creating a tree structure where sub-functions call smaller helper functions as needed.\n"
        "  - Provide the updated code in C++ format, with each function defined separately in a clear and flattened structure, using the ```cpp``` block.\n\n"
        "Hierarchical C++ Code:\n"
    )
    output1 = llm.generate_text(prompt1)
    output1 = get_code(output1, "cpp")
    prompt2 = (
        f"Code: {output1}\n"
        "Function prototype must be declared to avoid comple error."
    )
    output2 = llm.generate_text(prompt2)
    return get_code(output2, "cpp")


def generate_debug(sub_func, test_case_input, test_case_output):
    llm = LLM("gpt-4o",
              max_model_len=15000,
              gpu_memory_utilization=1.0,
              temperature=0.7,
                top_p=0.95,
                max_tokens=15000,
              )
    prompt = (
        "<|endoftext|><|system|>"
        "Provide debugging analysis for the given test case. "
        "Focus on step-by-step evaluation, validation, and suggestions for improvement.<|end|>\n"
        "<|user|>"
        "C++ Code:\n"
        f"{sub_func}\n\n"
        "Test Case:\n"
        f"  - Input:\n{test_case_input}\n"
        f"  - Expected Output:\n{test_case_output}\n"
        "<|end|>\n"
        "<|assistant|>\n"
        "### Step-by-Step Debugging:\n"
        "1. **Code Execution Analysis:**\n"
        "   - (Explain how the code processes the input step by step)\n"
        "2. **Validation:**\n"
        "   - (Describe if the output matches the expected behavior)\n"
        "3. **Improvement Suggestions:**\n"
        "   - (Provide suggestions to improve performance, readability, or correctness)\n"
        "<|end|>"
    )
    
    output = llm.generate_text(prompt)
    return f"Debugging Analysis for Test Case:\n{output}"

def generate_qa(formatted_spec, code, debug):
    llm = LLM("gpt-4o")
    prompt = (
        "<|endoftext|><|system|>\n"
        "You are responsible for providing feedback on the code, specifications, and debugging results. "
        "<|end|>\n"
        "<|user|>\n"
        f"Formatted Specification:\n{formatted_spec}\n\n"
        f"Sub-function Code:\n{code}\n\n"
        f"Debugging Result:\n{debug}\n\n"
        "<|end|>\n"
        "<|assistant|>\n"
        "### Feedback:\n"
        "Q1. Summary of Implementation Errors:\n"
        "Q2. Summary of Consistency Between Specification and Code:\n"
        "Q3. Suggestions for Improvements or Alternative Implementations:\n"
        "Q4. Summary of Debugging Results:\n"
        "<|end|>"
    )
    output = llm.generate_text(prompt)
    return output
