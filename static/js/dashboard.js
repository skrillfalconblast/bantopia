
// ------------------- Tabs ------------------------

const command_pane = document.getElementById("dashboard-commands")
const rules_pane = document.getElementById("dashboard-rules")
const tips_pane = document.getElementById("dashboard-tips")

const command_tab = document.getElementById("dashboard-commands-tab")
const rules_tab = document.getElementById("dashboard-rules-tab")
const tips_tab = document.getElementById("dashboard-tips-tab")



command_tab.onclick = function(e){
    command_pane.classList.remove('hidden')

    rules_pane.classList.add('hidden')
    tips_pane.classList.add('hidden')
}

rules_tab.onclick = function(e){
    rules_pane.classList.remove('hidden')

    command_pane.classList.add('hidden')
    tips_pane.classList.add('hidden')
}

tips_tab.onclick = function(e){
    tips_pane.classList.remove('hidden')

    rules_pane.classList.add('hidden')
    command_pane.classList.add('hidden')
}


// Mobile Navigation


const one_btn = document.getElementById("mobile-nav-1")
const two_btn = document.getElementById("mobile-nav-2")
const three_btn = document.getElementById("mobile-nav-3")

const watchlist = document.getElementById("dashboard-right")
const identity = document.getElementById("dashboard-identity")
const info = document.getElementById("dashboard-info-pane")
const dashboardLeft = document.getElementById("dashboard-left")


one_btn.onclick = function(e){
     info.className = 'dashboard-info-pane'
     watchlist.className = 'dashboard-right mobile-hidden'
     identity.className = 'dashboard-identity mobile-hidden'
     dashboardLeft.className = 'dashboard-left'

     one_btn.className = 'dashboard-title-menu-mobile dashboard-blue'
     two_btn.className = 'dashboard-title-menu-mobile'
     three_btn.className = 'dashboard-title-menu-mobile'
}

two_btn.onclick = function(e){
    info.className = 'dashboard-info-pane mobile-hidden'
    watchlist.className = 'dashboard-right'
    identity.className = 'dashboard-identity mobile-hidden'
    dashboardLeft.className = 'dashboard-left mobile-hidden'
    

    one_btn.className = 'dashboard-title-menu-mobile'
    two_btn.className = 'dashboard-title-menu-mobile dashboard-blue'
    three_btn.className = 'dashboard-title-menu-mobile'
}

three_btn.onclick = function(e){
    info.className = 'dashboard-info-pane mobile-hidden'
    watchlist.className = 'dashboard-right mobile-hidden'
    identity.className = 'dashboard-identity'
    dashboardLeft.className = 'dashboard-left'

    one_btn.className = 'dashboard-title-menu-mobile'
    two_btn.className = 'dashboard-title-menu-mobile'
    three_btn.className = 'dashboard-title-menu-mobile dashboard-blue'
}
