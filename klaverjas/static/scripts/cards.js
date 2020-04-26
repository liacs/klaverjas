import {Animations} from "./animations.js";


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


class Card {
    constructor($parent, hidden, suit, rank) {
        this.flipped = hidden;
        this.rank = rank;
        this.suit = suit;
        this.x = 0;
        this.y = 0;
        this.angle = 0;
        this.$el = document.createElement("div");

        this.$el.className = "card";
        const $back = document.createElement("div");
        $back.className = "back";
        if (!hidden) {
            const $face = document.createElement("div");
            const $rank = document.createElement("span");
            const $suit = document.createElement("span");

            $face.className = "face suit-" + suit.label;
            $rank.className = "rank";
            $suit.className = "suit";

            $rank.innerHTML = rank.html;
            $suit.innerHTML = suit.html;

            $face.appendChild($rank);
            $face.appendChild($suit);
            this.$el.appendChild($face);
        } else {
            this.$el.style.transform = "rotateY(180deg)";
        }
        this.$el.appendChild($back);
        //this.$el.style.visibility = "hidden";
        $parent.appendChild(this.$el);
    }

    animate_to(delay, duration, x, y, angle) {
        const start_x = this.x;
        const start_y = this.y;
        const start_angle = this.angle;
        const d_x = x - this.x;
        const d_y = y - this.y;
        const d_angle = angle - this.angle;
        const card = this;

        Animations.create(duration,
            function(d_t) {
                card.x = d_x * d_t + start_x;
                card.y = d_y * d_t + start_y;
                card.angle = d_angle * d_t + start_angle;
                card.$el.style.transform = "translate(" + card.x + "px, " + card.y + "px) rotate(" + card.angle + "deg)" + (card.flipped ? " rotateY(180deg)" : "");
            }, {effect: Animations.effects.ease, delay: delay});
    }

    animate_flip(delay, duration) {
        const card = this;
        Animations.create(duration,
            function(d_t) {
                const angle = card.flipped ? 180 - 180 * d_t : 180 * d_t;
                card.$el.style.transform = "translate(" + card.x + "px, " + card.y + "px) rotate(" + card.angle + "deg)" + (card.flipped ? " rotateY(" + rot + "deg)" : "");
            }, {effect: Animations.effects.ease, on_end: function() { card.flipped = !card.flipped; }, delay: delay});
    }
}


export {
    Card,
    RANKS,
    SUITS
}
