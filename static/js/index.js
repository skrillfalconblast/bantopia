const params = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
  });

let sort = params.sort; 
let search = params.search;

const new_link = document.getElementById('new')
const trending_link = document.getElementById('trending')
const controversial_link = document.getElementById('controversial')

const navline = document.getElementById('navline')
const rail = document.getElementById('rail')
const posts = document.getElementsByClassName('post')

const sortContainer = document.getElementById('sort')

if (sort == 'new') {

  new_link.firstElementChild.className = 'active-new-link'
  trending_link.firstElementChild.className = ''
  controversial_link.firstElementChild.className = ''

  //navline.className = 'navline'
  document.querySelectorAll('.right-label-face').forEach(e => e.classList = 'right-label-face new-face')
  document.querySelectorAll('.post-label-box').forEach(e => e.classList = 'post-label-box new-face')
  posts.classNamea = 'post'

  sortContainer.className = 'sort new-mobile-border'

} else if (sort == 'trending') { 

  new_link.firstElementChild.className = ''
  trending_link.firstElementChild.className = 'active-trending-link'
  controversial_link.firstElementChild.className = ''

  //navline.className = 'navline trending-border'
  document.querySelectorAll('.right-label-face').forEach(e => e.classList = 'right-label-face trending-face')
  document.querySelectorAll('.post-label-box').forEach(e => e.classList = 'post-label-box trending-face')
  posts.classNamea = 'post trending-post-border'

  sortContainer.className = 'sort trending-mobile-border'

} else if (sort == 'controversial') {

  new_link.firstElementChild.className = ''
  trending_link.firstElementChild.className = ''
  controversial_link.firstElementChild.className = 'active-controversial-link'

  //navline.className = 'navline controversial-border'
  document.querySelectorAll('.right-label-face').forEach(e => e.classList = 'right-label-face controversial-face')
  document.querySelectorAll('.post-label-box').forEach(e => e.classList = 'post-label-box controversial-face')
  posts.className = 'post controversial-post-border'

  sortContainer.className = 'sort controversial-mobile-border'

} else {

  new_link.firstElementChild.className = 'active-new-link'
  trending_link.firstElementChild.className = ''
  controversial_link.firstElementChild.className = ''

  // navline.className = 'navline'
  document.querySelectorAll('.right-label-face').forEach(e => e.classList = 'right-label-face new-face')
  document.querySelectorAll('.post-label-box').forEach(e => e.classList = 'post-label-box new-face')
  posts.classNamea = 'post'

  sortContainer.className = 'sort new-border'

}

if (search) {
  if (search.trim() != '') {

    const search_term_container = document.getElementById('search-term-container')
    search_term_container.className = 'search-term-container'

    const search_term = document.getElementById('search-term')
    search_term.innerText = search

    new_link.firstElementChild.className = ''
    trending_link.firstElementChild.className = ''
    controversial_link.firstElementChild.className = ''

  } else {

    const search_term_container = document.getElementById('search-term-container')
    search_term_container.className = 'search-term-container hidden'

  }
}

const observer = new IntersectionObserver((entries) => { 
  entries.forEach((entry) => {
    if (!entries[0].isIntersecting) {
      entry.target.querySelector('.post-counter-ticker').classList.remove('unpaused')
    }
    else {
      entry.target.querySelector('.post-counter-ticker').classList.add('unpaused')
    }
  })
}); 

document.querySelectorAll('.post').forEach((i) => {
  if (i) {
      observer.observe(i);
  }
})

function truncate(str, n) {
  if (str.length <= n) { return str; }
  var subString = str.slice(0, n-1); // the original check
  var index = subString.lastIndexOf(" ");
  subString = subString.substring(0, index) + "..." 
  return subString
};

function setTime(display) {
  totalSeconds = 0

  var interval = setInterval(function() { 
    
    totalSeconds++;

    if (totalSeconds == 1) {
      display.innerText = totalSeconds + ' sec ago'
    } else if (totalSeconds < 60) {
      display.innerText = totalSeconds + ' sec ago'
    } else if ((Math.floor(totalSeconds / 60)) == 1) {
      display.innerText = (Math.floor(totalSeconds / 60)) + ' min ago'
    } else if ((totalSeconds >= 60) && (totalSeconds <= 3600)) {
      display.innerText = (Math.floor(totalSeconds / 60)) + ' mins ago'
    } else if (((Math.floor(totalSeconds / 3600)) == 1)) {
      display.innerText = (Math.floor(totalSeconds / 3600)) + 'hour ago'
    } else if ((totalSeconds >= 3600)) {
      display.innerText = (Math.floor(totalSeconds / 3600)) + 'hours ago'
    } 
  }, 1000);
}

var activatedLastActivesDict = {}; 

