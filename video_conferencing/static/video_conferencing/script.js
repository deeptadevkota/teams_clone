let messages = [];
let localStream = null;
let videoalreadyadded = []
let conntetedpeers = new Object()
let displayMediaStream = null
let endpoint = 'ws://' + window.location.host + '/ws/' + room_id + '/' + user_name + '/'
let endpoint2 = 'ws://' + window.location.host + '/ws/dashboard/' + room_id + '/' + '15/'
let mediaConstraints = {
    audio: true,
    video: true
};
let screensharebool = false
let isMessageOpen = false
let firsttime = true
let ctx = null
let board = false
let plots = []
let drawing = false;
getLocalStreamFunc()
socket = new WebSocket(endpoint)
chatSocket = new WebSocket(endpoint2)

socket.onmessage = function (e) {
    let data = JSON.parse(e.data).obj
    if (data.type === "joined" && screensharebool == true) {
        videoAndScreen(data)
    }
    else if (data.type === "joined") {
        invite(data)
    }
    else if (data.type === "video-offer" && (data.target === user_name || data.target === user_name + '$')) {

        handleVideoOfferMsg(data)
    }
    else if (data.type === "new-ice-candidate" && (data.target === user_name || data.target === user_name + '$')) {
        handleNewICECandidateMsg(data)
    }
    else if (data.type === "video-answer" && (data.target === user_name || data.target === user_name + '$')) {
        handleAnswerMsg(data)
    }
    else if (data.type === "left") {
        handleLeftMsg(data)
    }
    else if (data.type === "screenShareLeft") {
        handleleftscreenshare(data);
    }
    else if (data.type === "whiteBoard") {
        drawOnCanvas(data.plots)
    }
}
chatSocket.onmessage = function (e) {
    let dataMsg = JSON.parse(e.data)
    tmp = dataMsg.message
    for (let i = 0; i < tmp.length; i++)
        messagecame(tmp[i], "user")
}
async function getLocalStreamFunc() {
    localStream = await navigator.mediaDevices.getUserMedia(mediaConstraints)
    addVideoStream(localStream, user_name)
}
async function invite(data) {
    targetUsername = data.name;
    createPeerConnection(targetUsername);
    myPeerConnection = conntetedpeers[targetUsername][0]
    localStream = await navigator.mediaDevices.getUserMedia(mediaConstraints)
    localStream.getTracks().forEach(track => myPeerConnection.addTrack(track, localStream));
}
function createPeerConnection(targetUsername) {
    myPeerConnection = new RTCPeerConnection({
        iceServers: [
            {
                urls: "stun:stun.l.google.com:19302"
            }
        ]
    });
    myPeerConnection.onicecandidate = tmpIcefunc = e => handleICECandidateEvent(e, targetUsername);
    myPeerConnection.onnegotiationneeded = tmpfunc = e => handleNegotiationNeededEvent(e, targetUsername);
    myPeerConnection.ontrack = tmpStreamfunc = e => handleRemoteStreamEvent(e, targetUsername);
    conntetedpeers[targetUsername] = [myPeerConnection, []]
    myPeerConnection = null
}
async function handleNegotiationNeededEvent(event, targetUsername) {
    myPeerConnection = conntetedpeers[targetUsername][0]
    await myPeerConnection.createOffer()
    await myPeerConnection.setLocalDescription();
    socket.send(JSON.stringify({
        "name": user_name,
        "target": targetUsername,
        "type": "video-offer",
        "sdp": myPeerConnection.localDescription
    }))
}
async function handleAnswerMsg(msg) {
    let desc = new RTCSessionDescription(msg.sdp)
    myPeerConnection = conntetedpeers[msg.name][0]
    if (!!!desc)
        return
    await myPeerConnection.setRemoteDescription(desc)
    candidates = conntetedpeers[msg.name][1]
    candidates.forEach(candidate => myPeerConnection.addIceCandidate(candidate))
}
async function handleVideoOfferMsg(msg) {
    targetUsername = msg.name;
    let desc = new RTCSessionDescription(msg.sdp);
    createPeerConnection(targetUsername);
    myPeerConnection = conntetedpeers[msg.name][0]
    await myPeerConnection.setRemoteDescription(desc)
    candidates = conntetedpeers[msg.name][1]
    candidates.forEach(candidate => myPeerConnection.addIceCandidate(candidate))
    stream = await navigator.mediaDevices.getUserMedia(mediaConstraints)
    localStream = stream;
    await localStream.getTracks().forEach(track => myPeerConnection.addTrack(track, localStream));
    myPeerConnection = conntetedpeers[msg.name][0]
    answer = await myPeerConnection.createAnswer();
    await myPeerConnection.setLocalDescription();
    socket.send(JSON.stringify({
        "name": user_name,
        "target": targetUsername,
        "type": "video-answer",
        "sdp": myPeerConnection.localDescription
    }))
}
function handleICECandidateEvent(event, targetUsername) {
    if (event.candidate) {
        socket.send(JSON.stringify({
            "type": "new-ice-candidate",
            "target": targetUsername,
            "name": user_name,
            "candidate": event.candidate
        }))
    }
}
function handleNewICECandidateMsg(msg) {
    let candidate = new RTCIceCandidate(msg.candidate);
    candidates = conntetedpeers[msg.name][1]
    myPeerConnection = conntetedpeers[msg.name][0]
    if (!myPeerConnection || !myPeerConnection.remoteDescription)
        candidates.push(candidate)
    else
        myPeerConnection.addIceCandidate(candidate)
}
function handleRemoteStreamEvent(event, user_id) {
    addVideoStream(event.streams[0], user_id)
}
function handleLeftMsg(msg) {
    document.getElementById(msg.name).remove()
    videoalreadyadded = videoalreadyadded.filter(i => i !== msg.name)
    delete conntetedpeers[msg.name]
    document.getElementById(msg.name + '$').remove()
    videoalreadyadded = videoalreadyadded.filter(i => i !== msg.name + '$')
    delete conntetedpeers[msg.name + '$']
}
async function inviteShare(targetUsername) {
    createPeerConnection(targetUsername);
    myPeerConnection = conntetedpeers[targetUsername][0]
    myPeerConnection.addTrack(displayMediaStream.getTracks()[0], displayMediaStream);
}
async function shareScreen() {
    user_name = user_name + "$"
    screensharebool = true
    displayMediaStream = await navigator.mediaDevices.getDisplayMedia();
    addVideoStream(displayMediaStream, user_name)
    for (let key in conntetedpeers) {
        inviteShare(key);
    }
    setTimeout(function () { user_name = user_name.substring(0, user_name.length - 1) }, 2000);
    displayMediaStream.getVideoTracks()[0].onended = screenshareended
}
async function videoAndScreen(data) {
    invite(data)
    setTimeout(function () {
        user_name = user_name + '$';
        inviteShare(data.name)
        setTimeout(function () { user_name = user_name.substring(0, user_name.length - 1) }, 2000);
    }, 2000);
}
function screenshareended() {
    screensharebool = false
    socket.send(JSON.stringify({
        "name": user_name + '$',
        "type": "screenShareLeft",
    }))
}
function handleleftscreenshare(msg) {
    videoalreadyadded = videoalreadyadded.filter(i => i !== msg.name)
    document.getElementById(msg.name).remove();
    delete conntetedpeers[msg.name];
}
function addVideoStream(stream, user_id) {
    if (videoalreadyadded.includes(user_id)) {
        const video = document.getElementById(user_id)
        video.srcObject = stream
        video.addEventListener('loadedmetadata', () => {
            video.play()
        })
        return
    }
    const video = document.createElement('video')
    video.id = user_id
    if (user_id === user_name)
        video.muted = true;
    const videoGrid = document.getElementById('video-grid')
    video.srcObject = stream
    video.addEventListener('loadedmetadata', () => {
        video.play()
    })
    videoGrid.append(video)
    videoalreadyadded = [...videoalreadyadded, user_id]
}
messages.forEach(i => $("ul").append(`<li class="message">${i}</li>`));
function whiteBoard() {
    if (board == false) {
        const canvas = document.createElement('canvas');
        canvas.id = 'canvas';
        const videoGrid = document.getElementById('video-grid');
        videoGrid.append(canvas);
        board = true;
        ctx = canvas.getContext('2d');
        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mouseup', finishDrawing);
        canvas.addEventListener('mousemove', draw);
    }
    else {
        document.getElementById('canvas').remove();
        board = false;
    }
}

