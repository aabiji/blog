function updateYear() {
    let date = new Date().getFullYear();
    let msg_element = document.getElementById("msg");
    let msg = `<a href='https://github.com/aabiji'>@aabiji</a> 2022 - ${date}`;
    msg_element.innerHTML = msg;
}

function getGithubLogoSrc(theme) {
	let path = window.location.pathname.split("/");
	path = path.slice(0, path.length - 1);

	let base_path = (path[path.length - 1] === "blog" ? "assets/imgs/" : "../assets/imgs/");
	let file = (theme === "dark" ? "light-logo.png" : "dark-logo.png");

	return base_path + file;
}

function toggleTheme() {
	let theme_switch = document.getElementById("theme_switch");
	let theme = window.localStorage.getItem("css_theme");
	let body = document.getElementsByTagName("body")[0];
	let github_logo = document.getElementById("github-logo");

	if (theme === "dark") {
		body.className = "light";
		theme_switch.innerHTML = "Dark 🌙";
		github_logo.src = getGithubLogoSrc("light");
		window.localStorage.setItem("css_theme", "light");
	} else {
		body.className = "dark";
		theme_switch.innerHTML = "Light ☀️";
		github_logo.src = getGithubLogoSrc("dark");
		window.localStorage.setItem("css_theme", "dark");
	}
}

function update() {
	let theme_switch = document.getElementById("theme_switch");
	let body = document.getElementsByTagName("body")[0];
	let theme = window.localStorage.getItem("css_theme");
	let github_logo = document.getElementById("github-logo");

	if (theme !== "dark" && theme !== "light") {
		theme = "light";
		window.localStorage.setItem("css_theme", "light");
	}

	body.className = theme;

	if (theme === "light") {
		theme_switch.innerHTML = "Dark 🌙";
		github_logo.src = getGithubLogoSrc("light");
	} else {
		theme_switch.innerHTML = "Light ☀️";
		github_logo.src = getGithubLogoSrc("dark");
	}

	updateYear();
}
