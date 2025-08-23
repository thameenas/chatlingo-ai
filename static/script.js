let sessionId = localStorage.getItem('session_id') || 'web_' + Math.random().toString(36).slice(2);
localStorage.setItem('session_id', sessionId);
let chatHistory = [];

function appendMessage(text, sender) {
    const chatBox = document.getElementById('chatBox');
    const div = document.createElement('div');
    div.className = 'msg ' + sender;
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = text.replace(/\n/g, '<br>');
    div.appendChild(bubble);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    chatHistory.push({ text: text, sender: sender });

}

function sendMessage() {
    const input = document.getElementById('userInput');
    const msg = input.value.trim();
    if (!msg) return;
    appendMessage(msg, 'user');
    input.value = '';
    // API endpoint removed
    appendMessage('Web chat API has been removed', 'bot');
}

function resetChat() {
    // Clear chat history in UI only
    chatHistory = [];
    document.getElementById('chatBox').innerHTML = '';
    // New session id for a fresh chat
    sessionId = 'web_' + Math.random().toString(36).slice(2);
    localStorage.setItem('session_id', sessionId);
    
    // Reset API endpoint removed
    appendMessage('Chat reset. Web chat API has been removed.', 'bot');
}


document.getElementById('userInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') sendMessage();
});
// Optionally, greet on load
appendMessage('Type "start" to begin your Kannada learning journey!', 'bot'); 