from utils.model import LLM
from typing import Dict
import re
from utils.model import OpenAI, LocalLLM, LoRALLM

def get_code(text, type_):
    match = re.search(rf"```{type_}\s+(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else ""

def make_code(text, type_):
    return f"```{type_}\n{text}\n```"

def generate_spec(problem: Dict):
    llm = LocalLLM(
        name="microsoft/Phi-3-small-8k-instruct",
        temperature=0.6,
        top_p=0.95,
        repetition_penalty=1.2,
        gpu_memory_utilization=0.9
    )
    
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
    del llm
    return output


def generate_code(standardized_spec, feedback=None):
    llm = OpenAI(name="gpt-4o")
    if feedback is None:
        system_prompt = """When prompting for user input, do not display any text. Simply wait for the input without showing any message, such as "Enter your age" or similar prompts."""

        prompt = f"""
        "<|endoftext|><|system|>\n"
        f"{system_prompt}"
        "<|end|>"
        "Add function prototypes to avoid complie errors.
        Specification:{standardized_spec}
        C++ Code:
        """
    else:
        prompt = f"""
        {feedback}
        C++ Code:
        {standardized_spec}
        Please give me revised code.
        C++ Code:
        """

    output = llm.generate_text(prompt)
    code = get_code(output, "cpp")
    code = make_code(code, "cpp")
    return code


def generate_sub_function(code):
    llm1 = LocalLLM(
        name="Qwen/Qwen2.5-7B-Instruct", temperature=0.7, top_p=0.95, max_tokens=2048
    )

    prompt1 = (
        f"Code: {code}\n"
        "Convert the given C++ code into a hierarchical tree-style structure:\n"
        "  - Separate each major step or logical block into its own sub-function.\n"
        "  - The main function should orchestrate these sub-functions, creating a tree structure where sub-functions call smaller helper functions as needed.\n"
        "  - Provide the updated code in C++ format, with each function defined separately in a clear and flattened structure, using the ```cpp``` block.\n\n"
        "Hierarchical C++ Code:\n"
    )
    output1 = llm1.generate_text(prompt1)
    output1 = get_code(output1, "cpp")
    code = make_code(output1, "cpp")
    del llm1
    llm2 = LocalLLM(
        name="Qwen/Qwen2.5-7B-Instruct", temperature=0.4, top_p=0.95, max_tokens=2048
    )
    prompt2 = (
       f"Code: {code}\n"
        "Please analyze the code provided and generate all necessary function prototypes to ensure the code compiles correctly. "
        "Each prototype should include the return type, function name, and parameter types with meaningful names, following C/C++ conventions. "
        "If the function is already defined in the code, ensure its prototype matches the definition."
    )
    output2 = llm2.generate_text(prompt2)
    output2 = get_code(output2, "cpp")
    code = make_code(output2, "cpp")
    del llm2
    return code


def generate_debug(
    formatted_spec, sub_func, test_case_input, test_case_output, observed_output
):
    llm = LoRALLM(
        name="./QaA",
        max_model_len=10000,
        gpu_memory_utilization=0.9,
        temperature=0.4,
        top_p=0.90,
        max_tokens=1500,
        repetition_penalty=1.1,
    )
    prompt = (
        "Formatted Spec:\n"
        f"{formatted_spec}\n\n"
        "Provide debugging analysis for the given test case. "
        "Focus on step-by-step evaluation, validation, and suggestions for improvement.\n"
        "C++ Code:\n"
        f"{sub_func}\n\n"
        "Test Case:\n"
        f"  - Input:\n{test_case_input}\n"
        f"  - Expected Output:\n{test_case_output}\n"
        f"  - Observed Output:\n{observed_output}\n"
        "### Step-by-Step Debugging:\n"
        "1. **Output Matching:**\n"
        "   - Compare the observed output with the expected output. If they match, indicate 'Match: True'; otherwise, indicate 'Match: False.'\n"
        "2. **Code Execution Analysis:**\n"
        "   - (Explain how the code processes the input step by step)\n"
        "3. **Validation:**\n"
        "   - (Describe if the output matches the expected behavior)\n"
        "4. **Improvement Suggestions:**\n"
        "   - (Provide suggestions to improve performance, readability, or correctness)\n"
        "Answer:\n"
    )

    output = llm.generate_text(prompt)
    del llm
    return output


def generate_qa(formatted_spec, code, debug):
    llm = LoRALLM(
        name="./qa",
        max_model_len=10000,
        gpu_memory_utilization=0.9,
        temperature=0.6,
        top_p=0.95,
        max_tokens=1500,
        repetition_penalty=1.1,
    )
    prompt = (
        "You are responsible for providing feedback on the code, specifications, and debugging results. "
        f"Formatted Specification:\n{formatted_spec}\n\n"
        f"Sub-function Code:\n{code}\n\n"
        f"Debugging Result:\n{debug}\n\n"
        "### Feedback:\n"
        "1. **Summary of Implementation Errors:**\n"
        "2. **Summary of Consistency Between Specification and Code:**\n"
        "3. **Suggestions for Improvements or Alternative Implementations:**\n"
        "4. **Summary of Debugging Results:**\n\n"
        "Answer:\n"
    )
    output = llm.generate_text(prompt)
    del llm
    return output


def parse_pass_value(debug_result):
    """
    Extracts the 'pass' value (true or false) from the debugging output.

    Args:
        debug_output (str): Output string generated by the LLM.

    Returns:
        str: The value of 'pass' (true or false), or None if not found.
    """
    match = re.search(r"Answer:\s*(True|False)", debug_result)
    if match:
        return match.group(1)
    else:
        return "Unknown"
