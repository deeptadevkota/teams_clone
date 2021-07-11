let endpoint = 'wss://' + window.location.host + '/ws/dashboard/' + team_id + '/'
socket = new WebSocket(endpoint)

socket.onmessage = function (e) {
    let dataMsg = JSON.parse(e.data)
    tmp = dataMsg.message
    for (let i = 0; i < tmp.length; i++) {
        let app = document.querySelector('#chat-box')
        let li = document.createElement('span')
        li.textContent = tmp[i]
        li.classList.add('message');
        let new_div = document.createElement('div')
        new_div.className = "chat_div"
        new_div.append(li)
        app.append(new_div)
        scrollToBottom()
    }
}
const scrollToBottom = () => {
    let d = $('#chat-box');
    d.scrollTop(d.prop("scrollHeight"));
}
document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function (e) {        //storing the message and sending it in JSON format to the server
    const messageInputDom = document.querySelector('#chat-message-input');
    let message = messageInputDom.value;
    message = username + " : " + message;
    socket.send(JSON.stringify({
        'message': message,
        'type': "msg",
        'user_name': username
    }));
    messageInputDom.value = '';
};

document.querySelector('#message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#message');
    const message = messageInputDom.value;
    messageInputDom.value = '';
    if (message != '')
        window.location.pathname = '/' + message + '/' + username;
};