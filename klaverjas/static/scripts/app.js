"use strict";


function suit_HTML(suit) {
    return {"clubs": "&clubs;&#xfe0e;", "diamonds": "&diams;&#xfe0e;",
            "hearts": "&hearts;&#xfe0e;", "spades": "&spades;&#xfe0e;"}[suit];
}

function create_card(card, id, classes) {
    let dom_card = document.createElement("div");
    if (id) {
        dom_card.id = id;
    }
    dom_card.className = "card";
    if (classes) {
        dom_card.classList.add(classes);
    }
    let dom_face = document.createElement("div");
    dom_face.className = "face"
    dom_face.classList.add("suit-" + card.suit);
    let dom_rank = document.createElement("span");
    dom_rank.className = "rank";
    dom_rank.innerHTML = card.rank;
    let dom_suit = document.createElement("span");
    dom_suit.className = "suit";
    dom_suit.innerHTML = suit_HTML(card.suit);
    dom_face.appendChild(dom_rank);
    dom_face.appendChild(dom_suit);
    dom_card.appendChild(dom_face);
    return dom_card;
}


const App = (function() {


    let states = [];
    let players = {};


    const init = function(state) {
        states = [];
        players = {};
        if (state) {
            update(state);
        }
        window.requestAnimationFrame(render);
    };

    const event_ask_bid = function(data) {
        document.getElementById("trump-suit-chosen").className = "trump-suit suit-" + data.trump_suit;
        document.getElementById("play").addEventListener("click", function _bid() {
            this.removeEventListener("click", _bid);
            $("#ask-bid").modal("hide");
            socket.emit("bid", {"game": game, "trump_suit": data.trump_suit});
        });
        document.getElementById("pass").addEventListener("click", function _pass() {
            this.removeEventListener("click", _pass);
            $("#ask-bid").modal("hide");
            socket.emit("pass", {"game": game});
        });
        $("#ask-bid").modal("show");
    };

    const event_ask_play = function(data) {
        data.legal_moves.forEach(function(item, index) {
            const dom_card = document.getElementById(item.suit + item.rank);
            dom_card.classList.add("movable");
            dom_card.addEventListener("click", function _play() {
                data.legal_moves.forEach(function(item, index) {
                    const dom_card = document.getElementById(item.suit + item.rank);
                    dom_card.classList.remove("movable");
                    dom_card.removeEventListener("click", _play);
                    const dom_table = document.getElementById("table");
                });
                table.removeChild(dom_card);
                socket.emit("play", {"game": game, "card": {"suit": item.suit,
                                                            "rank": item.rank}});
            });
        });
    };

    const event_bid = function(data) {
        document.getElementById("player-" + players[data.player]).classList.remove("active");
        document.getElementById("player-" + players[data.to_play]).classList.add("active");
        // TODO: show trump_suit
    };

    const event_deal = function(data) {
        for (const position of ["north", "east", "west"]) {
            const dom_hand = document.getElementById("hand-" + position);
            dom_hand.innerHTML = "";
            for (let i = 0; i < 8; ++i) {
                const dom_card = document.createElement("div");
                dom_card.className = "card";
                dom_hand.appendChild(dom_card);
            }
        }

        document.getElementById("player-" + players[data.to_play]).classList.add("active");

        const dom_table = document.getElementById("table");
        for (let i = 1; i <= 8; ++i) {
            dom_table.querySelectorAll(".hand-" + i).forEach(function(item, index) {
                dom_table.removeChild(item);
            });
        }

        data.hand.forEach(function(item, index) {
            let dom_card = create_card(item, item.suit + item.rank, "hand-" + (index + 1));
            dom_table.appendChild(dom_card);
        });
    };

    const event_force_bid = function(data) {
        const dom_options = document.getElementById("force-bid-options");
        data.trump_suits.forEach(function(item, index) {
            const dom_trump = document.createElement("button");
            dom_trump.className = "trump-suit suit-" + item;
            dom_trump.addEventListener("click", function _choose() {
                this.removeEventListener("click", _choose);
                $("#force-bid").modal("hide");
                socket.emit("bid", {"game": game, "trump_suit": item})
            });
            dom_options.appendChild(dom_trump);
        });
        $("#force-bid").modal("show");
    };

    const event_init = function(data) {
        for (const position of ["north", "east", "south", "west"]) {
            players[data[position].name] = position;
            const dom_player = document.getElementById("player-" + position);
            const dom_avatar = document.createElement("img");
            dom_avatar.src = data[position].avatar;
            dom_avatar.className = "img-rounded";
            dom_player.innerHTML = "";
            dom_player.appendChild(dom_avatar);
        }
    };

    const event_pass = function(data) {
        document.getElementById("player-" + players[data.player]).classList.remove("active");
        document.getElementById("player-" + players[data.to_play]).classList.add("active");
    };

    const event_play = function(data) {
        const dom_card = create_card(data.card);
        const dom_trick = document.getElementById("trick-" + players[data.player]);
        dom_trick.appendChild(dom_card);
        document.getElementById("player-" + players[data.player]).classList.remove("active");
        document.getElementById("player-" + players[data.to_play]).classList.add("active");
    };

    const event_score = function(data) {

    };

    const event_take_trick = function(data) {
        for (const position of ["north", "east", "south", "west"]) {
            const dom_trick = document.getElementById("trick-" + position);
            dom_trick.removeChild(dom_trick.firstChild);
        }
    };

    const event_trick = function(data) {
        for (const position of ["north", "east", "west"]) {
            const dom_hand = document.getElementById("hand-" + position);
            dom_hand.innerHTML = "";
            for (let i = 0; i < data[position]; ++i) {
                const dom_card = document.createElement("div");
                dom_card.className = "card";
                dom_hand.appendChild(dom_card);
            }
        }

        document.getElementById("player-" + players[data.to_play]).classList.add("active");

        const dom_table = document.getElementById("table");
        for (let i = 1; i <= 8; ++i) {
            dom_table.querySelectorAll(".hand-" + i).forEach(function(item, index) {
                dom_table.removeChild(item);
            });
        }

        data.hand.forEach(function(item, index) {
            let dom_card = create_card(item, item.suit + item.rank, "hand-" + (index + 1));
            dom_table.appendChild(dom_card);
        });

        data.trick.forEach(function(item, index) {
            const dom_card = create_card(item.card);
            const dom_trick = document.getElementById("trick-" + players[item.player]);
            dom_trick.appendChild(dom_card);
        });
    };

    const render = function() {
        const data = states.shift();
        if (data) {
            switch (data.event) {
                case "ask_bid":
                    event_ask_bid(data);
                    render();
                    break;
                case "ask_play":
                    event_ask_play(data);
                    render();
                    break;
                case "bid":
                    event_bid(data);
                    render();
                    break;
                case "deal":
                    event_deal(data);
                    window.setTimeout(render, 250);
                    break;
                case "force_bid":
                    event_force_bid(data);
                    render();
                    break;
                case "init":
                    event_init(data);
                    render();
                    break;
                case "pass":
                    event_pass(data);
                    render();
                    break;
                case "play":
                    event_play(data);
                    window.setTimeout(render, 500);
                    break;
                case "score":
                    event_score(data);
                    window.setTimeout(render, 1000);
                    break;
                case "take_trick":
                    data.event = "take_trick2";
                    update(data)
                    window.setTimeout(render, 1000);
                    break;
                case "take_trick2":
                    event_take_trick(data);
                    render();
                    break;
                case "trick":
                    event_trick(data);
                    render();
                    break;
                default:
                    console.debug(data);
            }
            return;
        }
        window.requestAnimationFrame(render);
    };

    const update = function(state) {
        states.push(state);
    };


    return {
        init: init,
        update: update
    }
})();


