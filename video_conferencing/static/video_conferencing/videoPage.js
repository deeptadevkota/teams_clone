// list to store the messages of the chat
let messages = [];

// list to store the user id of the videos already added
let videoalreadyadded = []
// object to store the connected peers
let conntetedpeers = new Object()

// end point of the websocket connection
let endpoint = 'wss://' + window.location.host + '/ws/' + team_id + '/'
//setting the audio and video to be true at the beginning of the meet
let mediaConstraints = {
    audio: true,
    video: true
};

// setting the global variables with initial values
let localStream = null;
let displayMediaStream = null
let screensharebool = false
let isMessageOpen = false
let firsttime = true
let ctx = null
let board = false
let plots = []
let drawing = false;

//function call to get the video stream of the user
getLocalStreamFunc()
socket = new WebSocket(endpoint)
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
    else if (data.type === "msg") {

        let tmp = data.message
        for (let i = 0; i < tmp.length; i++)
            messagecame(tmp[i])
    }
    else if (data.type === "whiteBoard") {
        drawOnCanvas(data.plots)
    }
}

//function to get the video stream of the user 
async function getLocalStreamFunc() {
    localStream = await navigator.mediaDevices.getUserMedia(mediaConstraints)
    //function call to add the obtained video stream to the browser
    addVideoStream(localStream, user_name)
}
/*
function invoked when a new user joins the video call room
creates a new peer connection and obtained the local streams
 */
async function invite(data) {
    targetUsername = data.name;
    createPeerConnection(targetUsername);
    myPeerConnection = conntetedpeers[targetUsername][0]
    localStream = await navigator.mediaDevices.getUserMedia(mediaConstraints)
    localStream.getTracks().forEach(track => myPeerConnection.addTrack(track, localStream));
}
/*
creates a new RTCpeer connection, when a user joins the call
 */
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

/*
this function takes the targetUsername and the event as the input
invoked when negotiation of the connection through the signaling channel is required.
*/
async function handleNegotiationNeededEvent(event, targetUsername) {
    myPeerConnection = conntetedpeers[targetUsername][0]
    await myPeerConnection.createOffer()
    await myPeerConnection.setLocalDescription();
    //send it video offer message to the target via websockets
    socket.send(JSON.stringify({
        "name": user_name,
        "target": targetUsername,
        "type": "video-offer",
        "sdp": myPeerConnection.localDescription
    }))
}

/*
This function takes the data obatined from the websocket as the input
It is invoked when a the message is answered from the the target user accepts the video offer
*/

async function handleAnswerMsg(msg) {
    let desc = new RTCSessionDescription(msg.sdp)
    myPeerConnection = conntetedpeers[msg.name][0]
    if (!!!desc)
        return
    await myPeerConnection.setRemoteDescription(desc)
    candidates = conntetedpeers[msg.name][1]
    candidates.forEach(candidate => myPeerConnection.addIceCandidate(candidate))
}
/*
This function takes the data obatined from the websocket as the input
It is invoked when a video offer message is made to the user
it adds the ICE candidate to the PeerConnection 
and in return a video answer message is send to the target
 */
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

/*
this function takes the targetUsername and the event as the input
This functions sends the contents of ICE candidates transmit using the signaling server.  
*/
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
/*
This adds thw new remote candidate to the RTCPeerConnection's remote description
which describes the state of the remote end of the connection.
 */
function handleNewICECandidateMsg(msg) {
    let candidate = new RTCIceCandidate(msg.candidate);
    candidates = conntetedpeers[msg.name][1]
    myPeerConnection = conntetedpeers[msg.name][0]
    if (!myPeerConnection || !myPeerConnection.remoteDescription)
        candidates.push(candidate)
    else
        myPeerConnection.addIceCandidate(candidate)
}
/*
this functions add the stream to the browser when a new Peer connection is made
 */
function handleRemoteStreamEvent(event, user_id) {
    addVideoStream(event.streams[0], user_id)
}
/*
this functions takes the user_id as the input 
it is invoked when a user leaves the meet or they when they stop sharing the screen
respective video elements are removed, and conntetedpeers object is also deleted
*/
function handleLeftMsg(msg) {
    document.getElementById(msg.name).remove()
    videoalreadyadded = videoalreadyadded.filter(i => i !== msg.name)
    delete conntetedpeers[msg.name]
    document.getElementById(msg.name + '$').remove()
    videoalreadyadded = videoalreadyadded.filter(i => i !== msg.name + '$')
    delete conntetedpeers[msg.name + '$']
}
/*
this function takes target user name as the input
this function is invoked when the target user shares the screen
it adds the stream to the PeerConnection
 */
