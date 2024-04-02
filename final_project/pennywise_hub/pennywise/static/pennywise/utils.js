function showInstallments(el) {
    installments_box = document.getElementById("installments");
    if (el.checked) {
        installments_box.style.display = "block";
        installments_box.required = true;
        document.getElementById("monthly").setAttribute("disabled", "");
        document.getElementById("quarterly").setAttribute("disabled", "");
        if (document.getElementById("monthly").checked || document.getElementById("quarterly").checked) {
            document.getElementById("once").checked = true;
        }
        if (document.getElementById("installments").value > 12) {
            document.getElementById("once").checked = true;
            document.getElementById("yearly").setAttribute("disabled", "");
        }
    } else {
        installments_box.required = false;
        document.getElementById("installments").style.display = "none";
        document.getElementById("monthly").removeAttribute("disabled");
        document.getElementById("quarterly").removeAttribute("disabled");
        document.getElementById("yearly").removeAttribute("disabled");
    }
}

function checkInstallments(el) {
    if (el.value > 12) {
        document.getElementById("once").checked = true;
        document.getElementById("yearly").setAttribute("disabled", "");
    }
    else if (el.value <= 12) {
        document.getElementById("yearly").removeAttribute("disabled");
    }
}

function showMore(id) {
    if (document.getElementById(id).style.display === "none") {
        document.getElementById(id).style.display = "table-row";
    } else {
        document.getElementById(id).style.display = "none";
    }
}