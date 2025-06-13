
function refreshUI() {
    const chatBox = document.getElementById('chatBox');
    chatBox.innerHTML = '';
    chatHistory.forEach(msg => {
        appendMessage(msg.text, msg.sender);
    });
    appendMessage('UI refreshed', 'bot');
}