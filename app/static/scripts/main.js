"use strict";

const socket = io(location.protocol + "//" +
                  document.domain + ":" +
                  location.port);

socket.on("connect", function() {
    console.log("connect", socket.id);
    socket.emit("join", {"room": game});
});

socket.on("disconnect", function() {
    console.log("disconnect");
});

socket.on("log", function(data) {
    console.log("log", data);
});