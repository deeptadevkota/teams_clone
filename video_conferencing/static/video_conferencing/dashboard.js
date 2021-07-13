//creating an endpoint for the websocket
let endpoint = 'wss://' + window.location.host + '/ws/dashboard/' + team_id + '/'
socket = new WebSocket(endpoint)

// listens to web socket
// if message arises then the function is invoked
socket.onmessage = function (e) {
    let dataMsg = JSON.parse(e.data)
    tmp = dataMsg.message
    for (let i = 0; i < tmp.length; i++) {
        // created a span element and appends the incoming message on it
        let app = document.querySelector('#scroll-object')
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
//function scrolls to the bottom of the chat box
const scrollToBottom = () => {
    let d = $('.scroll-div');
    d.scrollTop(d.prop("scrollHeight"));
}

//listens to the enter key on the text box
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.keyCode === 13) {
        document.querySelector('#chat-message-submit').click();
    }
};

//function to read the message and send it to the websocket 
document.querySelector('#chat-message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    let message = messageInputDom.value;
    message = username + " : " + message;
    // sending the message to the websocket
    socket.send(JSON.stringify({
        'message': message,
        'type': "msg"
    }));
    messageInputDom.value = '';
};

//function to enter the group dashboard by enter the group ID in the navigation bar text box
document.querySelector('#message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#message');
    const message = messageInputDom.value;
    messageInputDom.value = '';
    if (message != '')
        window.location.pathname = '/dashboard/' + message + '/'
};