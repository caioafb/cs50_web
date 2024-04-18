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

function disableInstallment() {
    el = document.getElementById("has_installments");
    el.setAttribute("disabled", "");
    el.checked = false;
}

function enableInstallment() {
    el = document.getElementById("has_installments");
    el.removeAttribute("disabled");
}

function showMore(id) {
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

function submitForm(img) {
    var form = img.parentNode;
    if (form.tagName === 'FORM') {
        form.submit();
    }
}

function showDeleteConfirmation() {
    document.getElementById("delete").style.display = "none";
    document.getElementById("confirmation").style.display = "initial";
}

// Swap between statement and projection tables
function swap_overview_tab(el) {
    if (el.innerHTML == "Overview") {
        document.getElementById("overview").style.display = "block";
        document.getElementById("projection").style.display = "none";
        document.getElementById("projection-button").removeAttribute("disabled");
        el.setAttribute("disabled", "");
    }
    else {
        document.getElementById("projection").style.display = "block";
        document.getElementById("overview").style.display = "none";
        document.getElementById("overview-button").removeAttribute("disabled");
        el.setAttribute("disabled", "");
    }
}