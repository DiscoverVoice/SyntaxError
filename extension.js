const vscode = require("vscode");
const { exec } = require("child_process");
const path = require("path");
const fs = require("fs");
const winston = require("winston");


const logger = winston.createLogger({
  level: "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
  ),
  transports: [
    new winston.transports.File({
      filename: path.join(__dirname, "logs", "extension.log"),
    }), 
    new winston.transports.Console(),
  ],
});




async function readJsonFile(filePath) {
  return new Promise((resolve, reject) => {
    if (fs.existsSync(filePath)) {
      fs.readFile(filePath, "utf8", (err, data) => {
        if (err) {
          logger.error(`File read error: ${err}`);
          reject(err);
        } else {
          resolve(JSON.parse(data));
        }
      });
    } else {
      logger.error(`File not found: ${filePath}`);
      reject(new Error(`File not found: ${filePath}`));
    }
  });
}


function prettyPrintJson(jsonData) {
  return JSON.stringify(jsonData, null, 2); 
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

        
        const timestamp = new Date().toISOString().replace(/T/, '_').replace(/:/g, '-').split('.')[0];
        const jsonFilePath = path.join(__dirname, "Data", "Input", `input_${timestamp}.json`);

        fs.writeFileSync(jsonFilePath, JSON.stringify(inputData, null, 2));

        logger.info("JSON file created: " + jsonFilePath);

        const pythonScriptPath = path.join(__dirname, "Code.py");

        
        exec(`python3 ${pythonScriptPath} ${timestamp}`, (error, stdout, stderr) => {
          if (error) {
            vscode.window.showErrorMessage(`Error: ${stderr}`);
            logger.error("Error executing Python script: " + stderr);
            return;
          }

          
          const standardizedSpecFile = path.join(
            __dirname,
            "Data",
            "Standard_spec",
            `standard_spec_${timestamp}.json`,
          );
          const generatedCodeFile = path.join(
            __dirname,
            "Data",
            "Generated",
            `generated_code_${timestamp}.json`,
          );

          
          Promise.all([readJsonFile(standardizedSpecFile), readJsonFile(generatedCodeFile)]).then(([standardizedSpec, generatedCode]) => {
            
            console.log("Standardized Spec:\n" + prettyPrintJson(standardizedSpec));
            console.log("Generated Code:\n" + prettyPrintJson(generatedCode));

            vscode.window.showInformationMessage(`Generated Code:\n${generatedCode.generated_code}`);

            
            logger.info("Standardized Spec: " + standardizedSpec.standardized_spec);
            logger.info("Generated Code: " + generatedCode.generated_code);
          }).catch(err => {
            vscode.window.showErrorMessage("정형 명세 또는 생성된 코드를 불러오지 못했습니다.");
            logger.error("Error reading JSON files: " + err);
          });
        });
      } else {
        vscode.window.showWarningMessage("자연어 명세를 입력하지 않았습니다.");
      }
      
    },
  );




let loadWorksCommand = vscode.commands.registerCommand("extension.LoadWorks", async () => {
  const inputFolderPath = path.join(__dirname, 'Data', 'Input');

  
  const files = fs.readdirSync(inputFolderPath).filter(file => file.startsWith('input_') && file.endsWith('.json'));

  if (files.length === 0) {
    vscode.window.showWarningMessage("이전 작업이 없습니다.");
    return;
  }

  
  const fileOptions = files.map(file => ({
    label: file,
    description: "이전 작업"
  }));

  const selectedFile = await vscode.window.showQuickPick(fileOptions, {
    placeHolder: "이전 작업을 선택하세요" 
  });

  if (selectedFile) {
    const selectedFilePath = path.join(inputFolderPath, selectedFile.label);
    const inputData = await readJsonFile(selectedFilePath);

    if (inputData) {
      logger.info("Selected Input: " + selectedFile.label);
      vscode.window.showInformationMessage(`선택된 작업: ${selectedFile.label}`);
      
      
      const timestamp = selectedFile.label.replace('input_', '').replace('.json', '');

      
      const standardizedSpecFile = path.join(__dirname, 'Data', 'Standard_spec', `standard_spec_${timestamp}.json`);
      const generatedCodeFile = path.join(__dirname, 'Data', 'Generated', `generated_code_${timestamp}.json`);

      try {
        const standardizedSpec = await readJsonFile(standardizedSpecFile);
        const generatedCode = await readJsonFile(generatedCodeFile);

      
        vscode.window.showInformationMessage(`선택된 정형 명세: ${prettyPrintJson(standardizedSpec)}`);
        vscode.window.showInformationMessage(`생성된 코드: ${prettyPrintJson(generatedCode)}`);

        logger.info("Standardized Spec: " + standardizedSpec.standardized_spec);
        logger.info("Generated Code: " + generatedCode.generated_code);
      } catch (err) {
        vscode.window.showErrorMessage("정형 명세 또는 생성된 코드를 불러오지 못했습니다.");
        logger.error("Error reading standardized spec or generated code: " + err);
      }
    }
  } else {
    vscode.window.showWarningMessage("아무것도 선택하지 않았습니다.");
  }
});