async function inviteShare(targetUsername) {
    createPeerConnection(targetUsername);
    myPeerConnection = conntetedpeers[targetUsername][0]
    myPeerConnection.addTrack(displayMediaStream.getTracks()[0], displayMediaStream);
}
/*
this function is invoked when user wishes to share his/her screen
the user_name is concatenated with a dollor sign to mimiks the screen share stream as a new user stream
 */
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
/*
    this function is invoked when a new user joins the call 
    when a screen share is being shared by a an existing user
    it first handles the event when the just the video stream
    and then handles the event when the video and screen share
 */
async function videoAndScreen(data) {
    invite(data)
    setTimeout(function () {
        user_name = user_name + '$';
        inviteShare(data.name)
        setTimeout(function () { user_name = user_name.substring(0, user_name.length - 1) }, 2000);
    }, 2000);
}
/*
    function is invoked when a user stops sharing the screen
 */
function screenshareended() {
    screensharebool = false
    socket.send(JSON.stringify({
        "name": user_name + '$',
        "type": "screenShareLeft",
    }))
}

/*
    function removes the screen share stream when a user stops sharing the screen
 */
function handleleftscreenshare(msg) {
    videoalreadyadded = videoalreadyadded.filter(i => i !== msg.name)
    document.getElementById(msg.name).remove();
    delete conntetedpeers[msg.name];
}
/*
appends the message in the chat side bar in the browser
 */
messages.forEach(i => $("ul").append(`<li class="message">${i}</li>`));

/*
functions takes the user_id and the video stream as input
checks if the video stream of the user is already included or not, if not then
adds the stream to the browser 
*/
function addVideoStream(stream, user_id) {
    //checks if it stream is already added
    if (videoalreadyadded.includes(user_id)) {
        const video = document.getElementById(user_id)
        video.srcObject = stream
        video.addEventListener('loadedmetadata', () => {
            video.play()
        })
        return
    }
    //creates a new video element 
    const video = document.createElement('video')
    video.id = user_id
    //mutes the video sound of the user in his/her browser
    if (user_id === user_name)
        video.muted = true;
    const videoGrid = document.getElementById('video-grid')
    video.srcObject = stream
    video.addEventListener('loadedmetadata', () => {
        video.play()
    })
    videoGrid.append(video)
    //appends the user_id to the videoalreadyaddedlist
    videoalreadyadded = [...videoalreadyadded, user_id]
}

/*
invoked when white board button is clicked
if the the white board is already open it removes the canvas
if the white board is closed then it opens the canva
 */
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
/* 
this function takes input as the drawing context on the canvas
it sets the drawing variable as true and starts drawing
*/
function startDrawing(e) {
    drawing = true;
    draw(e);
}
/*
once the drawing is done, the plots list is emptied
 */
function finishDrawing() {
    drawing = false;
    plots = [];
}
/*
    this function takes input as the canva context
   and sends the coordinates via the web socket
 */
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
    // relationship bitmap vs. element for X
    scaleX = canvas.width / rect.width;
    scaleY = canvas.height / rect.height;
    plots.push({ x: (x - rect.left) * scaleX, y: (y - rect.top) * scaleY });
    //sending the coordinates via the websocket
    socket.send(JSON.stringify({
        "type": "whiteBoard",
        "plots": plots,
    }))
    drawOnCanvas(plots);
}
/*
    this function takes the plots as the input 
    and draws on the canva
 */
function drawOnCanvas(plots) {
    ctx.lineWidth = 1;
    ctx.lineCap = "round";
    ctx.beginPath();
    if (plots.length >= 2)
        ctx.moveTo(plots[plots.length - 2].x, plots[plots.length - 2].y);
    ctx.lineTo(plots[plots.length - 1].x, plots[plots.length - 1].y);
    ctx.stroke();
}
/*
this function toggles the side nav bar of the chat app
and send the chat messages via the websocket
 */
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
            let message = messageInputDom.value;
            message = user_name + " : " + message
            let msg = []
            msg.push(message)
            //chat message sent via the web socket
            socket.send(JSON.stringify({
                'message': msg,
                'type': "msg",
            }));
            messageInputDom.value = '';
        };
        firsttime = false;
    }

}


/* the obatined chat message is appended to the chat box */
function messagecame(message) {
    messages = [...messages, message];
    $("ul").append(`<li class="message">${message}</li>`);
    scrollToBottom()
}
/*
function to scroll to the bottom of the chat box
 */
const scrollToBottom = () => {
    var d = $('.main__chat_window');
    d.scrollTop(d.prop("scrollHeight"));
}
/*
function to set the mute and unmute button for the audio
 */
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
/*
function to block the video if the user wishes not to show video
 */
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
/*
this function ends the meet and redirects to the dashboard
 */
function endMeet() {
    window.location.pathname = '/dashboard/' + team_id + '/'
}
