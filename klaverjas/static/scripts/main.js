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

socket.on("notify", function(data) {
    console.log("notify", data);
    let table = document.getElementById("table");
    table.innerHTML = "";
    for (let i = 0; i < data.hand.length; i++) {
        let card = create_card(data.hand[i], "hand-" + (i + 1), "hand-" + (i + 1));
        table.appendChild(card);
    }
});

socket.on("ask_bid", function(data) {
    console.log("ask_bid", data);
    document.getElementById("trump-suit-chosen").className = "trump-suit suit-" + data.trump_suit;
    document.getElementById("play").addEventListener("click", function() {
        console.log("play");
        $("#ask-bid").modal("hide");
        socket.emit("bid", {"game": game, "trump_suit": data.trump_suit});
    });
    document.getElementById("pass").addEventListener("click", function() {
        console.log("pass");
        $("#ask-bid").modal("hide");
        socket.emit("bid", {"game": game});
    });
    $("#ask-bid").modal("show");
});

socket.on("force_bid", function(data) {
    console.log("force_bid", data);
    let options = document.getElementById("force-bid-options");
    for (let i = 0; i < data.trump_suit.length; i++) {
        let el = document.createElement("button");
        el.className = "trump-suit suit-" + data.trump_suit[i]
        el.addEventListener("click", function() {
            console.log("play", data.trump_suit[i]);
            $("#ask-bid").modal("hide");
            socket.emit("bid", {"game": game, "trump_suit": data.trump_suit[i]})
        });
        options.appendChild(el);
    }
    $("#force-bid").modal("show");
    /*
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
    */
});

socket.on("play", function(data) {
    console.log("play", data);
    for (let i = 0; i < data.legal_moves.length; i++) {
        let card = document.getElementById("hand-" + (i + 1));
        card.classList.add("movable");
        card.addEventListener("click", function() {
            console.log("play");
            socket.emit("play", {"game": game, "card": {"suit": data.legal_moves[i].suit,
                                                        "rank": data.legal_moves[i].rank}});
        });
    }
});

function suit_HTML(suit) {
    return {"clubs": "&clubs;", "diamonds": "&diams;",
            "hearts": "&hearts;", "spades": "&spades;"}[suit];
}

function create_card(card, id, classes) {
    let div = document.createElement("div");
    if (id) {
        div.id = id;
    }
    div.className = "card";
    if (classes) {
        div.classList.add(classes);
    }
    let face = document.createElement("div");
    face.className = "face"
    face.classList.add("suit-" + card.suit);
    let rank = document.createElement("span");
    rank.className = "rank";
    rank.innerHTML = card.rank;
    let suit = document.createElement("span");
    suit.className = "suit";
    suit.innerHTML = suit_HTML(card.suit);
    face.appendChild(rank);
    face.appendChild(suit);
    div.appendChild(face);
    return div;
}
