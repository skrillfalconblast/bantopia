const params = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
  });

let sort = params.sort; 
let search = params.search;

const new_link = document.getElementById('new')
const trending_link = document.getElementById('trending')
const controversial_link = document.getElementById('controversial')

if (sort == 'new') {

  const navline = document.getElementById('navline')
  const post_scroll = document.getElementById('post-scroll')
  const posts = document.getElementsByClassName('post')

  new_link.firstElementChild.className = 'color-OR'
  trending_link.firstElementChild.className = ''
  controversial_link.firstElementChild.className = ''

  navline.className = 'navline'
  post_scroll.className = "post-scroll new-rail";
  posts.classNamea = 'post'

} else if (sort == 'trending') { 

  const navline = document.getElementById('navline')
  const post_scroll = document.getElementById('post-scroll')
  const posts = document.getElementsByClassName('post')

  new_link.firstElementChild.className = ''
  trending_link.firstElementChild.className = 'color-BL'
  controversial_link.firstElementChild.className = ''

  navline.className = 'navline trending-border'
  post_scroll.className = "post-scroll trending-rail";
  posts.classNamea = 'post trending-post-border'

} else if (sort == 'controversial') {

  const navline = document.getElementById('navline')
  const post_scroll = document.getElementById('post-scroll')
  const posts = document.getElementsByClassName('post')

  new_link.firstElementChild.className = ''
  trending_link.firstElementChild.className = ''
  controversial_link.firstElementChild.className = 'color-PU'

  navline.className = 'navline controversial-border'
  post_scroll.className = "post-scroll controversial-rail";
  posts.className = 'post controversial-post-border'

} else {

  const navline = document.getElementById('navline')
  const post_scroll = document.getElementById('post-scroll')
  const posts = document.getElementsByClassName('post')

  new_link.firstElementChild.className = 'color-OR'
  trending_link.firstElementChild.className = ''
  controversial_link.firstElementChild.className = ''

  navline.className = 'navline'
  post_scroll.className = "post-scroll new-rail";
  posts.classNamea = 'post'

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