let showMenuCommand = vscode.commands.registerCommand("extension.showMenu", async () => {
  const menuOptions = [
    { label: "Ask ChatGPT", description: "ChatGPT에게 질문하기" },
    { label: "Load works", description: "이전 작업 불러오기" },
    { label: "QA Test", description: "Load QA model" },
    { label: "Fuzzing", description: "Fuzz test." },
    { label: "Exit", description: "종료" },
  ];

  const selection = await vscode.window.showQuickPick(menuOptions, {
    placeHolder: "옵션을 선택하세요",
  });

  if (selection) {
    switch (selection.label) {
      case "Ask ChatGPT":
        vscode.commands.executeCommand("extension.askChatGPT");
        break;
      case "Load works":
        vscode.commands.executeCommand("extension.LoadWorks");
        break;
      case "QA Test":
        await runQATest();
        break;
      case "Fuzzing":
        await runFuzzing();
        break;
      case "Exit":
        vscode.window.showInformationMessage("메뉴 종료");
        break;
      default:
        vscode.window.showErrorMessage("알 수 없는 명령입니다.");
    }
  } else {
    vscode.window.showWarningMessage("아무것도 선택하지 않았습니다.");
  }
});
  
  async function runQATest() {
    const generatedCodeFolder = path.join(__dirname, 'Data', 'Generated');
    const files = fs.readdirSync(generatedCodeFolder).filter(file => file.startsWith('generated_code_') && file.endsWith('.json'));

    if (files.length === 0) {
      vscode.window.showWarningMessage("생성된 코드가 없습니다.");
      return;
    }

    
    const latestCodeFile = files[files.length - 1];
    const latestCodeFilePath = path.join(generatedCodeFolder, latestCodeFile);

    
    exec(`QA.py ${latestCodeFilePath}`, (error, stdout, stderr) => {
      if (error) {
        vscode.window.showErrorMessage(`QA Test Error: ${stderr}`);
        logger.error("QA Test execution error: " + stderr);
        return;
      }
      
      
      vscode.window.showInformationMessage(`QA Test Results:\n${stdout}`);
      logger.info("QA Test Results: " + stdout);
    });
  }

  
  async function runFuzzing() {
    const generatedCodeFolder = path.join(__dirname, 'Data', 'Generated');
    const files = fs.readdirSync(generatedCodeFolder).filter(file => file.startsWith('generated_code_') && file.endsWith('.json'));

    if (files.length === 0) {
      vscode.window.showWarningMessage("생성된 코드가 없습니다.");
      return;
    }

    
    const latestCodeFile = files[files.length - 1];
    const latestCodeFilePath = path.join(generatedCodeFolder, latestCodeFile);

    
    exec(`Fuzzer.py ${latestCodeFilePath}`, (error, stdout, stderr) => {
      if (error) {
        vscode.window.showErrorMessage(`Fuzzing Error: ${stderr}`);
        logger.error("Fuzzing execution error: " + stderr);
        return;
      }
      
      
      vscode.window.showInformationMessage(`Fuzzing Results:\n${stdout}`);
      logger.info("Fuzzing Results: " + stdout);
    });
  }

  context.subscriptions.push(extension.askChatGPT, extension.LoadWorks, extension.showMenu);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
