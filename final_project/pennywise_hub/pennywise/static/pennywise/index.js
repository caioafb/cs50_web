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

