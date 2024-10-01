require('dotenv').config();  // .env 파일에서 로드
const axios = require('axios');

// OpenAI API 키 설정
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || 'your-api-key-here';

// API로부터 응답을 받아오는 함수
async function getChatGPTResponse(prompt) {
    const url = 'https://api.openai.com/v1/completions';
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
    };

    const data = {
        model: 'gpt-4O', 
        prompt: prompt,
        max_tokens: 1000
    };

    try {
        const response = await axios.post(url, data, { headers: headers });
        return response.data.choices[0].text;
    } catch (error) {
        console.error('Error fetching response from OpenAI:', error);
        return null;
    }
}


module.exports = {
    getChatGPTResponse
};
