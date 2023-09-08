// For the collapsable mobile navbar -------------------

const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('collapsable-menu');

navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('menu-collapsed')
});

// -------------------------- Functions -------------------------- //

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

function jumpToBottom() {
    const chat = document.getElementById('chat')

    chat.scrollTo(0, chat.scrollHeight);
};

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


    // Typing function

    function updateTyping() {
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
                typingIndicator.classList.remove('hidden')
            } else {
                typingIndicator.innerHTML = ''
                typingIndicator.classList.add('hidden')
            }
    }


    // For the chat -----------------------

    const postCode = JSON.parse(document.getElementById('post-code').textContent);

    const chatInput = document.getElementById('chat-input')

    const chatSocket = new WebSocket (
        'wss://'
        + window.location.host
        + '/ws/'
        + postCode
        + '/'
        + 'chat'
    );

    chatSocket.onopen = function() {
        document.getElementById('disconnect-alert').classList.add('hidden');

        document.getElementById('disconnect-alert-text').innerText = "Oops, you're disconnected from the chat. Click here to reconnect!";

        chatSocket.send(JSON.stringify({
            'ping' : 'initial',
        }));
    }

    var intervalPing = window.setInterval(function(){
        window.start = performance.now();
        chatSocket.send(JSON.stringify({
            'ping' : 'performance',
        }));
      }, 200);

    const pingReading = document.getElementById('ping-reading')
    
    chatSocket.onmessage = function(e) {

        const data = JSON.parse(e.data);

        if ('message' in data && 'author' in data) {
            const chat = document.getElementById('chat')
            const message_container = document.getElementById('messages-container')

            message_id = 'msg_' + data.message_code

            message_container.innerHTML += `<div class="message"><div class="message-body"><div class="text"><div class="author"><span class="author-shadow-${data.author_color}"></span></div><div class="content neutral" id="${message_id}"><span class="message-tag leading-tag dislikable-excited color-${data.author_color}">{</span><span class="message-actual-content"></span><span class="message-tag trailing-tag likable-excited color-${data.author_color}">}</span><sup>0</sup></div></div></div></div>`;
        
            message_container.lastElementChild.firstElementChild.firstElementChild.lastElementChild.querySelector('.message-actual-content').innerHTML = escapeHtml(data.message); // A long chain leading to the middle span of the message 'content' div
            message_container.lastElementChild.firstElementChild.firstElementChild.firstElementChild.firstElementChild.innerHTML = data.author;

            if (chat.scrollTop != 0) {
                document.getElementById('new-messages-alert').classList.remove('hidden');
            } else {
                document.getElementById('new-messages-alert').classList.add('hidden');
            }

            // Clear typing
            userSpan = `<span class="color-${data.author_color}">${data.author}</span>`
            removeAllItems(typers, userSpan);
            updateTyping(); 


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
                superScore.innerText = parseInt(superScore.innerText) + 1

                superScore.classList.remove('disliked')
                superScore.classList.add('liked')

            }
            
            if (data.action === 'unlike') {
                id = data.message_id

                const superScore = document.getElementById(id).lastElementChild // Superscript Score
                superScore.innerText = parseInt(superScore.innerText) - 1

                superScore.classList.remove('disliked')
                superScore.classList.remove('liked')

            } 
            
            if (data.action === 'dislike') {
                id = data.message_id

                const superScore = document.getElementById(id).lastElementChild // Superscript Score
                superScore.innerText = parseInt(superScore.innerText) - 1

                superScore.classList.remove('liked')
                superScore.classList.add('disliked')

            }
            
            if (data.action == 'undislike') {
                id = data.message_id

                const superScore = document.getElementById(id).lastElementChild // Superscript Score
                superScore.innerText = parseInt(superScore.innerText) + 1

                superScore.classList.remove('liked')
                superScore.classList.remove('disliked')
            }

        } else if ('interaction' in data) { // An interaction here is defined as someone else interacting with a message.
            id = data.message_id

            if (data.interaction === 'like') {

                const messageDOM = document.getElementById(id)
                message_scoreDOM = messageDOM.lastElementChild
                message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) + 1
            } else if (data.interaction === 'unlike') {

                const messageDOM = document.getElementById(id)
                message_scoreDOM = messageDOM.lastElementChild
                message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) - 1
            } else if (data.interaction == 'dislike') {
                
                const messageDOM = document.getElementById(id)
                message_scoreDOM = messageDOM.lastElementChild
                message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) - 1
            } else if (data.interaction == 'undislike') {
                
                const messageDOM = document.getElementById(id)
                message_scoreDOM = messageDOM.lastElementChild
                message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) + 1
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

            const userSpan = `<span class="color-${data.typing_color}">${data.typing_user}</span>`

            var dwellingTimer;

            if (data.typing_status == 'started') {

                removeAllItems(typers, userSpan);

                typers.push(userSpan)

                clearTimeout(dwellingTimer);
                dwellingTimer = setTimeout(function() { 
                    removeAllItems(typers, userSpan);
                    updateTyping(); 
                }, 30000);

            } else if (data.typing_status == 'stopped') {

                removeAllItems(typers, userSpan);

            } 

            updateTyping();

        } else if ('pong' in data) {
            pingReading.innerText = Math.round(performance.now() - start) + 'ms'
        }
    };

    chatSocket.onclose = function(e) {
        document.getElementById('disconnect-alert').classList.remove('hidden');
        doneTyping()

        clearInterval(intervalPing)

        const expressions = ['(o_O) ?', '(((; ఠ ਉ ఠ))', '( Ŏ艸Ŏ)', '(｢ ⊙Д⊙)｢', '(☉_ ☉)', '( •́ ⍨ •̀)', '(ↁ_ↁ)']

        pingReading.innerText = expressions[Math.floor(Math.random()*expressions.length)];
    };

    chatInput.onkeydown = function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
        }
    };

    var typers = []

    var typingTimer; //timer identifier
    var doneTypingInterval = 3000; //time in ms
    var timerIsOn

    chatInput.onkeyup = function(e) {
        if (e.key === 'Enter') {
            document.querySelector('#chat-submit').click();
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

    chatInput.addEventListener('paste', function(e) {
    // cancel paste
    e.preventDefault();

    // get text representation of clipboard
    var text = (e.originalEvent || e).clipboardData.getData('text/plain');

    // insert text manually
    document.execCommand("insertHTML", false, text);
    });

    // Sends message and clears chat bar
    document.querySelector('#chat-submit').onclick = function(e) {
        const messageInputDom = chatInput;
        const message = messageInputDom.textContent;

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

    document.addEventListener("mouseover", function(e) {
        if (e.target.id.startsWith('msg_')) {
            chatSocket.send(JSON.stringify({
                'message_id' : e.target.id,
                'trigger' : 'hover'
            }))
        }
    })

    document.addEventListener("click", function(e) {
        classNames = e.target.className.toString().split(' ')
        if (classNames.includes('message-tag') && classNames.includes('trailing-tag')) {
            if (document.querySelector('input[name="puppet"]:checked')){

                const puppet = document.querySelector('input[name="puppet"]:checked').value;

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'trigger' : 'click',
                    'attempt' : 'like',
                    'puppet' : puppet
                }))

            } else {

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'trigger' : 'click',
                    'attempt' : 'like'
                }))

            }
        } else if (classNames.includes('message-tag') && classNames.includes('leading-tag')) {
            if (document.querySelector('input[name="puppet"]:checked')){

                const puppet = document.querySelector('input[name="puppet"]:checked').value;

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'trigger' : 'click',
                    'attempt' : 'dislike',
                    'puppet' : puppet
                }))

            } else {

                chatSocket.send(JSON.stringify({
                    'message_id' : e.target.closest('.content').id,
                    'trigger' : 'click',
                    'attempt' : 'dislike'
                }))
                
            }
        }
    })

    var timer; 
    document.getElementById('chat').addEventListener('scroll', event => {

        clearTimeout(timer);
        timer = setTimeout(() => {
            const {scrollTop} = event.target;
            if (Math.abs(scrollTop) < 10) {
                document.getElementById('new-messages-alert').classList.add('hidden');
            };
        }, 250)

    });

    document.getElementById('new-messages-alert').onclick = function(){jumpToBottom()}

    document.getElementById('disconnect-alert').onclick = function(){
        document.getElementById('disconnect-alert-text').innerText = "Connecting...";

        connect();
    };

};

connect();