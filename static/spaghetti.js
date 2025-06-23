function darkmode() {
  const html = document.getElementById("Html");
  const icon = document.getElementById("darkmode");

  const isDark = html.classList.contains("dark");

  if (isDark) {
    html.classList.remove("dark");
    html.classList.add("light");
    localStorage.setItem("theme", "light");
    icon.src = "/static/dark.svg";
  } else {
    html.classList.remove("light");
    html.classList.add("dark");
    localStorage.setItem("theme", "dark");
    icon.src = "/static/light.svg";
  }
}
