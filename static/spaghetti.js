function popsicle(ar) {
    return ar[ar.length - 1];
}

function darkmode() {
    const html = document.getElementById("Html");
    const icon = document.getElementById("darkmode");

    if (html.className === "dark") {
        html.className = "light";
        localStorage.setItem("theme", "light");
        icon.src = "/static/dark.svg";
    } else {
        html.className = "dark";
        localStorage.setItem("theme", "dark");
        icon.src = "/static/light.svg";
    }
}