function getCounter(display, post_id) {

  let totalSeconds = 0;
  let interval;
  let isActive = false;

  function updateCounter() {
    totalSeconds++;

    if (totalSeconds == 1) {

      display.innerText = totalSeconds + ' sec ago'

    } else if (totalSeconds < 60) {

      display.innerText = totalSeconds + ' secs ago'

    } else if ((Math.floor(totalSeconds / 60)) == 1) {

      display.innerText = (Math.floor(totalSeconds / 60)) + ' min ago'

    } else if ((totalSeconds >= 60) && (totalSeconds < 3600)) {

      display.innerText = (Math.floor(totalSeconds / 60)) + ' mins ago'

    } else if (((Math.floor(totalSeconds / 3600)) == 1)) {

      display.innerText = (Math.floor(totalSeconds / 3600)) + 'hr ago'

    } else if ((totalSeconds >= 3600)) {

      display.innerText = (Math.floor(totalSeconds / 3600)) + 'hrs ago'

    } else if ((totalSeconds >= 3600) && (totalSeconds < 86400)) {

      display.innerText = (Math.floor(totalSeconds / 3600)) + 'hours ago'

    } else if (((Math.floor(totalSeconds / 86400)) == 1)) {

      display.innerText = (Math.floor(totalSeconds / 86400)) + 'day ago'

    } else if ((totalSeconds >= 86400) && (totalSeconds < 2592000)) {

      display.innerText = (Math.floor(totalSeconds / 86400)) + 'days ago'

    } else if (((Math.floor(totalSeconds / 2592000)) == 1)) {

      display.innerText = '1 mnth ago'

    } else if ((totalSeconds >= 2592000) && (totalSeconds < 31104000)) {

      display.innerText = '+1 mnths ago'

    } else if ((Math.floor(totalSeconds / 31104000)) == 1) {

      display.innerText = '1 yr ago'

    } else if (totalSeconds > 31104000) {

      display.innerText = '+1 yrs ago'

    }
  }

  if (!isActive) {
    
    console.log(activatedLastActivesDict)

    if (!(post_id in activatedLastActivesDict)) {

      console.log('its not in')
      interval = setInterval(updateCounter, 1000);
      activatedLastActivesDict[post_id] = interval

    } else {

      console.log('its in')
      console.log(JSON.parse(activatedLastActivesDict[post_id]))
      clearInterval(JSON.parse(activatedLastActivesDict[post_id]))
      interval = setInterval(updateCounter, 1000);
      activatedLastActivesDict[post_id] = interval
    }

    isActive = true;
  }
}
 
function connect(){

    var loc = window.location
    var wsProtocol = 'ws://'
    if (loc.protocol == "https:"){
        wsProtocol = 'wss://'
    }

    const homeSocket = new WebSocket(
        wsProtocol
        + window.location.host
    );

    /*
    homeSocket.onopen = function() {
    }
    */

    homeSocket.onmessage = function(e) {
      
      const data = JSON.parse(e.data);
        
      if ('last_message_content' in data){

        post_id = 'pst_' + data.post_code

        const postDom = document.getElementById(post_id)
        const lastMessageBarDom = postDom.querySelector('.message-bar')
        const beacon = lastMessageBarDom.firstElementChild
        const recentMessageCrier = lastMessageBarDom.lastElementChild.querySelector('.recent-message-crier')
        const lastMessageContent = lastMessageBarDom.lastElementChild.querySelector('.recent-message-content')

        beacon.classList.add('post-icon-active')
        recentMessageCrier.innerText = 'New Message'
        lastMessageContent.innerText = truncate(data.last_message_content, 35)

        const lastActive = postDom.firstElementChild.firstElementChild.lastElementChild
        const recoilBar = postDom.firstElementChild.lastElementChild.firstElementChild

        getCounter(lastActive, post_id)

        lastActive.classList.add('active-just-now')
        recoilBar.classList.remove('recoiling')
        recoilBar.offsetWidth
        recoilBar.classList.add('recoiling')

        notifSound.play()

      } else if (('data_point' in data)) {

        if ((data.data_point == 'someone_typing')) {

          post_id = 'pst_' + data.post_code

          const postDom = document.getElementById(post_id)
          const typingSpan = postDom.firstElementChild.querySelector('.typing-stat').firstElementChild

          typingSpan.innerHTML = '<span class="typing-span">Someone is </span><span class="typing-word">typing...</span>'
          typingSpan.classList.add('typing')

          var typingTimer;

          typingTimer = setTimeout(function() { 
            typingSpan.innerHTML = '<span class="typing-span">Someone was typing...</span>'
            typingSpan.classList.remove('typing')
          }, 10000);

        }

        } else if ('pong' in data) {

          pingReading.innerText = Math.round(performance.now() - start) + 'ms'
        
        }
    };

    const pingReading = document.getElementById('home-ping-reading');

    if (pingReading) {
        var performanceIntervalPing = window.setInterval(function(){
            window.start = performance.now();
            homeSocket.send(JSON.stringify({
                'ping' : 'performance',
            }));
        }, 200);
    }

    homeSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

}

connect()