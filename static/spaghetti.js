function popsicle(ar) {
    return ar[ar.length - 1];
}

function darkmode() {
    const html = document.getElementById("Html");

    if (html.className === "dark") {
        html.className = "light";
        console.log("Light mode")
    } else {
        html.className = "dark";
        console.log("Dark mode")
    }

    const button = document.getElementById("darkmode-btn");
    const icon = button.querySelector('img');
    const current = popsicle(icon.src.split('/'));
    console.log(icon.src)
    icon.src = (icon.src.includes("static/dark.svg")) ? "static/light.svg" : "static/dark.svg";
}
