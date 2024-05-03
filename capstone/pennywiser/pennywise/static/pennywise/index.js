// Swap between income and expanse transactions table
function swap_tab(el) {
    if (el.innerHTML == "Income") {
        document.getElementById("income").style.display = "block";
        document.getElementById("expense").style.display = "none";
        document.getElementById("expense-button").removeAttribute("disabled");
        el.setAttribute("disabled", "")
    }
    else {
        document.getElementById("expense").style.display = "block";
        document.getElementById("income").style.display = "none";
        document.getElementById("income-button").removeAttribute("disabled");
        el.setAttribute("disabled", "")
    }
}

// Set settle date to today by default 
window.onload = () => {
   
    dates = document.querySelectorAll(".today");
    for (let i = 0; i < dates.length; i++) {
        dates[i].valueAsDate = new Date();
    }
}

