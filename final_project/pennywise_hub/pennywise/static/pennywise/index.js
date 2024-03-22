function showSettle(id) {
    el_button = document.getElementsByClassName(id)[0];
    el = document.getElementById(id);
    el.style.animationDuration = "0.2s";
    el.style.animationPlaystate = "paused";
    el.style.animationFillMode = "forwards";
    if (el_button.innerHTML == "˅") {
        el_button.innerHTML = "˄";
        el.style.animationName = "slide-down";
        el.style.animationPlaystate = "running";
        el.style.display = "table-row";  
    }
    else {
        el_button.innerHTML = "˅";
        el.style.animationName = "slide-up";
        el.style.animationPlaystate = "running";
        setTimeout(() => {
            el.style.display = "none";
          }, 200)
    }
}

// Show expense transactions table
function show_expense(el) {
    document.getElementById("expense").style.display = "block";
    document.getElementById("income").style.display = "none";
    document.getElementById("income-button").removeAttribute("disabled");
    el.setAttribute("disabled", "")

}

// Show income transactions table
function show_income(el) {
    document.getElementById("income").style.display = "block";
    document.getElementById("expense").style.display = "none";
    document.getElementById("expense-button").removeAttribute("disabled");
    el.setAttribute("disabled", "")
}

// Set settle date to today by default 
window.onload = () => {
   
    dates = document.querySelectorAll(".today");
    for (let i = 0; i < dates.length; i++) {
        dates[i].valueAsDate = new Date();
    }
}

/* 
// Maintain the current select tab (expense or income)
if (document.getElementById("current_tab")) {
        document.getElementById("income-button").click();
        console.log(document.getElementById("income-button"))
}  
*/