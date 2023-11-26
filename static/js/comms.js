// For the collapsable mobile navbar -------------------

const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('collapsable-menu');

navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('menu-collapsed')
});

// -------------------------- Functions that don't reference the chatsocket -------------------------- //

function escapeHtml(text) {
    var map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function removeAllItems(arr, value) {
    var i = 0;
    while (i < arr.length) {
      if (arr[i] === value) {
        arr.splice(i, 1);
      } else {
        ++i;
      }
    }
    return arr
}

function removeAllItems2D(arr, value) {
    var i = 0;
    while (i < arr.length) {
      if (arr[i][0] === value) {
        arr.splice(i, 1);
      } else {
        ++i;
      }
    }
    return arr
}

function jumpToBottom() {
    const chat = document.getElementById('chat')

    chat.scrollTo(0, chat.scrollHeight);
};

function replaceMentions(messageContentRaw, mentionDataString) {

    let messageContent = messageContentRaw

    const mentionArray = mentionDataString.split(',')

    mentionArray.pop()

    mentionDict = {}

    mentionArray.forEach(function(item, index) {
        if(index % 2 === 0) {
           mentionDict[item] = mentionArray[index + 1];
        }
    });

    for (const [key, value] of Object.entries(mentionDict)) {
        const displayName = key
        const color = value

        const mentionHTMl = `<span class="color-${color}">@${displayName}</span>`

        messageContent = messageContent.replaceAll(`@${displayName}`, mentionHTMl)
    }

    return messageContent
}

// -------------------------- Connect Function Globals -------------------------- //

let reconnecting = false

// -------------------------- Connect Function -------------------------- //

function connect(){

    // -------------------------- Voting System -------------------------- //

    if (document.querySelector('#Y')) {
        document.querySelector('#Y').onclick = function(e) {
            if (document.querySelector('input[name="puppet"]:checked')){
                const puppet = document.querySelector('input[name="puppet"]:checked').value;
    
                chatSocket.send(JSON.stringify({
                    'voting' : 'Y',
                    'puppet' : puppet
                }));
            } else {
                chatSocket.send(JSON.stringify({
                    'voting' : 'Y',
                }));
            }
        };
    
        document.querySelector('#N').onclick = function(e) {
            if (document.querySelector('input[name="puppet"]:checked')){
                const puppet = document.querySelector('input[name="puppet"]:checked').value;
    
                chatSocket.send(JSON.stringify({
                    'voting' : 'N',
                    'puppet' : puppet
                }));
            } else {
                chatSocket.send(JSON.stringify({
                    'voting' : 'N',
                }));
            }
        };
    
        document.querySelector('#mobile-Y').onclick = function(e) {
            if (document.querySelector('input[name="puppet"]:checked')){
                const puppet = document.querySelector('input[name="puppet"]:checked').value;
    
                chatSocket.send(JSON.stringify({
                    'voting' : 'Y',
                    'puppet' : puppet
                }));
            } else {
                chatSocket.send(JSON.stringify({
                    'voting' : 'Y',
                }));
            }
        };
    
        document.querySelector('#mobile-N').onclick = function(e) {
            if (document.querySelector('input[name="puppet"]:checked')){
                const puppet = document.querySelector('input[name="puppet"]:checked').value;
    
                chatSocket.send(JSON.stringify({
                    'voting' : 'N',
                    'puppet' : puppet
                }));
            } else {
                chatSocket.send(JSON.stringify({
                    'voting' : 'N',
                }));
            }
        };
    }


    // -------------------------- Chat Startup -------------------------- //

    const postCode = JSON.parse(document.getElementById('post-code').textContent);

    const chatInput = document.getElementById('chat-input')

    var loc = window.location
    var wsProtocol = 'ws://'
    if (loc.protocol == "https:"){
        wsProtocol = 'wss://'
    }

    const chatSocket = new WebSocket (
        wsProtocol
        + window.location.host
        + '/ws/'
        + postCode
        + '/'
        + 'chat'
    );

    chatSocket.onopen = function() {
        
        const disconnectAlertDOM = document.getElementById('disconnect-alert');
        if (disconnectAlertDOM) {
            disconnectAlertDOM.classList.add('hidden');

            document.getElementById('disconnect-alert-text').innerText = "Reconnect";
        }

        chatSocket.send(JSON.stringify({
            'ping' : 'initial',
        }));

        if (reconnecting) {

            reconnecting = false

            let lastMessageId = document.getElementById('messages-container').lastElementChild.firstElementChild.firstElementChild.lastElementChild.id

            chatSocket.send(JSON.stringify({
                'reconnecting' : 'true',
                'last_message_id' : lastMessageId,
            }));
        }
    }

    // -------------------------- Pingster Functionality -------------------------- //

    const pingReading = document.getElementById('ping-reading');

    const pingReadingMobile = document.getElementById('ping-reading-mobile')

    if (pingReading) {
        var performanceIntervalPing = window.setInterval(function(){
            window.start = performance.now();
            chatSocket.send(JSON.stringify({
                'ping' : 'performance',
            }));
        }, 200);
    }



    // -------------------------- Online List Functionality -------------------------- //

    const onlineReading = document.getElementById('online-reading')
    const onlineReadingMobile = document.getElementById('online-reading-mobile')


    if (onlineReading) {
        var onlineIntervalPing = window.setInterval(function(){
            chatSocket.send(JSON.stringify({
                'online_status' : 'online',
                'online_timestamp' : Date.now(),
            }));
        }, 1000);
    }
    
    // -------------------------- Functions used in onmessage -------------------------- //

    function updateIsTyping() {
        const typingIndicator = document.getElementById('typing-indicator')
    
        if (typers.length > 0) {
    
            indicatorContent = ''
    
            if (typers.length == 1) {
                
                indicatorContent = `${typers[0]} is typing...`
    
            } else {
    
                for (let i = 0; i < typers.length; i++) {
                    if (i == 0) {
                        indicatorContent = typers[i]
                    } else if ((i + 1) == typers.length) {
                        indicatorContent += ` and ${typers[i]} are typing...`
                    } else {
                        indicatorContent += `, ${typers[i]}`
                    }
                }
    
            }
    
            typingIndicator.innerHTML = indicatorContent
            // typingIndicator.classList.remove('hidden')
        } else {
            typingIndicator.innerHTML = ''
            // typingIndicator.classList.add('hidden')
        }
    }

    function doneTyping () {
        if (document.querySelector('input[name="puppet"]:checked')){
            const puppet = document.querySelector('input[name="puppet"]:checked').value;
            chatSocket.send(JSON.stringify({
                'typing_status' : 'stopped',
                'puppet' : puppet
            }))
           timerIsOn = false
        } else {
            chatSocket.send(JSON.stringify({
                'typing_status' : 'stopped',
            }))
           timerIsOn = false
        }
    }

    function updateOnlineReading() {
    
        if (onlineUsers) {
            onlineReading.innerText = onlineUsers.length
            onlineReadingMobile.innerText = onlineUsers.length
        }
    }
    // -------------------------- Chatsocket Methods -------------------------- //
    
    chatSocket.onmessage = function(e) {

        const data = JSON.parse(e.data);

        if ('message' in data && 'author' in data) {
            const chat = document.getElementById('chat')
            const message_container = document.getElementById('messages-container')

            const message_id = 'msg_' + data.message_code

            if (data.origin == 'native') {

                if (data.is_walker == "True") {

                    message_container.insertAdjacentHTML("beforeend", `<div class="message VIPmessage"><div class="message-body"><div class="text"><div class="author"><span class="author-shadow-${data.author_color}"></span></div><div class="content editable" id="${message_id}"><span class="message-tag color-${data.author_color}">{</span><div class="actual-content-wrapper"><span class="message-actual-content editable-content" contenteditable="plaintext-only" contenteditable="true" enterkeyhint="send"></span></div><span class="message-tag color-${data.author_color}">}</span><sup>0</sup></div></div></div></div>`);
                
                } else {

                    message_container.insertAdjacentHTML("beforeend", `<div class="message"><div class="message-body"><div class="text"><div class="author"><span class="author-shadow-${data.author_color}"></span></div><div class="content editable" id="${message_id}"><span class="message-tag color-${data.author_color}">{</span><div class="actual-content-wrapper"><span class="message-actual-content editable-content" contenteditable="plaintext-only" contenteditable="true" enterkeyhint="send"></span></div><span class="message-tag color-${data.author_color}">}</span><sup>0</sup></div></div></div></div>`);

                }
                
                message_container.lastElementChild.firstElementChild.firstElementChild.lastElementChild.querySelector('.message-actual-content').addEventListener("keypress", function(e) {
                    if (e.key === 'Enter' && !e.shiftKey && !matchMedia('only screen and (max-width: 960px)').matches) {
                        e.preventDefault();
                        e.target.blur()
                    }
                })

            } else if (data.origin == 'foreign') {

                if (data.is_walker == "True") {

                    message_container.insertAdjacentHTML("beforeend", `<div class="message VIPmessage"><div class="message-body"><div class="text"><div class="author"><span class="author-shadow-${data.author_color}"></span></div><div class="content" id="${message_id}"><span class="message-tag leading-tag dislikable-excited color-${data.author_color}">{</span><div class="actual-content-wrapper"><span class="message-actual-content"></span></div><span class="message-tag trailing-tag likable-excited color-${data.author_color}">}</span><sup>0</sup></div></div></div></div>`);

                } else {

                    message_container.insertAdjacentHTML("beforeend", `<div class="message"><div class="message-body"><div class="text"><div class="author"><span class="author-shadow-${data.author_color}"></span></div><div class="content" id="${message_id}"><span class="message-tag leading-tag dislikable-excited color-${data.author_color}">{</span><div class="actual-content-wrapper"><span class="message-actual-content"></span></div><span class="message-tag trailing-tag likable-excited color-${data.author_color}">}</span><sup>0</sup></div></div></div></div>`);

                }
                
                message_container.lastElementChild.firstElementChild.firstElementChild.lastElementChild.querySelector('.message-actual-content').addEventListener("keypress", function(e) {
                    if (e.key === 'Enter' && !e.shiftKey && !matchMedia('only screen and (max-width: 960px)').matches) {
                        e.preventDefault();
                        e.target.blur()
                    }
                })

            }

            const authorDiv = document.getElementById(message_id).parentNode.firstElementChild

            authorDiv.firstElementChild.addEventListener("click", function(e) {

                const chatInput = document.getElementById('chat-input')
    
                chatInput.innerText += `@${authorDiv.firstElementChild.innerText}`
            })

            if ('mention_data_string' in data && data.mention_data_string) {

                message_container.lastElementChild.firstElementChild.firstElementChild.lastElementChild.querySelector('.message-actual-content').innerHTML = replaceMentions(escapeHtml(data.message), data.mention_data_string); // The message content

            } else {

                message_container.lastElementChild.firstElementChild.firstElementChild.lastElementChild.querySelector('.message-actual-content').innerText = data.message; // The message content

            }

            if (chat.scrollTop != 0) {
                document.getElementById('new-messages-alert').classList.remove('hidden');
            } else {
                document.getElementById('new-messages-alert').classList.add('hidden');
            }

            // Clear typing
            userSpan = `<span>${data.author}</span>`
            // userSpan = `<span  class="color-${data.author_color}">${data.author}</span>`
            removeAllItems(typers, userSpan);
            updateIsTyping();
            
            notifSound.volume = 0.5 
            notifSound.play();


        } else if ('message_id' in data && 'state' in data) {

            id = data.message_id
            if (data.state === 'disliked') {

                document.getElementById(id).lastElementChild.classList.remove('liked')
                document.getElementById(id).lastElementChild.classList.add('disliked')

            } else if (data.state === 'liked') {

                document.getElementById(id).lastElementChild.classList.remove('disliked')
                document.getElementById(id).lastElementChild.classList.add('liked')

            }

        } else if ('message_id' in data && 'action' in data) {
            if (data.action === 'like') {
                id = data.message_id

                const superScore = document.getElementById(id).lastElementChild // Superscript Score
                superScore.innerText = parseInt(superScore.innerText) + parseInt(data.changeBy)

                superScore.classList.remove('disliked')
                superScore.classList.add('liked')

            } else if (data.action === 'unlike') {
                id = data.message_id

                const superScore = document.getElementById(id).lastElementChild // Superscript Score
                superScore.innerText = parseInt(superScore.innerText) - parseInt(data.changeBy)

                superScore.classList.remove('disliked')
                superScore.classList.remove('liked')

            } else if (data.action === 'dislike') {
                id = data.message_id

                const superScore = document.getElementById(id).lastElementChild // Superscript Score
                superScore.innerText = parseInt(superScore.innerText) - parseInt(data.changeBy)

                superScore.classList.remove('liked')
                superScore.classList.add('disliked')

            } else if (data.action == 'undislike') {
                id = data.message_id

                const superScore = document.getElementById(id).lastElementChild // Superscript Score
                superScore.innerText = parseInt(superScore.innerText) + parseInt(data.changeBy)

                superScore.classList.remove('liked')
                superScore.classList.remove('disliked')
            }

        } else if ('interaction' in data) { // An interaction here is defined as someone else interacting with a message.
            id = data.message_id

            if (data.interaction === 'like') {

                const messageDOM = document.getElementById(id)
                message_scoreDOM = messageDOM.lastElementChild
                message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) + parseInt(data.changeBy)

            } else if (data.interaction === 'unlike') {

                const messageDOM = document.getElementById(id)
                message_scoreDOM = messageDOM.lastElementChild
                message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) - parseInt(data.changeBy)
            } else if (data.interaction == 'dislike') {
                
                const messageDOM = document.getElementById(id)
                message_scoreDOM = messageDOM.lastElementChild
                message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) - parseInt(data.changeBy)
            } else if (data.interaction == 'undislike') {
                
                const messageDOM = document.getElementById(id)
                message_scoreDOM = messageDOM.lastElementChild
                message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) + parseInt(data.changeBy)
            }
        } else if ('edited_content' in data) {

            message_id = 'msg_' + data.message_code

            if ('mention_data_string' in data && data.mention_data_string) {

                document.getElementById(message_id).querySelector('.message-actual-content').innerHTML = replaceMentions(escapeHtml(data.edited_content), data.mention_data_string);

            } else {

                document.getElementById(message_id).querySelector('.message-actual-content').textContent = data.edited_content

            }

        } else if ('switch' in data) {
            
            const messageContent = document.getElementById(data.message_id)

            if (data.switch == 'native') {

                messageContent.classList.remove('neutral')
                messageContent.classList.add('editable')

                messageContent.firstElementChild.classList.remove('leading-tag')
                messageContent.firstElementChild.classList.remove('dislikable-excited')

                messageContent.querySelector('.message-actual-content').classList.add('editable-content')
                messageContent.querySelector('.message-actual-content').contentEditable = "plaintext-only";
                messageContent.querySelector('.message-actual-content').setAttribute("enterkeyhint", "edit");

                // Can't use the lastElementChild selector because it's not the last element, the super score is.
                messageContent.children[2].classList.remove('trailing-tag') 
                messageContent.children[2].classList.remove('likable-excited')



            } else if (data.switch == 'foreign') {

                messageContent.classList.add('neutral')
                messageContent.classList.remove('editable')

                messageContent.firstElementChild.classList.add('leading-tag')
                messageContent.firstElementChild.classList.add('dislikable-excited')

                messageContent.querySelector('.message-actual-content').classList.remove('editable-content')
                messageContent.querySelector('.message-actual-content').removeAttribute("contenteditable")
                messageContent.querySelector('.message-actual-content').removeAttribute("enterkeyhint");

                // Can't use the lastElementChild selector because it's not the last element, the super score is.
                messageContent.children[2].classList.add('trailing-tag') 
                messageContent.children[2].classList.add('likable-excited')

            }
            

        } else if ('y_votes' in data || 'n_votes' in data) {

            document.getElementById('Y').firstElementChild.innerText = 'yes=' + data.y_votes
            document.getElementById('N').firstElementChild.innerText = 'no=' + data.n_votes

            document.getElementById('mobile-Y').innerText = 'yes=' + data.y_votes
            document.getElementById('mobile-N').innerText = 'no=' + data.n_votes

        } else if ('alert' in data) {
            if (data.alert == 'command_success') {
                const message_container = document.getElementById('messages-container')

                message_text = data.message

                message_container.innerHTML += `<div class="message command-border"><div class="message-body"><div class="text"><div class="content neutral"><span></span><span class="message-actual-content command-text">&lt;${message_text}&gt;</span></div></div></div></div>`
            } else if (data.alert == 'message_failure') {
                const message_container = document.getElementById('messages-container')

                message_text = data.message

                message_container.innerHTML += `<div class="message command-border"><div class="message-body"><div class="text"><div class="content neutral"><span></span><span class="message-actual-content command-text">&lt;${message_text}&gt;</span></div></div></div></div>`
            }
        } else if ('redirect' in data) {

            window.location.replace(data.redirect)

        } else if ('typing_user' in data && 'typing_status' in data) {

            // Before: const typingUserSpan = `<span class="color-${data.typing_color}">${data.typing_user}</span>`

            const typingUserSpan = `<span>${data.typing_user}</span>`

            var typingDwellingTimer;

            if (data.typing_status == 'started') {

                removeAllItems(typers, typingUserSpan);

                typers.push(typingUserSpan)

                clearTimeout(typingDwellingTimer);
                typingDwellingTimer = setTimeout(function() { 
                    removeAllItems(typers, typingUserSpan);
                    updateIsTyping(); 
                }, 60000);

            } else if (data.typing_status == 'stopped') {

                removeAllItems(typers, typingUserSpan);

            } 

            updateIsTyping();

        } else if ('pong' in data) {

            pingReading.innerText = Math.round(performance.now() - start) + 'ms'
            pingReadingMobile.innerText = Math.round(performance.now() - start) + 'ms'

        } else if ('online_status' in data) {

            const onlineUserSpan = [`<span class="online-user online-user-color-{{${data.online_color}}}}"><div class="online-beacon"></div><h1>{{${data.online_user}}}</h1></span>`, data.online_timestamp]

            if (data.online_status == 'online') {

                removeAllItems2D(onlineUsers, onlineUserSpan[0]);

                onlineUsers.push(onlineUserSpan);

                for (let i = 0; i < onlineUsers.length; i++) {
                    if ((Date.now() - onlineUsers[i][1]) >= 10000) {
                        removeAllItems2D(onlineUsers, onlineUsers[i][0]);
                    }
                }

            }

            updateOnlineReading();

        } else if ('contrib_user' in data) {
            contrib_users = document.getElementById('contrib-users-list')

            contrib_users.innerHTML += `<span class="contrib-user contrib-user-color-${data.contrib_color}"><div class="online-beacon"></div><h1>${data.contrib_user}</h1></span>`
        }
    };

    chatSocket.onclose = function(e) {
        document.getElementById('disconnect-alert').classList.remove('hidden');
        doneTyping()

        clearInterval(performanceIntervalPing)

        const expressions = ['(o_O) ?', '(((; ఠ ਉ ఠ))', '( Ŏ艸Ŏ)', '(｢ ⊙Д⊙)｢', '(☉_ ☉)', '( •́ ⍨ •̀)', '(ↁ_ↁ)']

        pingReading.innerText = expressions[Math.floor(Math.random()*expressions.length)];
        pingReadingMobile.innerText = expressions[Math.floor(Math.random()*expressions.length)];
    };

    // -------------------------- Chat Bar Events -------------------------- //

    if (chatInput) {
        
        mainRegion.bind(chatInput, 'pan', function(e){
            if (matchMedia('only screen and (max-width: 960px)').matches){
                chatInput.style.background = `linear-gradient(0deg, #000 ${(e.detail.data[0].distanceFromOrigin)}%, #fd4556 ${(e.detail.data[0].distanceFromOrigin)}%)`
            }
        });

        chatInput.onkeydown = function(e) {
            if (e.key === 'Enter' && !e.shiftKey && !matchMedia('only screen and (max-width: 960px)').matches) {
                e.preventDefault();
            }
        };

        var onlineUsers = ['john doe', 'jane doe']

        var typers = []

        var typingTimer; //timer identifier
        var doneTypingInterval = 3000; //time in ms
        var timerIsOn

        chatInput.onkeyup = function(e) {
            if (e.key == 'Enter' && !e.shiftKey && !matchMedia('only screen and (max-width: 960px)').matches) {
                sendMessage();
            }


            if (document.querySelector('input[name="puppet"]:checked')){
                if (!timerIsOn) {

                    const puppet = document.querySelector('input[name="puppet"]:checked').value;
                    
                    chatSocket.send(JSON.stringify({
                        'typing_status' : 'started',
                        'puppet' : puppet
                    }))

                }
            } else {
                if (!timerIsOn) {

                    chatSocket.send(JSON.stringify({
                        'typing_status' : 'started',
                    }))

                }
            }

            clearTimeout(typingTimer);
            if (document.querySelector('input[name="puppet"]:checked')){

                doneTypingInterval = 1000
                typingTimer = setTimeout(doneTyping, doneTypingInterval);

            } else {

                typingTimer = setTimeout(doneTyping, doneTypingInterval);

            }
            timerIsOn = true
        }

        chatInput.addEventListener('paste', function(e) {
            // cancel paste
            e.preventDefault();

            // get text representation of clipboard
            var text = (e.originalEvent || e).clipboardData.getData('text/plain');

            // insert text manually
            document.execCommand("insertHTML", false, text);
        });

        // Sends message and clears chat bar
        function sendMessage() {
            const messageInputDom = chatInput;
            const message = messageInputDom.innerText;

            if (message != '') {

                if (document.querySelector('input[name="puppet"]:checked')){

                    const puppet = document.querySelector('input[name="puppet"]:checked').value;

                    chatSocket.send(JSON.stringify({
                        'message' : message,
                        'puppet' : puppet
                    }));
                    messageInputDom.textContent = '';

                } else {

                    chatSocket.send(JSON.stringify({
                        'message' : message,
                    }));
                    messageInputDom.textContent = '';
                }
            };
        };

        let touchstartY = 0
        let touchendY = 0
            
        function checkDirection() {
            if (touchendY < touchstartY) { // Swiped up
                sendMessage();
            }
        }

        chatInput.addEventListener('touchstart', e => {
            if (matchMedia('only screen and (max-width: 960px)').matches){
                touchstartY = e.changedTouches[0].screenY
            }
        })

        chatInput.addEventListener('touchend', e => {
            if (matchMedia('only screen and (max-width: 960px)').matches){
                touchendY = e.changedTouches[0].screenY
                chatInput.style.background = `linear-gradient(0deg, #000 0%, #fd4556 0%)`
                checkDirection()
            }
        })
    }

    // -------------------------- General Mouseover Events -------------------------- //

    document.addEventListener("mouseover", function(e) {
        if (e.target.id.startsWith('msg_')) {
            if (document.querySelector('input[name="puppet"]:checked')){

                const puppet = document.querySelector('input[name="puppet"]:checked').value;

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.id,
                    'target' : 'message',
                    'trigger' : 'hover',
                    'puppet' : puppet
                }))
                
            } else {

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.id,
                    'target' : 'message',
                    'trigger' : 'hover'
                }))

            }
        }
    })

    // -------------------------- General Mouseclick Events -------------------------- //

    document.addEventListener("click", function(e) {
        classNames = e.target.className.toString().split(' ')
        if (classNames.includes('message-tag') && classNames.includes('trailing-tag')) {
            if (document.querySelector('input[name="puppet"]:checked')){

                const puppet = document.querySelector('input[name="puppet"]:checked').value;

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'target' : 'tag',
                    'trigger' : 'click',
                    'attempt' : 'like',
                    'puppet' : puppet
                }))

            } else {

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'target' : 'tag',
                    'trigger' : 'click',
                    'attempt' : 'like'
                }))

            }
        } else if (classNames.includes('message-tag') && classNames.includes('leading-tag')) {
            if (document.querySelector('input[name="puppet"]:checked')){

                const puppet = document.querySelector('input[name="puppet"]:checked').value;

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'target' : 'tag',
                    'trigger' : 'click',
                    'attempt' : 'dislike',
                    'puppet' : puppet
                }))

            } else {

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'target' : 'tag',
                    'trigger' : 'click',
                    'attempt' : 'dislike'
                }))
                
            }
        } else if (classNames.includes('editable-content')) {

            const messageActualContent = e.target

            //messageActualContent.focus()

        }

        if (classNames.includes('message-actual-content')) {

            if (document.querySelector('input[name="puppet"]:checked')){

                const puppet = document.querySelector('input[name="puppet"]:checked').value;

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'target' : 'message',
                    'trigger' : 'hover',
                    'puppet' : puppet
                }))
                
            } else {

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'target' : 'message',
                    'trigger' : 'hover'
                }))

            }
        }
    })

    // -------------------------- Focusout Events -------------------------- //

    document.addEventListener("focusout", function(e) {
        if (e.target.className.toString().split(' ').includes('message-actual-content')) {
            if (document.querySelector('input[name="puppet"]:checked')){

                const puppet = document.querySelector('input[name="puppet"]:checked').value;

                messageId = e.target.parentElement.id
                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.parentElement.id,
                    'edit' : e.target.textContent,
                    'puppet' : puppet
                }))
            } else {

                messageId = e.target.parentElement.id
                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.parentElement.parentElement.id,
                    'edit' : e.target.textContent,
                }))
            }
        }
    });

    // -------------------------- Events for each .message-actual-content -------------------------- //

    document.querySelectorAll('.message-actual-content').forEach(content =>

        content.addEventListener("paste", function(e) {
            // cancel paste
            e.preventDefault();

            // get text representation of clipboard
            var text = (e.originalEvent || e).clipboardData.getData('text/plain');

            // insert text manually
            document.execCommand("insertHTML", false, text);
        })
    )

    document.querySelectorAll('.message-actual-content').forEach(content =>
        content.addEventListener("keypress", function(e) {
            if (e.key === 'Enter' && !e.shiftKey && !matchMedia('only screen and (max-width: 960px)').matches) {
                e.preventDefault();
                e.target.blur()
            }
        })
    )

    // -------------------------- Events for each .author -------------------------- //

    document.querySelectorAll('.author').forEach(content =>

        content.firstElementChild.addEventListener("click", function(e) {

            const chatInput = document.getElementById('chat-input')

            chatInput.innerText += `@${content.firstElementChild.innerText}`
        })
    )

    // -------------------------- Scroll Functionality -------------------------- //

    var timer; 
    const chatDOM = document.getElementById('chat')
    if (chatDOM) {
        chatDOM.addEventListener('scroll', event => {

            clearTimeout(timer);
            timer = setTimeout(() => {
                const {scrollTop} = event.target;
                if (Math.abs(scrollTop) < 10) {
                    document.getElementById('new-messages-alert').classList.add('hidden');
                };
            }, 250)

        });
    }

    const newMessagesAlertDOM = document.getElementById('new-messages-alert');
    if (newMessagesAlertDOM) {
        newMessagesAlertDOM.onclick = function(){
            jumpToBottom()
        };
    };

    const disconnectAlertDOM = document.getElementById('disconnect-alert');
    if (disconnectAlertDOM) {
        disconnectAlertDOM.onclick = function(){
            document.getElementById('disconnect-alert-text').innerText = "Connecting...";

            console.log(document.getElementById('disconnect-alert-text').parentElement.lastElementChild)

            document.getElementById('disconnect-alert-text').parentElement.lastElementChild.classList.add('hidden')

            reconnecting = true;

            connect();
        };
    };

};

// -------------------------- Starting the Connection -------------------------- //

connect();