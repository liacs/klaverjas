"use strict";


import {DOM} from "./DOM.js";
import {Animations} from "./animations.js";


let Cards = {};


const RANKS = {
    SEVEN: {
        html: "7",
        label: "seven",
        value: 0
    },
    EIGHT: {
        html: "8",
        label: "eight",
        value: 1
    },
    NINE: {
        html: "9",
        label: "nine",
        value: 2
    },
    TEN: {
        html: "10",
        label: "ten",
        value: 3
    },
    JACK: {
        html: "J",
        label: "jack",
        value: 4
    },
    QUEEN: {
        html: "Q",
        label: "queen",
        value: 5
    },
    KING: {
        html: "K",
        label: "king",
        value: 6
    },
    ACE: {
        html: "A",
        label: "ace",
        value: 7
    },
};

const SUITS = {
    SPADES: {
        html: "&spades;&#xfe0e;",
        label: "spades",
        value: 0
    },
    HEARTS: {
        html: "&hearts;&#xfe0e;",
        label: "hearts",
        value: 1
    },
    CLUBS: {
        html: "&clubs;&#xfe0e",
        label: "clubs",
        value: 2
    },
    DIAMONDS: {
        html: "&diams&#xfe0e",
        label: "diamonds",
        value: 3
    }
};


(function() {
    Cards.create = function(hidden, suit, rank, flipped) {
        let $el = DOM.create_element("div", "card");
        let $back = DOM.create_element("div", "back");
        if (!hidden) {
            let $face = DOM.create_element("div", "face suit-" + suit.label);
            let $rank = DOM.create_element("span", "rank");
            let $suit = DOM.create_element("span", "suit");

            $rank.innerHTML = rank.html;
            $suit.innerHTML = suit.html;

            $face.appendChild($rank);
            $face.appendChild($suit);
            $el.appendChild($face);
        }

        $el.appendChild($back);

        if (flipped || hidden) {
            $el.style.transform = "rotateY(180deg)";
            flipped = true;
        }

        return {
            suit: suit,
            rank: rank,
            $el: $el,
            flipped: flipped,
            x: 0.0,
            y: 0.0,
            rot: 0.0
        };
    };

    Cards.animate_to = function(card, delay, duration, x, y, rot) {
        const start_x = card.x;
        const start_y = card.y;
        const start_rot = card.rot;

        Animations.create(delay, duration,
            function(dt) {
                const dx = x - start_x;
                const dy = y - start_y;
                const drot = rot - start_rot;

                card.x = dx * dt + start_x;
                card.y = dy * dt + start_y;
                card.rot = drot * dt + start_rot;

                card.$el.style.transform = "translate(" + card.x + "px, " + card.y + "px) rotate(" + card.rot + "deg)" + (card.flipped ? " rotateY(180deg)" : "");
            }, Animations.ease);
    };

    Cards.animate_flip = function(card, delay, duration) {
        Animations.create(delay, duration,
            function(dt) {
                const rot = card.flipped ? 180.0 - 180.0 * dt : 180.0 * dt;

                card.$el.style.transform = "translate(" + card.x + "px, " + card.y + "px) rotate(" + card.rot + "deg)" + (card.flipped ? " rotateY(" + rot + "deg)" : "");
            }, Animations.ease, null, function() { card.flipped = !card.flipped; });
    };
})();


export {
    Cards,
    RANKS,
    SUITS
}
