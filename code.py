from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('SECRET_KEY'))
# OpenAI API 키 설정

previous_responses = []

def read_input_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        print(f"Read data from input.json: {data}")  # 데이터 확인
        return data['natural_language_spec']
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")  # JSON 형식 오류 처리
        raise

# 입력 파일 경로 설정
json_file_path = os.path.join(os.path.dirname(__file__), 'input.json')

print(f"Looking for input file at: {json_file_path}")  # 경로 확인

natural_language_spec = read_input_json(json_file_path)

# 자연어 명세를 정형 명세로 변환하는 함수
def natural_language_to_standardized_spec(natural_language_spec):
    prompt = f"""
    Analyze the following natural language specification and convert it into a standardized specification:
    {natural_language_spec}
    
    1. 변수 및 제약 조건을 포함한 입력 형식
    2. 출력 형식과 제약 조건
    3. 규칙 요약
    4. 조건
    5. 시간 및 메모리 제한
    마지막으로 초기 시드를 제공하기 위한 입력 예시도 제공해라.
    """
    try:
        response = client.chat.completions.create(model="gpt-4o",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}])
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred in natural_language_to_standardized_spec: {e}"

def generate_function_code(standardized_spec):
    prompt = f"""
    Based on the following standardized specification, generate the C++ code to solve the problem and no explanation, only code:
    {standardized_spec}
    """
    try:
        response = client.chat.completions.create(model="gpt-4o",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}])
        result = response.choices[0].message.content.strip()
        previous_responses.append(result)
        return result 
    except Exception as e:
        return f"An error occurred in generate_function_code: {e}"


# 자연어 명세를 정형 명세로 변환
standardized_spec = natural_language_to_standardized_spec(natural_language_spec)
print("standardized_spec:\n")
print(standardized_spec)

# 정형 명세를 JSON 파일로 저장
standard_spec_file = os.path.join(os.path.dirname(__file__), 'standard_spec.json')
with open(standard_spec_file, 'w') as f:
    json.dump({'standardized_spec': standardized_spec}, f, indent=2)

# 정형 명세를 입력하여 코드 생성
generated_code = generate_function_code(standardized_spec)
print("Generated Code:\n")
print(generated_code)

# 생성된 코드를 JSON 파일로 저장
generated_code_file = os.path.join(os.path.dirname(__file__), 'generated_code.json')
with open(generated_code_file, 'w') as f:
    json.dump({'generated_code': generated_code}, f, indent=2)

