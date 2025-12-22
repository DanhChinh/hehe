function getTimeHHMM() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}${minutes}`;
}


function addMessage(content = "...", from = "player") {
    const chatBox = document.getElementById('chat-container');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${from}`;
    msgDiv.innerHTML = `#${getTimeHHMM()}/${from}: ${content}`;
    chatBox.appendChild(msgDiv);

    // 👇 Giới hạn chỉ giữ lại 20 tin nhắn mới nhất
    while (chatBox.children.length > 20) {
        chatBox.removeChild(chatBox.firstChild);
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}
