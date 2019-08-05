async function send(DATA, HEADERS, TARGET, METHOD) {
    const data = DATA;
    const headers = HEADERS;
    return fetch(TARGET, { method: METHOD, body: data, headers: headers }).then(response => { return response.text(); });
}

function gebi(id) {
    return document.getElementById(id);
}

function do_check() {
    let one = document.getElementById("1").value;
    let two = document.getElementById("2").value;
    let data = "one=" + encodeURIComponent(one) + "&two=" + encodeURIComponent(two);
    send(data, { "Content-Type": "application/x-www-form-urlencoded" }, "./kadai05.php", "POST").then(text => {
        console.log(text);
        if (text == "1") {
            document.body.style.backgroundColor = "green";
        }
        else {
            document.body.style.backgroundColor = "red";
        }
    });
}

function hi(e) {
    e.innerText = "";
    e.className = "menu";
}