function startDrawing(e) {
    drawing = true;
    draw(e);
}

function finishDrawing() {
    drawing = false;
    plots = [];
}

function draw(e) {
    if (drawing == false)
        return;
    let x = e.clientX, y = e.clientY;
    let z = null;
    if (plots.length >= 1)
        z = plots[plots.length - 1];
    plots = [];
    plots.push(z);
    var rect = canvas.getBoundingClientRect();
    scaleX = canvas.width / rect.width;   // relationship bitmap vs. element for X
    scaleY = canvas.height / rect.height;
    plots.push({ x: (x - rect.left) * scaleX, y: (y - rect.top) * scaleY });
    socket.send(JSON.stringify({
        "type": "whiteBoard",
        "plots": plots,
    }))
    drawOnCanvas(plots);
}

function drawOnCanvas(plots) {
    ctx.lineWidth = 1;
    ctx.lineCap = "round";
    ctx.beginPath();
    if (plots.length >= 2)
        ctx.moveTo(plots[plots.length - 2].x, plots[plots.length - 2].y);
    ctx.lineTo(plots[plots.length - 1].x, plots[plots.length - 1].y);
    ctx.stroke();
}
function toggleNav() {
    if (isMessageOpen == false) {
        document.getElementById("mySidepanel").style.width = "25vw";
        document.getElementById("main-window").style.width = "75vw";
        isMessageOpen = true;
    }
    else {
        document.getElementById("mySidepanel").style.width = "0";
        document.getElementById("main-window").style.width = "100vw";
        isMessageOpen = false;
    }

    if (firsttime) {

        document.querySelector('#chat-message-input').onkeyup = function (e) {
            if (e.keyCode === 13) {
                document.querySelector('#chat-message-submit').click();
            }
        };

        document.querySelector('#chat-message-submit').onclick = function (e) {
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value;
            console.log(message);
            chatSocket.send(JSON.stringify({
                'message': message,
                'type': "msg",
                'user_name': user_name,
            }));
            messageInputDom.value = '';
        };
        firsttime = false;
    }

}



