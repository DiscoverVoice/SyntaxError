const vscode = require("vscode");
const { exec } = require("child_process");
const path = require("path");
const fs = require("fs");
const winston = require("winston");

// 로거 설정
const logger = winston.createLogger({
  level: "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
  ),
  transports: [
    new winston.transports.File({
      filename: path.join(__dirname, "extension.log"),
    }), // 로그 파일 경로 명시
    new winston.transports.Console(),
  ],
});

// JSON 파일 읽기 함수
function readJsonFile(filePath) {
  if (fs.existsSync(filePath)) {
    const data = fs.readFileSync(filePath, "utf8");
    return JSON.parse(data);
  } else {
    logger.error(`File not found: ${filePath}`);
    return null;
  }
}

// JSON 데이터 포맷팅 출력하는 함수
function prettyPrintJson(jsonData) {
  return JSON.stringify(jsonData, null, 2); // 들여쓰기 2칸
}

function activate(context) {
  let disposable = vscode.commands.registerCommand(
    "extension.askChatGPT",
    async () => {
      const naturalLanguageSpec = await vscode.window.showInputBox({
        placeHolder: "자연어 명세를 입력하세요...",
        prompt: "예: 두 수의 합을 계산하는 함수 작성",
      });

      logger.info("User Input: " + naturalLanguageSpec);

      if (naturalLanguageSpec) {
        const inputData = {
          natural_language_spec: naturalLanguageSpec,
        };

        const jsonFilePath = path.join(__dirname, "input.json");
        fs.writeFileSync(jsonFilePath, JSON.stringify(inputData, null, 2));

        logger.info("JSON file created: " + jsonFilePath);

        const pythonScriptPath = path.join(__dirname, "code.py");

        exec(`python3 ${pythonScriptPath}`, (error, stdout, stderr) => {
          if (error) {
            vscode.window.showErrorMessage(`Error: ${stderr}`);
            logger.error("Error executing Python script: " + stderr);
            return;
          }

          // 정형 명세와 생성된 코드 JSON 파일 경로
          const standardizedSpecFile = path.join(
            __dirname,
            "standard_spec.json",
          );
          const generatedCodeFile = path.join(__dirname, "generated_code.json");

          // JSON 파일을 읽어옴
          const standardizedSpec = readJsonFile(standardizedSpecFile);
          const generatedCode = readJsonFile(generatedCodeFile);

          if (standardizedSpec && generatedCode) {
            // JSON 파일 포맷팅 출력
            console.log(
              "Standardized Spec:\n" + prettyPrintJson(standardizedSpec),
            );
            console.log("Generated Code:\n" + prettyPrintJson(generatedCode));

            vscode.window.showInformationMessage(
              `Generated Code:\n${generatedCode.generated_code}`,
            );

            // 로그에 저장
            logger.info(
              "Standardized Spec: " + standardizedSpec.standardized_spec,
            );
            logger.info("Generated Code: " + generatedCode.generated_code);
          } else {
            vscode.window.showErrorMessage(
              "정형 명세 또는 생성된 코드를 불러오지 못했습니다.",
            );
          }
        });
      } else {
        vscode.window.showWarningMessage("자연어 명세를 입력하지 않았습니다.");
      }
    },
  );

  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
