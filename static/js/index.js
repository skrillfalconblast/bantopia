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
  rail.className = "new-rail";
  posts.classNamea = 'post'

  sortContainer.className = 'sort new-mobile-border'

} else if (sort == 'trending') { 

  new_link.firstElementChild.className = ''
  trending_link.firstElementChild.className = 'active-trending-link'
  controversial_link.firstElementChild.className = ''

  //navline.className = 'navline trending-border'
  rail.className = "trending-rail";
  posts.classNamea = 'post trending-post-border'

  sortContainer.className = 'sort trending-mobile-border'

} else if (sort == 'controversial') {

  new_link.firstElementChild.className = ''
  trending_link.firstElementChild.className = ''
  controversial_link.firstElementChild.className = 'active-controversial-link'

  //navline.className = 'navline controversial-border'
  rail.className = "controversial-rail";
  posts.className = 'post controversial-post-border'

  sortContainer.className = 'sort controversial-mobile-border'

} else {

  new_link.firstElementChild.className = 'active-new-link'
  trending_link.firstElementChild.className = ''
  controversial_link.firstElementChild.className = ''

  // navline.className = 'navline'
  rail.className = "new-rail";
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