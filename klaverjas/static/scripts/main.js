"use strict";

const socket = io(location.protocol + "//" + document.domain + ":" +
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

    for (let i = 0; i < 8; i++) {
        let elements = document.getElementsByClassName("hand-" + (i + 1));
        while (elements.length > 0) {
            elements[0].remove();
        }
    }

    if (data.trick.length === 0)
    {
        document.getElementById("trick-west").innerHTML = "";
        document.getElementById("trick-north").innerHTML = "";
        document.getElementById("trick-east").innerHTML = "";
        document.getElementById("trick-south").innerHTML = "";
    }

    for (let el of ["west", "north", "east", "south"]) {
        let player = document.getElementById("player-" + el);
        let avatar = document.createElement("img");
        avatar.src = data[el].avatar;
        avatar.className = "img-rounded";
        player.innerHTML = "";
        player.appendChild(avatar);
        if (data[el].name === data.dealer) {
            let dealer = document.createElement("div");
            dealer.className = "dealer";
            player.appendChild(dealer);
        }

        if (data[el].name === data.lead) {
            let trump = document.createElement("div");
            trump.className = "trump";
            let trump_suit = document.createElement("div");
            trump_suit.className = "suit-" + data.trump_suit;
            trump.appendChild(trump_suit);
            player.appendChild(trump);
        }

        if (el !== "south") {
            let hand = document.getElementById("hand-" + el);
            hand.innerHTML = "";
            for (let i = 0; i < data[el].card_count; i++) {
                let card = document.createElement("div");
                card.className = "card";
                hand.appendChild(card);
            }
        }

        for (let card of data.trick) {
            if (data[el].name === card.player) {
                let div = create_card(card.card);
                document.getElementById("trick-" + el).appendChild(div);
            }
        }
    }

    for (let i = 0; i < data.hand.length; i++) {
        let card = create_card(data.hand[i], data.hand[i].suit + data.hand[i].rank, "hand-" + (i + 1));
        table.appendChild(card);
    }
});

socket.on("ask_bid", function(data) {
    console.log("ask_bid", data);
    document.getElementById("trump-suit-chosen").className = "trump-suit suit-" + data.trump_suit;
    document.getElementById("play").addEventListener("click", function _play() {
        console.log("play");
        this.removeEventListener("click", _play);
        $("#ask-bid").modal("hide");
        socket.emit("bid", {"game": game, "trump_suit": data.trump_suit});
    });
    document.getElementById("pass").addEventListener("click", function _pass() {
        console.log("pass");
        this.removeEventListener("click", _pass);
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
        el.addEventListener("click", function _choose() {
            console.log("play", data.trump_suit[i]);
            this.removeEventListener("click", _choose);
            $("#force-bid").modal("hide");
            socket.emit("bid", {"game": game, "trump_suit": data.trump_suit[i]})
        });
        options.appendChild(el);
    }
    $("#force-bid").modal("show");
});

socket.on("play", function(data) {
    console.log("play", data);
    for (let i = 0; i < data.legal_moves.length; i++) {
        let card = document.getElementById(data.legal_moves[i].suit + data.legal_moves[i].rank);
        card.classList.add("movable");
        card.addEventListener("click", function() {
            console.log("play");
            socket.emit("play", {"game": game, "card": {"suit": data.legal_moves[i].suit,
                                                        "rank": data.legal_moves[i].rank}});
        });
    }
});

function suit_HTML(suit) {
    return {"clubs": "&clubs;&#xFE0E;", "diamonds": "&diams;&#xFE0E;",
            "hearts": "&hearts;&#xFE0E;", "spades": "&spades;&#xFE0E;"}[suit];
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
