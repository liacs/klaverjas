"use strict";


let Animations = {};


(function() {
    let animations = [];
    let ticking = false;

    let tick = function() {
        const now = Date.now();

        if (!animations.length) {
            ticking = false;
            return;
        }

        for (let i = 0; i < animations.length; i++) {
            let animation = animations[i];
            if (now < animation.start) {
                continue;
            }

            if (!animation.started) {
                animation.started = true;
                animation.on_start && animation.on_start();
            }

            const delta = Math.min((now - animation.start) / (animation.end - animation.start), 1.0);
            animation.on_progress && animation.on_progress(animation.effect(delta));

            if (now > animation.end) {
                animation.on_end && animation.on_end();
                animations.splice(i--, 1);
            }
        }

        window.requestAnimationFrame(tick);
    };


    Animations.linear = function(t) {
        return t;
    };

    Animations.ease = function(t) {
        return t < 0.5 ? 4.0 * t * t * t : (t - 1.0) * (2.0 * t - 2.0) * (2.0 * t - 2.0) + 1.0;
    };

    Animations.create = function(delay, duration, on_progress, effect, on_start, on_end) {
        const now = Date.now();
        let start = now + delay;

        animations.push({
            start: start,
            end: start + duration,
            effect: effect || Animations.linear,
            on_start: on_start,
            on_progress: on_progress,
            on_end: on_end
        });

        if (!ticking) {
            ticking = true;
            window.requestAnimationFrame(tick);
        }
    };
})();


export {
    Animations
}
