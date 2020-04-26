"use strict";


import {Card, RANKS, SUITS} from "./cards.js";
import {Hand} from "./hands.js";


const $table = document.querySelector("#table");


const north = new Hand(-400 - 75 / 2 + 375, -786, 180);
const west = new Hand(-768, -400 + 562.5 / 2 - 75, 90);
const east = new Hand(643, -400 + 562.5 / 2 - 75, 270);
const south = new Hand(-400 - 75 / 2 + 375, 433, 0);

function _next() {
    const card_n = new Card($table, true);
    north.add(card_n);
    const card_w = new Card($table, true);
    west.add(card_w);
    const card_e = new Card($table, true);
    east.add(card_e);
    const card_s = new Card($table, false, SUITS.HEARTS, RANKS.TEN);
    south.add(card_s);

    east.animate_fan(0, 100);
    south.animate_fan(100, 100, 35, 400);
    west.animate_fan(200, 100);
    north.animate_fan(300, 100);
}

for (let i = 0; i < 8; i++) {
    window.setTimeout(_next, i * 400);
}


document.querySelector("#remove").addEventListener("click", function() {
    const card = north.remove(0);
    north.animate_fan(0, 200);
    card.animate_to(0, 200, 0, 0, 0);
});


document.querySelector("#add").addEventListener("click", function() {
    const card = new Card($table, true);
    north.add(card);
    north.animate_fan(0, 200);
});
