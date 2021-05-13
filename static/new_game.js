document.getElementById('new_challenge').addEventListener(
    'click', new_challenge, false
);
document.getElementById('new_random').addEventListener(
    'click', new_random, false
);
document.getElementById('new_bot').addEventListener(
    'click', new_bot, false
);

function new_challenge(evt) {
    evt.preventDefault()
    console.log("Try new_challenge")
}

function new_random(evt) {
    evt.preventDefault()
    console.log("Try new_random")
}

function new_bot(evt) {
    evt.preventDefault()
    console.log("Try new_bot")
}