"use strict";


import {Cards, RANKS, SUITS} from "./cards.js";
import {Hands} from "./hands.js";


const $table = document.getElementById("table");


let players = [
    Hands.create(200, -250, 180),
    Hands.create(600, 100, 270),
    Hands.create(-230, 100, 90),
    Hands.create(300, 400, 0)
]

for (let i = 0; i < 8; i++) {
    for (let j = 0; j < 3; j++) {
        const card = Cards.create(true);
        $table.appendChild(card.$el);
        Hands.add(players[j], card, i * 500);
    }
}

