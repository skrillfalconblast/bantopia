// For the collapsable mobile navbar -------------------

const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('collapsable-menu');

navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('menu-collapsed')
});

// -------------------------- Function -------------------------- //

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

// -------------------------- Voting System -------------------------- //
 
document.querySelector('#Y').onclick = function(e) {
    chatSocket.send(JSON.stringify({
        'voting' : 'Y',
    }));
};

document.querySelector('#N').onclick = function(e) {
    chatSocket.send(JSON.stringify({
        'voting' : 'N',
    }));
};

document.querySelector('#mobile-Y').onclick = function(e) {
    chatSocket.send(JSON.stringify({
        'voting' : 'Y',
    }));
};

document.querySelector('#mobile-N').onclick = function(e) {
    chatSocket.send(JSON.stringify({
        'voting' : 'N',
    }));
};



// For the chat -----------------------

const postCode = JSON.parse(document.getElementById('post-code').textContent);

const chatSocket = new WebSocket (
    'ws://'
    + window.location.host
    + '/ws/'
    + postCode
    + '/'
);

chatSocket.onmessage = function(e) {

    const data = JSON.parse(e.data);

    if ('message' in data && 'author' in data) {
        const message_container = document.getElementById('messages-container')

        message_id = 'msg_' + data.message_code

        message_container.innerHTML += `<div class="message"><div class="message-body"><div class="text"><div class="author"><span class="author-shadow-${data.author_color}"></span></div><div class="content neutral" id="${message_id}"><span class="message-tag leading-tag dislikable-excited color-${data.author_color}">{</span><span class="message-actual-content"></span><span class="message-tag trailing-tag likable-excited color-${data.author_color}">}</span><sup>0</sup></div></div></div></div>`
    
        message_container.lastElementChild.firstElementChild.firstElementChild.lastElementChild.querySelector('.message-actual-content').innerHTML = escapeHtml(data.message) // A long chain leading to the middle span of the message 'content' div
        message_container.lastElementChild.firstElementChild.firstElementChild.firstElementChild.firstElementChild.innerHTML = data.author
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

    } else if ('interaction' in data) {
        id = data.message_id

        if (data.interaction === 'like') {

            const messageDOM = document.getElementById(id)
            message_scoreDOM = messageDOM.lastElementChild
            message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) + 1
            console.log('liked')
        } else if (data.interaction === 'unlike') {

            const messageDOM = document.getElementById(id)
            message_scoreDOM = messageDOM.lastElementChild
            message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) - 1
            console.log('unliked')
        } else if (data.interaction == 'dislike') {
            
            const messageDOM = document.getElementById(id)
            message_scoreDOM = messageDOM.lastElementChild
            message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) - 1
            console.log(id)
            console.log('disliked')
            console.log('-----------------------')
        } else if (data.interaction == 'undislike') {
            
            const messageDOM = document.getElementById(id)
            message_scoreDOM = messageDOM.lastElementChild
            message_scoreDOM.innerText = parseInt(message_scoreDOM.innerText) + 1
            console.log('undisliked')
        }
    } else if ('y' in data || 'n' in data) {

        document.getElementById('Y').firstElementChild.innerText = 'yes=' + data.y
        document.getElementById('N').firstElementChild.innerText = 'no=' + data.n

        document.getElementById('mobile-Y').firstElementChild.innerText = 'yes=' + data.y
        document.getElementById('mobile-N').firstElementChild.innerText = 'no=' + data.n

    } else if ('alert' in data) {
        if (data.alert == 'command_success') {
            const message_container = document.getElementById('messages-container')

            message_text = data.message

            message_container.innerHTML += `<div class="message command-border"><div class="message-body"><div class="text"><div class="content neutral"><span></span><span class="message-actual-content command-text">&lt;${message_text}&gt;</span></div></div></div></div>`
        }
    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly')
};

document.querySelector('#chat-input').onkeyup = function(e) {
    if (e.keyCode === 13) {
        document.querySelector('#chat-submit').click();
    }
};

document.querySelector('#chat-input').onkeydown = function(e) {
    if (e.keyCode === 13) {
        e.preventDefault();
    }
};

// Sends message and clears chat bar
document.querySelector('#chat-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-input');
    const message = messageInputDom.textContent;
    if (message != '') {
        chatSocket.send(JSON.stringify({
            'message' : message,
        }));
        messageInputDom.textContent = '';
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
    classNames = e.target.className.split(' ')
    if (classNames.includes('message-tag') && classNames.includes('trailing-tag')) {
        chatSocket.send(JSON.stringify({
            'message_id' : e.target.closest('.content').id,
            'trigger' : 'click',
            'attempt' : 'like'
        }))
    } else if (classNames.includes('message-tag') && classNames.includes('leading-tag')) {
        chatSocket.send(JSON.stringify({
            'message_id' : e.target.closest('.content').id,
            'trigger' : 'click',
            'attempt' : 'dislike'
        }))
    }
  })

