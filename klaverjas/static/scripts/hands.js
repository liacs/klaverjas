"use strict";


import {Cards} from "./cards.js";


let Hands = {};


(function() {
    Hands.create = function(x, y, rot) {
        return {
            x: x,
            y: y,
            rot: rot,
            cards: []
        };
    };

    Hands.add = function(hand, card, delay) {
        if (hand.cards.length < 8) {
            hand.cards.push(card);
            Hands.animate_fan(hand, delay, 500);
        }
    };

    Hands.animate_fan = function(hand, delay, duration, arc=70.0, spread=150.0) {
        function deg2rad(degrees) {
            return degrees * Math.PI / 180.0;
        }

        const step = arc / 9.0;
        const offset = Math.floor((8 - hand.cards.length) / 2) + 1;

        for (let i = 0; i < hand.cards.length; i++) {
            const angle = step * (i + offset) - arc / 2.0;

            let x = Math.cos(deg2rad(angle - 90.0 + hand.rot)) * spread + spread + hand.x;
            let y = Math.sin(deg2rad(angle - 90.0 + hand.rot)) * spread + spread + hand.y;

            Cards.animate_to(hand.cards[i], delay, duration, x, y, angle + hand.rot);
        }
    };
})();


export {
    Hands
}
