document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (chatContainer.classList.contains('hidden')) {
            chatbotIcon.click();
        }
    }, 2000); // Opens the chat after 2 seconds
});

let chatbotIcon = document.getElementById('chatbot-icon');
let chatContainer = document.getElementById('chat-container');
let closeChat = document.getElementById('close-chat');
let chatBox = document.getElementById('chat-box');
let userInput = document.getElementById('user-input');
let sendBtn = document.getElementById('send-btn');
let questions = [
    "What's your email ID?",
    "What's your highest qualification?",
    "What's your LinkedIn profile Link?",
    "What's your last company?",
    "How many years of experience do you have?",
    "Please enter your unique code.",
    "What is your annual expected salary?(lakhs)",
    "Please mention your key skills.",
    "How much notice period do you require?(Days)"
];
let responses = {};
let questionIndex = 0;

chatbotIcon.addEventListener('click', () => {
    chatContainer.classList.remove('hidden');
    chatbotIcon.classList.add('hidden');
    setTimeout(() => {
        addMessage(" Welcome to the Q3edge recruitment process. Before we proceed further, could you please tell me your name?", 'bot');
    }, 500);
});

closeChat.addEventListener('click', () => {
    chatContainer.classList.add('hidden');
    chatbotIcon.classList.remove('hidden');
});

sendBtn.addEventListener('click', () => {
    let userText = userInput.value.trim();
    if (userText !== "") {
        addMessage(userText, 'user');
        userInput.value = "";
        setTimeout(() => {
            handleResponse(userText);
        }, 500);
    }
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendBtn.click();
    }
});

function addMessage(text, type) {
    let messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function handleResponse(response) {
    let botMessage = document.querySelector('.typing');
    if (botMessage) {
        botMessage.remove();
    }
    switch (questionIndex) {
        case 0:
            if (/^[a-zA-Z ]+$/.test(response)) {
                responses.name = response;
                addSmartResponse(`Nice to meet you, ${response}.`, () => askNextQuestion());
            } else {
                addMessage("Please enter a valid name.", 'bot');
            }
            break;
        case 1:
            if (/^\S+@\S+\.\S+$/.test(response)) {
                responses.email = response;
                addSmartResponse(`Got it, ${responses.name}.`, () => askNextQuestion());
            } else {
                addMessage("Please enter a valid email address.", 'bot');
            }
            break;
        case 2:
            responses.qualification = response;
            addSmartResponse(`${response} is impressive!`, () => askNextQuestion());
            break;
        case 3:
            if (response.startsWith('https://www.linkedin.com/')) {
                responses.linkedin = response;
                addSmartResponse(`Thank you, ${responses.name}! We've recorded your LinkedIn profile.`, () => askNextQuestion());
            } else {
                addMessage("Please enter a valid LinkedIn profile URL.", 'bot');
            }
            break;
        case 4: // Handle response for last company
            responses.last_company = response;
            addSmartResponse(`Great! Your last company is ${response}.`, () => askNextQuestion());
            break;
        case 5: // Handle response for years of experience
        if (/^\d+$/.test(response)) {
            responses.years_experience = response;
            addSmartResponse(`Nice! You have ${response} years of experience.`, () => askNextQuestion());
        } else {
            addMessage("Please enter a valid number for years of experience.", 'bot');
        }
        break;
        case 6: // Handle response for unique code
            responses.unique_code = response;
            addSmartResponse(`Got it! Your unique code is ${response}.`, () => askNextQuestion());
            break;
         case 7: // Handle response for expected salary
            if (/^\d+$/.test(response)) {
                responses.expected_salary = response;
                addSmartResponse(`Understood! Your expected salary is ${response}.`, () => askNextQuestion());
            } else {
                addMessage("Please enter a valid number for expected salary.", 'bot');
            }
            break;
        case 8: // Handle response for key skills
            responses.key_skills = response;
            addSmartResponse(`Thank you! Your key skills are ${response}.`, () => askNextQuestion());
            break;
            case 9: // Handle response for notice period
            if (/^\d+$/.test(response)) {
                responses.notice_period = response;
                addSmartResponse(`Noted! Your notice period is ${response}.`, () => {
                    sendDetailsToServer(responses);
                });
            } else {
                addMessage("Please enter a valid number for notice period.", 'bot');
            }
            break;
    }
}


function askNextQuestion() {
    if (questionIndex < questions.length) {
        addMessage(questions[questionIndex], 'bot');
        questionIndex++;
    }
}

function addSmartResponse(text, callback) {
    let typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing';
    typingDiv.textContent = '...';
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    setTimeout(() => {
        typingDiv.remove();
        addMessage(text, 'bot');
        if (callback) callback();
    }, 1000);
}

function sendDetailsToServer(details) {
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(details)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addMessage(data.error, 'bot');
        } else {
            addMessage(data.message, 'bot');
        }
    })
    .catch(error => {
        addMessage('An error occurred. Please try again later.', 'bot');
        console.error('Error:', error);
    });
}