function messagecame(message, name) {
    message = name + " : " + message;
    messages = [...messages, message];
    // if (x.style.display === "block")
    //     document.querySelector('#chat-log').value += (message + '\n');
    $("ul").append(`<li class="message">${message}</li>`);
    scrollToBottom()
}
const scrollToBottom = () => {
    var d = $('.main__chat_window');
    d.scrollTop(d.prop("scrollHeight"));
}
function muteUnmute() {
    var enabled = localStream.getAudioTracks()[0].enabled;
    if (enabled) {
        localStream.getAudioTracks()[0].enabled = false;
        setUnmuteButton();
    }
    else {
        setMuteButton();
        localStream.getAudioTracks()[0].enabled = true;
        // document.getElementById(user_name).srcObject.getAudioTracks()[0].enabled = true;
    }
}
function playStop() {
    var enabled = localStream.getVideoTracks()[0].enabled;
    if (enabled) {
        localStream.getVideoTracks()[0].enabled = false;
        document.getElementById(user_name).srcObject.getVideoTracks()[0].enabled = false;
        setPlayVideo()
    }
    else {
        setStopVideo()
        localStream.getVideoTracks()[0].enabled = true;
        document.getElementById(user_name).srcObject.getVideoTracks()[0].enabled = true;
    }
}
function setMuteButton() {
    const html = `<button onclick="muteUnmute()"><i class="fas fa-microphone"></i></button>`
    document.querySelector('.main__mute_button').innerHTML = html;
}
function setUnmuteButton() {
    const html = `<button class="btn-sec" onclick="muteUnmute()"><i class="fas fa-microphone-slash"></i></button>`
    document.querySelector('.main__mute_button').innerHTML = html;
}
function setStopVideo() {
    const html = `<button onclick="playStop()"><i class="fas fa-video"></i></button>`
    document.querySelector('.main__video_button').innerHTML = html;
}
function setPlayVideo() {
    const html = `<button class="btn-sec" onclick="playStop()"><i class="fas fa-video-slash"></i></button>`
    document.querySelector('.main__video_button').innerHTML = html;
}
