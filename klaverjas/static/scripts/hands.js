import {Card} from "./cards.js";


class Hand {
    constructor(x, y, angle) {
        this.x = x;
        this.y = y;
        this.angle = angle;
        this.cards = [];
    }

    add(card) {
        if (this.cards.length < 8) {
            this.cards.push(card);
        }
    }

    remove(idx) {
        if (this.cards.length > idx) {
            console.log(this.cards.length);
            const card = this.cards[idx];
            this.cards.splice(idx, 1);
            return card;
        }
    }

    animate_fan(delay, duration, arc=30, spread=400) {
        function deg2rad(degrees) {
            return degrees * Math.PI / 180;
        }

        const step = arc / 9;
        const offset = Math.floor((8 - this.cards.length) / 2) + 1;

        for (let i = 0; i < this.cards.length; i++) {
            const angle = step * (i + offset) - arc / 2;
            const x = Math.cos(deg2rad(angle - 90 + this.angle)) * spread + spread + this.x;
            const y = Math.sin(deg2rad(angle - 90 + this.angle)) * spread + spread + this.y;

            this.cards[i].animate_to(delay, duration, x, y, angle + this.angle);
        }
    }
}


export {
    Hand
}
