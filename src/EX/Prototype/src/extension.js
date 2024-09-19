// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');
const { getChatGPTResponse } = require('./api');  // 받아온거

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
	console.log('Congratulations, your extension "Prototype" is now active!');
	let disposable = vscode.commands.registerCommand('extension.askChatGPT', async function () {
		// 사용자가 입력한 질문 받기
		const userInput = await vscode.window.showInputBox({ prompt: 'ChatGPT에 질문하기' });
	
		if (userInput) {
			vscode.window.showInformationMessage('ChatGPT에 질문 중...');
	
			// OpenAI API 호출
			const response = await getChatGPTResponse(userInput);
	
			if (response) {
				// 응답을 VSCode에 출력
				vscode.window.showInformationMessage('ChatGPT 응답: ' + response);
			}
		}
	});
	
	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
	activate,
	deactivate
}
