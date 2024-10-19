from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('SECRET_KEY'))

def read_input_json(file_path):
  try:
    with open(file_path, 'r') as file:
      data = json.load(file)
    print(f"Read data from {file_path}: {data}")  # 데이터 확인
    return data['natural_language_spec']
  except FileNotFoundError as e:
    print(f"File not found: {e}")
    raise
  except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")  # JSON 형식 오류 처리
    raise

def find_latest_file(folder, prefix):
  """지정된 폴더에서 가장 최근의 파일을 찾는다."""
  files = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith('.json')]
  if not files:
    raise FileNotFoundError(f"No files found in {folder} with prefix '{prefix}'.")

  # 시간 정보를 기반으로 정렬
  files.sort(key=lambda f: f.split('_')[1].split('.')[0], reverse=True)  # 수정된 부분
  return files[0]  # 가장 최근 파일

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
    print(f"An error occurred in natural_language_to_standardized_spec: {e}")
    return None

def generate_function_code(standardized_spec):
  prompt = f"""
  Based on the following standardized specification, generate the C++ code to solve the problem and no explanation, only code:
  {standardized_spec}
  """
  try:
    response = client.chat.completions.create(model="gpt-4o",
    messages=[{"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": prompt}])
    return response.choices[0].message.content.strip()
  except Exception as e:
    print(f"An error occurred in generate_function_code: {e}")
    return None

def main():
  input_folder = os.path.join(os.path.dirname(__file__), 'Data', 'Input')
  input_file = os.path.join(input_folder, find_latest_file(input_folder, 'input_'))
  natural_language_spec = read_input_json(input_file)

  # 자연어 명세를 정형 명세로 변환
  standardized_spec = natural_language_to_standardized_spec(natural_language_spec)
  print("standardized_spec:\n")
  print(standardized_spec)

  # 정형 명세를 JSON 파일로 저장
  timestamp = input_file.split('_')[1].split('.')[0]  # timestamp 추출
  standardized_spec_file = os.path.join(os.path.dirname(__file__), 'Data', 'Standard_spec', f'standard_spec_{timestamp}.json')
  with open(standardized_spec_file, 'w') as f:
    json.dump({'standardized_spec': standardized_spec}, f, indent=2)
    print(f"Standardized specification saved to {standardized_spec_file}")  # 추가된 로그

  # 정형 명세를 입력하여 코드 생성
  generated_code = generate_function_code(standardized_spec)
  print("Generated Code:\n")
  print(generated_code)

  # 생성된 코드를 JSON 파일로 저장
  generated_code_file = os.path.join(os.path.dirname(__file__), 'Data', 'Generated', f'generated_code_{timestamp}.json')
  with open(generated_code_file, 'w') as f:
    json.dump({'generated_code': generated_code}, f, indent=2)
    print(f"Generated code saved to {generated_code_file}")  # 추가된 로그

if __name__ == "__main__":
  main()
