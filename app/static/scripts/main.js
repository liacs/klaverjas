"use strict";

const socket = io(location.protocol + "//" +
                  document.domain + ":" +
                  location.port);

socket.on("connect", function() {
    console.log("connect", socket.id);
    socket.emit("join", {"game": game});
});

socket.on("disconnect", function() {
    console.log("disconnect");
});

socket.on("log", function(data) {
    console.log("log", data);
    let hand = document.getElementById("hand");
    hand.innerHTML = "";
    for (let i = 0; i < data.hand.length; i++) {
        let card = create_card(data.hand[i]);
        hand.appendChild(card);
    }
});

socket.on("ask_bid", function(data) {
    console.log("ask_bid", data);
    let div = document.getElementById("ask_bid");
    document.getElementById("play").addEventListener("click", function _play() {
        console.log("play");
        socket.emit("bid", {"game": game, "trump_suit": data.trump_suit});
        this.removeEventListener("click", _play);
        div.style.visibility = "hidden";
    });
    document.getElementById("pass").addEventListener("click", function _pass() {
        console.log("pass");
        socket.emit("bid", {"game": game});
        this.removeEventListener("click", _pass);
        div.style.visibility = "hidden";
    });
    document.getElementById("trump").classList.add("suit-" + data.trump_suit);
    div.style.visibility = "visible";
});

socket.on("force_bid", function(data) {
    console.log("force_bid", data);
    let div = document.getElementById("force_bid");
    for (let i = 0; i < data.trump_suit.length; i++) {
        let span = document.createElement("span");
        span.className = "trump_suit";
        span.classList.add("suit-" + data.trump_suit[i]);
        span.addEventListener("click", function(suit) {
            console.log(data.trump_suit[i]);
            socket.emit("bid", {"game": game, "trump_suit": data.trump_suit[i]})
            div.innerHTML = "";
            div.style.visibility = "hidden";
        });
        div.appendChild(span);
    }
    div.style.visibility = "visible";
});

socket.on("play", function(data) {
    console.log("play", data);
    for (let i = 0; i < data.legal_moves.length; i++) {
        let card = document.getElementById(data.legal_moves[i].suit + data.legal_moves[i].rank);
        card.classList.add("movable");
        card.addEventListener("click", function() {
            card.classList.toggle("selected");
        });
    }
});

function suit_HTML(suit) {
    return {"clubs": "&clubs;", "diamonds": "&diams;",
            "hearts": "&hearts;", "spades": "&spades;"}[suit];
}

function create_card(card) {
    let div = document.createElement("div");
    div.id = card.suit + card.rank
    div.className = "card";
    div.classList.add("suit-" + card.suit);
    let rank = document.createElement("span");
    rank.className = "rank";
    rank.innerHTML = card.rank;
    let suit = document.createElement("span");
    suit.className = "suit";
    suit.innerHTML = suit_HTML(card.suit);
    div.appendChild(rank);
    div.appendChild(suit);
    return div;
}
