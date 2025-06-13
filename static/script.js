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
    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_msg: msg, session_id: sessionId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.response) {
            appendMessage(data.response, 'bot');
        } else if (data.error) {
            appendMessage('⚠️ ' + data.error, 'bot');
        }
    })
    .catch(err => {
        appendMessage('⚠️ Network error', 'bot');
    });
}

function resetChat() {
    // Clear chat history in UI and backend
    chatHistory = [];
    document.getElementById('chatBox').innerHTML = '';
    // New session id for a fresh chat
    sessionId = 'web_' + Math.random().toString(36).slice(2);
    localStorage.setItem('session_id', sessionId);
    
    // Call the reset API endpoint
    fetch('/api/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            appendMessage('⚠️ ' + data.error, 'bot');
        } else {
            appendMessage('Chat reset. Type "start" to begin again.', 'bot');
        }
    })
    .catch(err => {
        appendMessage('⚠️ Network error', 'bot');
    });
}


document.getElementById('userInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') sendMessage();
});
// Optionally, greet on load
appendMessage('Type "start" to begin your Kannada learning journey!', 'bot'); 