const socket = io(location.protocol + "//" + document.domain + ":" +
                  location.port);


socket.on("connect", function() {
    console.debug("connect", socket.id);
    socket.emit("join", {"game": game});
    App.init();
});


socket.on("disconnect", function() {
    console.debug("disconnect");
});


socket.on("ask_bid", function(data) {
    console.debug("ask_bid", data);
    data.event = "ask_bid";
    App.update(data);
});


socket.on("ask_play", function(data) {
    console.debug("ask_play", data);
    data.event = "ask_play";
    App.update(data);
});


socket.on("bid", function(data) {
    console.debug("bid", data);
    data.event = "bid";
    App.update(data);
});


socket.on("deal", function(data) {
    console.debug("deal", data);
    data.event = "deal";
    App.update(data);
});


socket.on("force_bid", function(data) {
    console.debug("force_bid", data);
    data.event = "force_bid";
    App.update(data);
});


socket.on("init", function(data) {
    console.debug("init", data);
    data.event = "init";
    App.update(data);
});


socket.on("pass", function(data) {
    console.debug("pass", data);
    data.event = "pass";
    App.update(data);
});


socket.on("play", function(data) {
    console.debug("play", data);
    data.event = "play";
    App.update(data);
});


socket.on("score", function(data) {
    console.debug("score", data);
    data.event = "score";
    App.update(data);
});

socket.on("take_trick", function(data) {
    console.debug("take_trick", data);
    data.event = "take_trick";
    App.update(data);
});


socket.on("trick", function(data) {
    console.debug("trick", data);
    data.event = "trick";
    App.update(data);
});
