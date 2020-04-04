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
});

socket.on("ask_bid", function(data) {
    console.log("ask_bid", data);
    let ans = confirm("play?");
    if (ans) {
        socket.emit("bid", {"game": game, "trump_suit": data["trump_suit"]})
    }
    else {
        socket.emit("bid", {"game": game})
    }
});

socket.on("force_bid", function(data) {
    console.log("force_bid", data);
    let ans = prompt("suit: ");
    socket.emit("bid", {"game": game, "bid": true, "trump_suit": ans})
});